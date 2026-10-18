

import ctypes
import difflib
import json
import os
import re
import subprocess
import sys
import tempfile
import webbrowser

import psutil

# ---------------------------------------------------------------- settings

if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(BASE_DIR, "model")
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")

KEYWORD = "johnson"             # the word that activates a command
AWAKE_WINDOW_SECONDS = 5        # time to give a command after saying only "Johnson"
PTT_TIMEOUT_SECONDS = 8         # how long the Push-to-talk button listens
MATCH_THRESHOLD = 0.6           # 0-1: how close a spoken name must be (opening)
CLOSE_MATCH_THRESHOLD = 0.75    # stricter on purpose: avoids closing the wrong app

OPEN_WORDS = {"open", "launch", "start", "run"}
CLOSE_APP_WORDS = {"close", "quit", "exit"}            # "close spotify"
DEACTIVATE_WORDS = {"close", "quit", "exit", "stop", "deactivate"}   # alone = voice off
KILL_WORDS = {"kill"}                                   # "kill spotify" = force
FILLER_WORDS = {"please", "up", "the", "my"}
TRAILING_FILLER = {"app", "application", "please"}

# Files of these types are never launched by voice, even if they are on your
# Desktop (a misheard word must not be able to run a script or installer).
BLOCKED_EXTENSIONS = {
    ".bat", ".cmd", ".ps1", ".vbs", ".vbe", ".js", ".jse", ".wsf", ".wsh",
    ".msi", ".reg", ".scr", ".hta", ".cpl", ".jar",
}
SKIP_NAMES = {"desktop.ini", "thumbs.db"}

# Windows programs Johnson will never close or kill, whatever you say.
PROTECTED_NAMES = {
    "explorer.exe", "winlogon.exe", "csrss.exe", "svchost.exe", "system",
    "lsass.exe", "dwm.exe", "services.exe", "smss.exe", "wininit.exe",
    "taskmgr.exe", "searchhost.exe", "startmenuexperiencehost.exe",
    "shellexperiencehost.exe", "textinputhost.exe", "applicationframehost.exe",
    "sihost.exe", "fontdrvhost.exe", "ctfmon.exe", "python.exe", "pythonw.exe",
}

DEFAULT_CONFIG = {
    "extra_scan_folders": [],
    "include_start_menu": False,
    "web_shortcuts": {"instagram": "https://www.instagram.com"},
}


# ---------------------------------------------------------------- config

def load_config():
    cfg = json.loads(json.dumps(DEFAULT_CONFIG))     # deep copy
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                user_cfg = json.load(f)
            for key in DEFAULT_CONFIG:
                if key in user_cfg:
                    cfg[key] = user_cfg[key]
        except (OSError, json.JSONDecodeError):
            pass
    return cfg


# ---------------------------------------------------------------- scanning

def normalize(name):
    name = name.lower()
    name = re.sub(r"[^a-z0-9 ]+", " ", name)
    return re.sub(r"\s+", " ", name).strip()


def scan_folders(cfg):
    """Return (top_level_folders, recursive_folders)."""
    env = os.environ
    home = os.path.expanduser("~")

    top_level = [os.path.join(home, "Desktop")]
    if env.get("OneDrive"):
        top_level.append(os.path.join(env["OneDrive"], "Desktop"))
    if env.get("PUBLIC"):
        top_level.append(os.path.join(env["PUBLIC"], "Desktop"))
    if env.get("APPDATA"):
        # Where Windows keeps shortcuts for apps pinned to the taskbar.
        top_level.append(os.path.join(
            env["APPDATA"], "Microsoft", "Internet Explorer",
            "Quick Launch", "User Pinned", "TaskBar"))
    for extra in cfg.get("extra_scan_folders", []):
        top_level.append(os.path.expandvars(extra))

    recursive = []
    if cfg.get("include_start_menu"):
        for base in (env.get("APPDATA"), env.get("PROGRAMDATA")):
            if base:
                recursive.append(os.path.join(
                    base, "Microsoft", "Windows", "Start Menu", "Programs"))
    return top_level, recursive


def add_item(index, path):
    base = os.path.basename(path)
    if not base or base.startswith(".") or base.lower() in SKIP_NAMES:
        return
    if os.path.isdir(path):
        stem, ext = base, ""
    else:
        stem, ext = os.path.splitext(base)
    if ext.lower() in BLOCKED_EXTENSIONS:
        return
    if "uninstall" in stem.lower():
        return
    key = normalize(stem)
    if key and key not in index:          # first match wins (user Desktop first)
        index[key] = (stem, path)


