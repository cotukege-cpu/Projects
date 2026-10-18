
import tkinter as tk
from tkinter import font


class HesapMakinesi:
    def __init__(self, pencere):
        self.pencere = pencere
        self.pencere.title("Hesap Makinesi")
        self.pencere.geometry("600x600")
        self.pencere.configure(bg="#1c1c1e")

        # Durum deiskenler
        self.mevcut_deger = "0"
        self.onceki_deger = ""
        self.islem = None
        self.yeni_sayi_bekleniyor = False

        # Fontlar
        self.ekran_font = font.Font(family="Helvetica", size=32, weight="normal")
        self.buton_font = font.Font(family="Helvetica", size=18, weight="normal")

        self._ekrani_olustur()
        self._butonlari_olustur()
        self._klavye_baglantilarini_kur()

    # ------------------------------------------------------------------
    # Interface
    # ------------------------------------------------------------------
    def _ekrani_olustur(self):
        cerceve = tk.Frame(self.pencere, bg="#1c1c1e")
        cerceve.pack(fill="both", expand=True)

        self.ekran_etiketi = tk.Label(
            cerceve,
            text=self.mevcut_deger,
            anchor="e",
            bg="#1c1c1e",
            fg="white",
            font=self.ekran_font,
            padx=20,
            pady=30,
        )
        self.ekran_etiketi.pack(fill="both", expand=True)

    def _buton_yap(self, cerceve, metin, satir, sutun, colspan=1, bg="#333333", fg="white", komut=None):
        buton = tk.Button(
            cerceve,
            text=metin,
            font=self.buton_font,
            bg=bg,
            fg=fg,
            activebackground="#555555",
            activeforeground="white",
            bd=0,
            relief="flat",
            command=komut if komut else lambda m=metin: self._buton_tiklandi(m),
        )
        buton.grid(
            row=satir,
            column=sutun,
            columnspan=colspan,
            sticky="nsew",
            padx=3,
            pady=3,
            ipady=18,
        )
        return buton

    def _butonlari_olustur(self):
        cerceve = tk.Frame(self.pencere, bg="#1c1c1e")
        cerceve.pack(fill="both", expand=True)

        for i in range(4):
            cerceve.grid_columnconfigure(i, weight=1)
        for i in range(5):
            cerceve.grid_rowconfigure(i, weight=1)

        turuncu = "#ff9500"
        gri = "#a5a5a5"
        koyu_gri = "#333333"

        # C, +/-, %, /
        self._buton_yap(cerceve, "C", 0, 0, bg=gri, fg="black", komut=self._temizle)
        self._buton_yap(cerceve, "+/-", 0, 1, bg=gri, fg="black", komut=self._isaret_degistir)
        self._buton_yap(cerceve, "%", 0, 2, bg=gri, fg="black", komut=self._yuzde)
        self._buton_yap(cerceve, "÷", 0, 3, bg=turuncu, komut=lambda: self._islem_sec("/"))

        # 7 8 9 *
        self._buton_yap(cerceve, "7", 1, 0, bg=koyu_gri)
        self._buton_yap(cerceve, "8", 1, 1, bg=koyu_gri)
        self._buton_yap(cerceve, "9", 1, 2, bg=koyu_gri)
        self._buton_yap(cerceve, "×", 1, 3, bg=turuncu, komut=lambda: self._islem_sec("*"))

        # 4 5 6 -
        self._buton_yap(cerceve, "4", 2, 0, bg=koyu_gri)
        self._buton_yap(cerceve, "5", 2, 1, bg=koyu_gri)
        self._buton_yap(cerceve, "6", 2, 2, bg=koyu_gri)
        self._buton_yap(cerceve, "−", 2, 3, bg=turuncu, komut=lambda: self._islem_sec("-"))

        # 1 2 3 +
        self._buton_yap(cerceve, "1", 3, 0, bg=koyu_gri)
        self._buton_yap(cerceve, "2", 3, 1, bg=koyu_gri)
        self._buton_yap(cerceve, "3", 3, 2, bg=koyu_gri)
        self._buton_yap(cerceve, "+", 3, 3, bg=turuncu, komut=lambda: self._islem_sec("+"))

        # 0 , =
        self._buton_yap(cerceve, "0", 4, 0, colspan=2, bg=koyu_gri)
        self._buton_yap(cerceve, ",", 4, 2, bg=koyu_gri, komut=self._ondalik_ekle)
        self._buton_yap(cerceve, "=", 4, 3, bg=turuncu, komut=self._esittir)

    # ------------------------------------------------------------------
    # Klavye 
    # ------------------------------------------------------------------
    def _klavye_baglantilarini_kur(self):
        self.pencere.bind("<Key>", self._tus_basildi)

    def _tus_basildi(self, event):
        tus = event.char
        if tus.isdigit():
            self._buton_tiklandi(tus)
        elif tus == "+":
            self._islem_sec("+")
        elif tus == "-":
            self._islem_sec("-")
        elif tus == "*":
            self._islem_sec("*")
        elif tus == "/":
            self._islem_sec("/")
        elif tus in (".", ","):
            self._ondalik_ekle()
        elif event.keysym == "Return" or tus == "=":
            self._esittir()
        elif event.keysym == "BackSpace":
            self._geri_al()
        elif event.keysym == "Escape":
            self._temizle()

    # ------------------------------------------------------------------
    # Hesap makinesi logic
    # ------------------------------------------------------------------
    def _ekrani_guncelle(self):
        # Make long numbers shorter to fit the screen
        metin = self.mevcut_deger
        if len(metin) > 12:
            try:
                metin = f"{float(metin):.6g}"
            except ValueError:
                pass
        self.ekran_etiketi.config(text=metin)

    def _buton_tiklandi(self, rakam):
        if self.yeni_sayi_bekleniyor:
            self.mevcut_deger = rakam
            self.yeni_sayi_bekleniyor = False
        else:
            if self.mevcut_deger == "0":
                self.mevcut_deger = rakam
            else:
                self.mevcut_deger += rakam
        self._ekrani_guncelle()

    def _ondalik_ekle(self):
        if self.yeni_sayi_bekleniyor:
            self.mevcut_deger = "0."
            self.yeni_sayi_bekleniyor = False
        elif "." not in self.mevcut_deger:
            self.mevcut_deger += "."
        self._ekrani_guncelle()

    def _temizle(self):
        self.mevcut_deger = "0"
        self.onceki_deger = ""
        self.islem = None
        self.yeni_sayi_bekleniyor = False
        self._ekrani_guncelle()

    def _geri_al(self):
        if len(self.mevcut_deger) > 1:
            self.mevcut_deger = self.mevcut_deger[:-1]
        else:
            self.mevcut_deger = "0"
        self._ekrani_guncelle()

    def _isaret_degistir(self):
        try:
            deger = float(self.mevcut_deger)
            deger = -deger
            self.mevcut_deger = self._sayi_formatla(deger)
        except ValueError:
            pass
        self._ekrani_guncelle()

    def _yuzde(self):
        try:
            deger = float(self.mevcut_deger) / 100
            self.mevcut_deger = self._sayi_formatla(deger)
        except ValueError:
            pass
        self._ekrani_guncelle()

    def _islem_sec(self, yeni_islem):
        if self.islem is not None and not self.yeni_sayi_bekleniyor:
            self._esittir()
        self.onceki_deger = self.mevcut_deger
        self.islem = yeni_islem
        self.yeni_sayi_bekleniyor = True

    def _esittir(self):
        if self.islem is None or self.onceki_deger == "":
            return
        try:
            a = float(self.onceki_deger)
            b = float(self.mevcut_deger)

            if self.islem == "+":
                sonuc = a + b
            elif self.islem == "-":
                sonuc = a - b
            elif self.islem == "*":
                sonuc = a * b
            elif self.islem == "/":
                if b == 0:
                    self.mevcut_deger = "Error: Cant be divided to 0"
                    self._ekrani_guncelle()
                    self.islem = None
                    self.onceki_deger = ""
                    self.yeni_sayi_bekleniyor = True
                    return
                sonuc = a / b
            else:
                return

            self.mevcut_deger = self._sayi_formatla(sonuc)
        except ValueError:
            self.mevcut_deger = "Hata"

        self.islem = None
        self.onceki_deger = ""
        self.yeni_sayi_bekleniyor = True
        self._ekrani_guncelle()

    @staticmethod
    def _sayi_formatla(deger):
        # Tam sayıysa nokta olmadan göster, değilse ondalık göster
        if deger == int(deger) and abs(deger) < 1e15:
            return str(int(deger))
        return str(round(deger, 10))


def main():
    pencere = tk.Tk()
    HesapMakinesi(pencere)
    pencere.mainloop()


if __name__ == "__main__":
    main()