import os
import requests
import pandas as pd
import time
import mysql.connector
from pathlib import Path
from dotenv import load_dotenv
import tkinter as tk
from tkinter import messagebox , scrolledtext , ttk
from datetime import datetime
from zoneinfo import ZoneInfo





#env path guarantee
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)


#--------------SECURITY CONFIGURATION--------------

API_KEY = os.getenv("API_KEY")
DB_PASSWORD = os.getenv("DB_PASSWORD")





FOOTBALL_URL_matches = "https://api.football-data.org/v4/competitions/PL/matches"

FOOTBALL_URL_scorers = "https://api.football-data.org/v4/competitions/PL/scorers"

FOOTBALL_URL_standings = "https://api.football-data.org/v4/competitions/PL/standings"

headers = { "X-Auth-Token": API_KEY }


def safe_val(val):
    if pd.isna(val) or val is None:
        return None
    if hasattr(val,"item"):
        return val.item()      
    return val






#-----UK CLOCK---------

def update_uk_clock(clock_label):
    try:
        uk_time=datetime.now(ZoneInfo("Europe/London"))
        time_string= uk_time.strftime("%H:%M:%S - %d %B %Y")
        clock_label.config(text = f"UK TIME: {time_string}")
    except Exception:
        pass
    clock_label.after(1000,lambda: update_uk_clock(clock_label))






#------DATABASE GENERATOR AUTOMATED----- (generates the database tables for anybody)
def initialize_database(cursor):
    #teams
    cursor.execute("""CREATE TABLE IF NOT EXISTS teams (team_id INT PRIMARY KEY,team_name VARCHAR(100));""")

    #matches
    cursor.execute("""CREATE TABLE IF NOT EXISTS matches(match_id INT PRIMARY KEY,match_date DATETIME,home_team_id INT ,away_team_id INT,home_team_score INT, away_team_score INT,match_status VARCHAR(50),odds FLOAT);""")

    #scorers
    cursor.execute("""CREATE TABLE IF NOT EXISTS scorers(player_id INT PRIMARY KEY,player_name VARCHAR(50),team_id INT,matches_played INT,goals INT);""")

    #standings
    cursor.execute("""CREATE TABLE IF NOT EXISTS standings(team_position INT,team_id INT,matches_played INT,points INT,goal_difference INT,goals_against VARCHAR(100),PRIMARY KEY(team_position),CONSTRAINT fk_standings_team_id FOREIGN KEY(team_id) REFERENCES teams(team_id));""")