def build_index(cfg):
    """Map normalized spoken name -> (display name, full path)."""
    index = {}
    top_level, recursive = scan_folders(cfg)

    for folder in top_level:
        if not os.path.isdir(folder):
            continue
        try:
            entries = sorted(os.listdir(folder))
        except OSError:
            continue
        for name in entries:
            add_item(index, os.path.join(folder, name))

    for folder in recursive:
        if not os.path.isdir(folder):
            continue
        for root, _dirs, files in os.walk(folder):
            for name in sorted(files):
                add_item(index, os.path.join(root, name))
    return index


def all_candidates(index, web_shortcuts):
    candidates = {key: ("path", disp, path) for key, (disp, path) in index.items()}
    for name, url in web_shortcuts.items():
        key = normalize(name)
        if key:
            candidates.setdefault(key, ("web", name, url))
    return candidates


def list_openable(cfg):
    """Names shown in the app's 'can open' list."""
    index = build_index(cfg)
    names = [disp for disp, _path in index.values()]
    names += [f"{n} (website)" for n in cfg.get("web_shortcuts", {})]
    return sorted(names, key=str.lower)


# ---------------------------------------------------------------- matching

def score_name(target, key):
    t_compact = target.replace(" ", "")
    k_compact = key.replace(" ", "")
    score = max(
        difflib.SequenceMatcher(None, target, key).ratio(),
        difflib.SequenceMatcher(None, t_compact, k_compact).ratio(),
    )
    # "opera" inside "opera gx" counts as a strong match, but only when the
    # shorter text is a real chunk of the longer one (so one stray letter or a
    # tiny fragment can never match, which matters most when closing apps).
    short, long_ = sorted((t_compact, k_compact), key=len)
    if len(short) >= 3 and short in long_ and len(short) / len(long_) >= 0.5:
        score = max(score, 0.85)
    return score


def find_best(target, candidates):
    target_n = normalize(target)
    if not target_n:
        return None
    best, best_score = None, 0.0
    for key, item in candidates.items():
        s = score_name(target_n, key)
        if s > best_score:
            best, best_score = item, s
    if best is not None and best_score >= MATCH_THRESHOLD:
        return best
    return None


def suggestions(target, candidates, n=3):
    keys = difflib.get_close_matches(normalize(target), list(candidates), n=n, cutoff=0.3)
    return [candidates[k][1] for k in keys]


# ---------------------------------------------------------------- understanding speech

def find_keyword(words):
    for i, w in enumerate(words):
        if w == KEYWORD or difflib.SequenceMatcher(None, w, KEYWORD).ratio() >= 0.8:
            return i
    return None


def _strip_filler(words):
    words = list(words)
    while words and words[0] in FILLER_WORDS:
        words = words[1:]
    while words and words[-1] in TRAILING_FILLER:
        words = words[:-1]
    return words


def parse(rest):
    """rest = words spoken after the keyword.
    Returns (action, argument). Actions:
      wake        - only the keyword was said
      deactivate  - turn voice activation off   ("close", "stop listening")
      open        - open <argument>
      close       - politely close <argument>   ("close spotify")
      kill        - force-close <argument>      ("kill spotify", "force close spotify")
    """
    rest = _strip_filler(rest)
    if not rest:
        return "wake", None
    first = rest[0]

    if first == "deactivate" or (first == "stop" and rest[1:2] == ["listening"]):
        return "deactivate", None
    if first in DEACTIVATE_WORDS and len(rest) == 1:
        return "deactivate", None

    if first == "force" and len(rest) > 1 and rest[1] in CLOSE_APP_WORDS:
        rest = ["kill"] + rest[2:]
        first = "kill"

    if first in KILL_WORDS:
        target = _strip_filler(rest[1:])
        return ("kill", " ".join(target)) if target else ("wake", None)

    if first in CLOSE_APP_WORDS:
        target = _strip_filler(rest[1:])
        return ("close", " ".join(target)) if target else ("wake", None)

    if first in OPEN_WORDS:
        rest = _strip_filler(rest[1:])
        if not rest:
            return "wake", None
    return "open", " ".join(rest)


# ---------------------------------------------------------------- opening