def Football_matchday_pipeline(log_widget, tree_widget):
    
    
    def log_message(message):
        log_widget.insert(tk.END, message + "\n")
        log_widget.see(tk.END)
        root.update_idletasks()

    log_message(f"\n-- Premier League Pipeline starting ({time.strftime("%Y-%m-%d  %H:%M:%S ")})----")


    try:
        
        #-----------------REQUESTING API DATA AND TURNING IT INTO A DICTIONARY----------------------#
        #Requesting Matches (and automatically teams) data from the API

        
        response_matches = requests.get(FOOTBALL_URL_matches, headers=headers)


        if response_matches.status_code == 200:

            data_matches = response_matches.json() #gets json data to a dictionary
            log_message("Matches Data retrieved successfully")
        else:
            data_matches = {"matches": []}
            log_message(f"Error, An error occured while retrieving MATCHES DATA! status code: {response_matches.status_code}")






        #---------Requesting Scorers data from the API-----------


        response_scorers = requests.get(FOOTBALL_URL_scorers, headers=headers)

        if response_scorers.status_code == 200:

            data_scorers = response_scorers.json() #gets json data to a dictionary
            log_message("Scorers Data retrieved successfully")

        else:
            data_scorers = {"scorers": []}
            log_message(f"Error, An error occured while retrieving SCORERS DATA! status code: {response_scorers.status_code}")



        

        #--------Requesting Standing data from the API------------

        response_standings = requests.get(FOOTBALL_URL_standings, headers = headers)

        if response_standings.status_code == 200:
            

            data_standings = response_standings.json()
            log_message("Standings Data retrieved successfully")
        else:
            data_standings= {"standings":[]}
            log_message(f"Error, An error occured while retrieving STANDINGS DATA! status code: {response_standings.status_code}")

        







        #----------------------DATA CLEANING AND TRANSFORMATION WIH PANDAS--------------------------#



        #FOR MATCHES TABLE
        #MATCHES (match_id, home_team, away_team, match_date, match_status, home_score, away_score,odds)

        raw_matches = data_matches.get("matches", [])

        cleaned_data_matches = []


        for match in raw_matches:
            match_id = match.get("id")
            home_team_id = match.get("homeTeam", {}).get("id")  # when you use [] ---> keyError 
            away_team_id = match.get("awayTeam", {}).get("id")
            
            raw_date = match.get("utcDate")
            match_date = None                     # replacing T with space and remove Z to make it compatible with the MySQL time system
            if raw_date:                                                # (2026-08-21T19:00:00Z) ---> (2026-08-21 19:00:00) 
                match_date=raw_date.replace("T"," ").replace("Z","")
            

            score_info = match.get("score", {}).get("fullTime",{})
            home_team_score = score_info.get("home")
            away_team_score = score_info.get("away")
            match_status = match.get("status")

            odds_dict = match.get("odds")
            odds = odds_dict.get("homeWin") if odds_dict else None

            cleaned_data_matches.append({"match_id":match_id,
                            "home_team_id":home_team_id,
                            "away_team_id":away_team_id,
                            "match_date":match_date,
                            "match_status":match_status,
                            "home_team_score":home_team_score,
                            "away_team_score":away_team_score,
                            "odds":odds,
                            })


        df_matches = pd.DataFrame(cleaned_data_matches)

        

        




        #FOR TEAMS TABLE
        #TEAMS (team_id, team_name)


        teams_dict = {}
        for match in raw_matches:
            home = match.get("homeTeam", {})
            if home and home.get("id"):
                teams_dict[home.get("id")] = home.get("name")
                
            away = match.get("awayTeam", {})
            if away and away.get("id"):
                teams_dict[away.get("id")] = away.get("name")

        cleaned_data_teams = [{"team_id": t_id, "team_name": t_name} for t_id, t_name in teams_dict.items()]
        df_teams = pd.DataFrame(cleaned_data_teams)
       





        #FOR SCORERS TABLE
        #SCORERS (player_id, player_name, team_id,matches_played,goals)

        raw_scorers = data_scorers.get("scorers" ,[])

        cleaned_data_scorers = []



        for scorer in raw_scorers:
            player_id = scorer.get("id",{}).get("id")
                      
            team_id = scorer.get("team", {}).get("id")
            if not player_id or not team_id:
                continue
            
            player_name = scorer.get("player", {}).get("name")  

            matches_played = scorer.get("playedMatches")
            goals = scorer.get("goals")


            cleaned_data_scorers.append({"player_id":player_id,
                            "player_name":player_name,
                            "team_id":team_id,
                            "matches_played":matches_played,
                            "goals":goals,
                            })


        df_scorers = pd.DataFrame(cleaned_data_scorers)



      


        #FOR STANDINGS TABLE
        #STANDINGS (team_position, team_id, matches_played, points, goals_for_against, goal_difference)

        raw_standings = data_standings.get("standings",[])
        table_data = []
        

        for standing in raw_standings:
            if standing.get("type") == "TOTAL":
                table_data = standing.get("table", [])
                break


        cleaned_data_standings = []
        
        for row in table_data:
            team_position = row.get("position")
            team_id = row.get("team", {}).get("id")
            if not team_id:
                continue

            matches_played = row.get("playedGames")
            points = row.get("points")
            goal_difference = row.get("goalDifference")
            goals_against = row.get("goalsAgainst", 0)
            


            cleaned_data_standings.append({"team_position":team_position,
                                        "team_id":team_id,
                                        "matches_played":matches_played,
                                        "points":points,
                                        "goal_difference":goal_difference,                      
                                        "goals_against":goals_against,
                                        })


        df_standings = pd.DataFrame(cleaned_data_standings)





        #----------------------CONNECTING DATABASE AND INSERTING DATA---------------------------------------------#



        #Connection opened

        db_connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password= DB_PASSWORD,
            database = "api_projecte" )

        cursor = db_connection.cursor()

        initialize_database(cursor)



        #TEAMS


        for _, row in df_teams.iterrows():
            sql = """INSERT INTO teams (team_id, team_name) VALUES (%s, %s) ON DUPLICATE KEY UPDATE team_name = VALUES(team_name)
            """
            cursor.execute(sql,
                        (safe_val(row["team_id"]),
                        safe_val(row["team_name"]),),)






        #MATCHES

        for _, row in df_matches.iterrows():
            sql = """INSERT INTO matches(match_id,match_date,home_team_id,away_team_id,home_team_score,away_team_score,match_status,odds) 
            VALUES(%s,%s,%s,%s,%s,%s,%s,%s) 
            ON DUPLICATE KEY UPDATE home_team_score = VALUES(home_team_score),away_team_score = VALUES(away_team_score),match_status = VALUES(match_status); """
            cursor.execute(sql,(safe_val(row["match_id"]),
                                safe_val(row["match_date"]),
                                safe_val(row["home_team_id"]),   #commas are necessary even in one element executions
                                safe_val(row["away_team_id"]),
                                safe_val(row["home_team_score"]),
                                safe_val(row["away_team_score"]),
                                safe_val(row["match_status"]),
                                safe_val(row["odds"]),),)





        #SCORES 


        for _, row in df_scorers.iterrows():   #itterrows() allows pandas to iterate through the rows (aka allows it to loop)

            sql = """INSERT INTO scorers(player_id,player_name,team_id,matches_played,goals) VALUES(%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE
            goals = VALUES(goals) , matches_played = VALUES(matches_played);  
            """

            cursor.execute(sql,(safe_val(row["player_id"]),
                                safe_val(row["player_name"]),
                                safe_val(row["team_id"]),
                                safe_val(row["matches_played"]),
                                safe_val(row["goals"]),),)




        #STANDINGS
        for _, row in df_standings.iterrows():
            sql = """INSERT INTO standings(team_position,team_id,matches_played,points,goal_difference,goals_against) VALUES(%s,%s,%s,%s,%s,%s)
                ON DUPLICATE KEY UPDATE matches_played = VALUES(matches_played),points = VALUES(points),goal_difference = VALUES(goal_difference); 
                """

            cursor.execute(sql,(safe_val(row["team_position"]),
                                safe_val(row["team_id"]),
                                safe_val(row["matches_played"]),
                                safe_val(row["points"]),
                                safe_val(row["goal_difference"]),
                                safe_val(row["goals_against"]),),)


        db_connection.commit()

        #INSERTING DATA INTO UI
        cursor.execute("""SELECT m.match_date,t1.team_name AS home_team,
                        CONCAT(IFNULL(m.home_team_score,"-"),":",
                        IFNULL(m.away_team_score,"-"))AS score,
                        t2.team_name AS away_team,
                        m.match_status 
                        FROM matches m
                        JOIN teams t1 ON m.home_team_id = t1.team_id
                        JOIN teams t2 ON m.away_team_id = t2.team_id
                        ORDER BY m.match_date ASC
                        """)

        rows = cursor.fetchall()

        #Clean the table
        for item in tree_widget.get_children():
            tree_widget.delete(item)

        #Insert new values
        for row_data in rows:
            tree_widget.insert("",tk.END,values=row_data)



        cursor.close()
        db_connection.close()
        

    except Exception as e:
        log_message(f"Error : {e}")
        messagebox.showerror("ERROR",f"An Error Has been occured\n{e}")






#------------------USER INTERFACE-----------------
root = tk.Tk()
root.title("Premier League Matchday Interface")


try:
  root.state("zoomed")
except Exception:
  root.attributes("-zoomed", True)

dark_blue = "#0f172a"
root.config(bg=dark_blue)

title_label = tk.Label(root,text="Premier League Matchday Data Operating System",font=("Arial", 22, "bold"),bg=dark_blue,fg="#ffffff",)
title_label.pack(pady=15)



content_frame = tk.Frame(root, bg=dark_blue)
content_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)

#----Left frame-----
log_frame = tk.Frame(content_frame, bg=dark_blue)
log_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))


log_label = tk.Label(log_frame,text="Pipeline Logs:",font=("Arial", 11, "bold"),bg=dark_blue,fg="#ffffff",anchor="w",)
log_label.pack(fill=tk.X, pady=(0, 5))


log_text = scrolledtext.ScrolledText(log_frame,wrap=tk.WORD,font=("Consolas", 10),bg="#ffffff",fg="#0f172a",insertbackground="black",)
log_text.pack(fill=tk.BOTH, expand=True)



#----UK CLOCK---------
uk_clock_label = tk.Label(log_frame, text="UK Time: Loading...", font=("Consolas", 14, "bold"), bg=dark_blue, fg="#ffffff", anchor="w")
uk_clock_label.pack(fill=tk.X, pady=(5, 0))
update_uk_clock(uk_clock_label)




#---- Right fram----
table_frame = tk.Frame(content_frame, bg=dark_blue)
table_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))



table_label = tk.Label(table_frame,text="Premier League Matches and scores:",font=("Arial", 11, "bold"),bg=dark_blue,fg="#ffffff",anchor="w",)
table_label.pack(fill=tk.X, pady=(0, 5))




# ------------Treeview columns-------
columns = ("date","home","score","away","status")
tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

tree.heading("date", text="Date")
tree.heading("home", text="Home Team")
tree.heading("score",text = "")
tree.heading("away", text="Away Team")
tree.heading("status", text="")



tree.column("date", width=50, anchor="center")
tree.column("home", width=180, anchor="w")
tree.column("score", width=50, anchor="center")
tree.column("away", width=50, anchor="w")
tree.column("status", width=50, anchor="center")


#SCROLLBAR
tree_scroll = ttk.Scrollbar(
    table_frame, orient=tk.VERTICAL, command=tree.yview
)
tree.configure(yscroll=tree_scroll.set)

tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)



# --------Run button------
run_button = tk.Button(root,text="Get Data & Load Standings",font=("Arial", 13, "bold"),bg="#22c55e",fg="white",padx=20,pady=10,relief="raised",cursor="hand2",command=lambda: Football_matchday_pipeline(log_text, tree),)
run_button.pack(pady=15)

root.mainloop()

 