def launch(kind, display, target):
    """Returns (ok, error_message)."""
    try:
        if kind == "web":
            if not target.lower().startswith(("http://", "https://")):
                return False, f"Refusing to open a non-web link for '{display}'."
            webbrowser.open(target)
        else:
            os.startfile(target)          # same as double-clicking it
        return True, ""
    except OSError as e:
        return False, f"Could not open '{display}': {e}"


def open_item(spoken, cfg):
    """Returns (ok, message)."""
    index = build_index(cfg)
    candidates = all_candidates(index, cfg.get("web_shortcuts", {}))
    match = find_best(spoken, candidates)
    if match is None:
        msg = f"I couldn't find '{spoken}' on your Desktop or Taskbar."
        close = suggestions(spoken, candidates)
        if close:
            msg += " Did you mean: " + ", ".join(close) + "?"
        return False, msg
    kind, display, target = match
    ok, err = launch(kind, display, target)
    return ok, (f"Opening {display}..." if ok else err)


# ---------------------------------------------------------------- Windows window/process helpers

_user32 = None
_dwmapi = None
_ENUM_PROC = None
WM_CLOSE = 0x0010
GW_OWNER = 4
GWL_EXSTYLE = -20
WS_EX_TOOLWINDOW = 0x00000080
DWMWA_CLOAKED = 14


def _init_winapi():
    global _user32, _dwmapi, _ENUM_PROC
    if _user32 is not None:
        return
    from ctypes import wintypes
    u = ctypes.windll.user32
    _ENUM_PROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    u.EnumWindows.argtypes = [_ENUM_PROC, wintypes.LPARAM]
    u.EnumWindows.restype = wintypes.BOOL
    u.IsWindowVisible.argtypes = [wintypes.HWND]
    u.IsWindowVisible.restype = wintypes.BOOL
    u.GetWindow.argtypes = [wintypes.HWND, wintypes.UINT]
    u.GetWindow.restype = wintypes.HWND
    u.GetWindowLongW.argtypes = [wintypes.HWND, ctypes.c_int]
    u.GetWindowLongW.restype = ctypes.c_long
    u.GetWindowTextLengthW.argtypes = [wintypes.HWND]
    u.GetWindowTextLengthW.restype = ctypes.c_int
    u.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
    u.GetWindowTextW.restype = ctypes.c_int
    u.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
    u.GetWindowThreadProcessId.restype = wintypes.DWORD
    u.PostMessageW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
    u.PostMessageW.restype = wintypes.BOOL
    d = ctypes.windll.dwmapi
    d.DwmGetWindowAttribute.argtypes = [wintypes.HWND, wintypes.DWORD, ctypes.c_void_p, wintypes.DWORD]
    d.DwmGetWindowAttribute.restype = ctypes.c_long
    _user32, _dwmapi = u, d


def _taskbar_windows():
    """[(hwnd, pid)] for windows that show up as buttons on the taskbar."""
    from ctypes import wintypes
    _init_winapi()
    found = []

    def callback(hwnd, _lparam):
        if not _user32.IsWindowVisible(hwnd):
            return True
        if _user32.GetWindow(hwnd, GW_OWNER):
            return True
        if _user32.GetWindowLongW(hwnd, GWL_EXSTYLE) & WS_EX_TOOLWINDOW:
            return True
        cloaked = wintypes.DWORD(0)
        _dwmapi.DwmGetWindowAttribute(hwnd, DWMWA_CLOAKED, ctypes.byref(cloaked),
                                      ctypes.sizeof(cloaked))
        if cloaked.value:
            return True
        if _user32.GetWindowTextLengthW(hwnd) == 0:
            return True
        pid = wintypes.DWORD()
        _user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        found.append((hwnd, pid.value))
        return True

    _user32.EnumWindows(_ENUM_PROC(callback), 0)
    return found


def post_close(hwnd):
    """Politely ask a window to close (same as clicking its X)."""
    _init_winapi()
    return bool(_user32.PostMessageW(hwnd, WM_CLOSE, 0, 0))


def _system_root():
    root = os.environ.get("SystemRoot") or os.environ.get("WINDIR") or ""
    return os.path.normcase(os.path.abspath(root)) if root else ""


def list_running_apps(include_background=False):
    """Running programs, grouped by .exe:
    [{"exe": path, "name": "Spotify", "pids": {..}, "hwnds": [..]}]
    Normally only programs with a taskbar window. include_background=True
    also lists windowless ones (tray apps), used for force-close."""
    if os.name != "nt":
        return []
    apps = {}
    me = os.getpid()

    def add(pid, hwnd=None):
        if pid == me:
            return
        try:
            exe = psutil.Process(pid).exe()
        except (psutil.Error, OSError):
            return
        if not exe or os.path.basename(exe).lower() in PROTECTED_NAMES:
            return
        key = os.path.normcase(exe)
        app = apps.setdefault(key, {
            "exe": exe,
            "name": os.path.splitext(os.path.basename(exe))[0],
            "pids": set(), "hwnds": [],
        })
        app["pids"].add(pid)
        if hwnd is not None:
            app["hwnds"].append(hwnd)

    for hwnd, pid in _taskbar_windows():
        add(pid, hwnd)

    if include_background:
        root = _system_root()
        for p in psutil.process_iter(["pid", "exe"]):
            exe = p.info.get("exe") or ""
            if not exe:
                continue
            if root and os.path.normcase(exe).startswith(root + os.sep):
                continue
            add(p.info["pid"])
    return list(apps.values())


def _unsafe_dirs():
    env = os.environ
    names = ["ProgramFiles", "ProgramFiles(x86)", "ProgramW6432", "SystemRoot",
             "WINDIR", "USERPROFILE", "APPDATA", "LOCALAPPDATA", "PUBLIC", "ProgramData"]
    dirs = set()
    for n in names:
        v = env.get(n)
        if v:
            dirs.add(os.path.normcase(os.path.abspath(v)))
    if env.get("LOCALAPPDATA"):
        dirs.add(os.path.normcase(os.path.abspath(
            os.path.join(env["LOCALAPPDATA"], "Programs"))))
    home = os.path.expanduser("~")
    for sub in ("", "Desktop", "Downloads", "Documents"):
        dirs.add(os.path.normcase(os.path.abspath(os.path.join(home, sub))))
    return dirs


def _dir_is_safe_for_prefix(d):
    """A program's whole install folder may be matched only if that folder is
    really the app's own (e.g. ...\\Steam), not a shared place like System32."""
    if os.path.dirname(d) == d:           # drive root
        return False
    if d in _unsafe_dirs():
        return False
    root = _system_root()
    if root and (d == root or d.startswith(root + os.sep)):
        return False
    return True


EXCLUDE_SUBPATHS = (os.sep + "steamapps" + os.sep,)     # don't treat running games as "Steam"


def exe_matches(proc_exe, target_exe):
    """Is proc_exe the target program (or part of the same app, in its install folder)?"""
    if not proc_exe or not target_exe:
        return False
    pe = os.path.normcase(os.path.abspath(proc_exe))
    te = os.path.normcase(os.path.abspath(target_exe))
    if pe == te:
        return True
    tdir = os.path.dirname(te)
    if _dir_is_safe_for_prefix(tdir):
        if pe.startswith(tdir + os.sep) and not any(x in pe for x in EXCLUDE_SUBPATHS):
            return True
    return False


# ---------------------------------------------------------------- shortcut targets

_LNK_CACHE = {}     # path -> (mtime, target)

_RESOLVE_PS = (
    "$ErrorActionPreference='SilentlyContinue';"
    "[Console]::OutputEncoding=[Text.Encoding]::UTF8;"
    "$sh=New-Object -ComObject WScript.Shell;"
    "Get-Content -LiteralPath $env:J_LIST -Encoding UTF8 | ForEach-Object {"
    " if($_){ $t=$sh.CreateShortcut($_).TargetPath; Write-Output ($_ + '|' + $t) } }"
)


def resolve_shortcuts(paths):
    """{.lnk path: the program it points to ('' if unknown)} using Windows' own
    shortcut reader through PowerShell. Results are cached."""
    result, todo = {}, []
    for p in paths:
        try:
            m = os.path.getmtime(p)
        except OSError:
            continue
        cached = _LNK_CACHE.get(p)
        if cached and cached[0] == m:
            result[p] = cached[1]
        else:
            todo.append((p, m))
    if not todo:
        return result

    tmp = tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8")
    try:
        tmp.write("\n".join(p for p, _ in todo))
        tmp.close()
        env = dict(os.environ, J_LIST=tmp.name)
        proc = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", _RESOLVE_PS],
            capture_output=True, text=True, encoding="utf-8", env=env, timeout=25,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        found = {}
        for line in proc.stdout.splitlines():
            if "|" in line:
                path, target = line.rsplit("|", 1)
                found[path.strip()] = target.strip()
        for p, m in todo:
            target = found.get(p, "")
            _LNK_CACHE[p] = (m, target)
            result[p] = target
    except (OSError, subprocess.SubprocessError):
        pass
    finally:
        try:
            os.remove(tmp.name)
        except OSError:
            pass
    return result


# ---------------------------------------------------------------- closing

def find_close_target(spoken, index, include_background=False):
    """Work out which running app is meant. Returns a dict or None."""
    target_n = normalize(spoken)
    if not target_n:
        return None
    running = list_running_apps(include_background)
    if not running:
        return None

    # Route 1: spoken name -> a shortcut of that name -> the program it starts
    cands = []
    for key, (disp, path) in index.items():
        ext = os.path.splitext(path)[1].lower()
        if ext not in (".lnk", ".exe"):
            continue
        s = score_name(target_n, key)
        if s >= CLOSE_MATCH_THRESHOLD:
            cands.append((s, disp, path, ext))
    cands.sort(reverse=True)
    cands = cands[:3]
    if cands:
        lnks = [p for _s, _d, p, e in cands if e == ".lnk"]
        resolved = resolve_shortcuts(lnks) if lnks else {}
        for _s, disp, path, ext in cands:
            exe = path if ext == ".exe" else resolved.get(path, "")
            if not exe:
                continue
            matched = [a for a in running if exe_matches(a["exe"], exe)]
            if matched:
                return {"display": disp, "apps": matched,
                        "exes": {exe} | {a["exe"] for a in matched}}

    # Route 2: spoken name -> the running program's own name
    best, best_score = None, 0.0
    for a in running:
        s = score_name(target_n, normalize(a["name"]))
        if s > best_score:
            best, best_score = a, s
    if best is not None and best_score >= CLOSE_MATCH_THRESHOLD:
        return {"display": best["name"], "apps": [best], "exes": {best["exe"]}}
    return None


def force_kill(exes):
    """Hard-stop every process that belongs to the given programs. Returns pids."""
    killed, me = [], os.getpid()
    for p in psutil.process_iter(["pid", "name", "exe"]):
        try:
            info = p.info
            if info["pid"] == me:
                continue
            if (info["name"] or "").lower() in PROTECTED_NAMES:
                continue
            exe = info["exe"]
            if exe and any(exe_matches(exe, t) for t in exes):
                p.kill()
                killed.append(info["pid"])
        except (psutil.Error, OSError):
            continue
    return killed


def still_running(pids):
    return [pid for pid in pids if psutil.pid_exists(pid)]


def _running_hint():
    names = sorted({a["name"] for a in list_running_apps()}, key=str.lower)
    if not names:
        return ""
    shown = ", ".join(names[:10]) + ("..." if len(names) > 10 else "")
    return f" Apps I can see running: {shown}."


def close_app(spoken, cfg, force=False):
    """Returns {"ok": bool, "message": str, "pids": [...], "display": str}."""
    index = build_index(cfg)
    found = find_close_target(spoken, index, include_background=force)

    if not found:
        if not force:
            bg = find_close_target(spoken, index, include_background=True)
            if bg:
                return {"ok": False, "pids": [], "display": bg["display"],
                        "message": (f"{bg['display']} is running in the background with no "
                                    f"window to close. Say \"Johnson, kill {spoken}\" to "
                                    "force it to quit.")}
        return {"ok": False, "pids": [], "display": spoken,
                "message": f"I couldn't find a running app called '{spoken}'." + _running_hint()}

    display = found["display"]
    if force:
        killed = force_kill(found["exes"])
        if not killed:
            return {"ok": False, "pids": [], "display": display,
                    "message": f"I couldn't force-close {display} (it may need admin rights)."}
        return {"ok": True, "pids": [], "display": display,
                "message": f"Force-closed {display} ({len(killed)} process(es))."}

    sent = sum(1 for a in found["apps"] for h in a["hwnds"] if post_close(h))
    pids = sorted({pid for a in found["apps"] for pid in a["pids"]})
    if not sent:
        return {"ok": False, "pids": [], "display": display,
                "message": f"I couldn't send a close request to {display} "
                           "(it may be running as administrator)."}
    return {"ok": True, "pids": pids, "display": display,
            "message": f"Asking {display} to close ({sent} window(s))..."}