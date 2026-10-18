import requests
import pandas as pd
import time
import schedule
import mysql.connector
import tkinter as tk
import messagebox as mb





FOOTBALL_URL_matches = "https://api.football-data.org/v4/competitions/PL/matches"

FOOTBALL_URL_scorers = "https://api.football-data.org/v4/competitions/PL/scorers"

FOOTBALL_URL_standings = "https://api.football-data.org/v4/competitions/PL/standings"

headers = { "X-Auth-Token": "a35f6ef38b5f4927bbc6fac47281a529" }



#-----------------REQUESTING API DATA AND TURNING IT INTO A DICTIONARY----------------------#



#Requesting Matches (and automatically teams) data from the API

response_matches = requests.get(FOOTBALL_URL_matches, headers=headers)

if response_matches.status_code == 200:
    print("API request for matchessuccessful!")

    data_matches = response_matches.json() #gets json data to a dictionary

    print("Retrieved keys: ", data_matches.keys())

elif response_matches.status_code == 401:
    print("too many requests")
else:
    print(f"An error occurred while fetching matches API data: {response_matches.status_code}")






#Requesting Scorers data from the API


response_scorers = requests.get(FOOTBALL_URL_scorers, headers=headers)

if response_scorers.status_code == 200:
    print( "API request for scorers successful!")

    data_scorers = response_scorers.json() #gets json data to a dictionary

    print("Retrieved keys: ", data_scorers.keys())

elif response_scorers.status_code == 401:
    print("too many requests")
else:
    print(f"An error occurred while fetching scorer API data: {response_scorers.status_code}")





#Requesting Standing data from the API

response_standings = requests.get(FOOTBALL_URL_standings, headers = headers)

if response_standings.status_code == 200:
    print("API request for standings successful!")

    data_standings = response_standings.json()

    print("Retrieved keys: ", data_standings.keys())

elif response_standings.status_code == 401:
    print("too many requests")
else:
    print(f"An error occured while fetching the standings API data: {response_standings.status_code}")







#----------------------DATA CLEANING AND TRANSFORMATION WIH PANDAS--------------------------#



#FOR MATCHES TABLE
#MATCHES (match_id, home_team, away_team, match_date, match_status, home_score, away_score,odds)

raw_matches = data_matches.get("matches", [])

cleaned_data_matches = []


for match in raw_matches:
    match_id = match.get("id")
    home_team = match.get("homeTeam", {}).get("name")  #[] kullanınca key error fırlatılır ve kod çöker
    away_team = match.get("awayTeam", {}).get("name")
    match_date = match.get("utcDate")

    score_info = match.get("score", {}).get("fullTime",{})
    home_score = score_info.get("home")
    away_score = score_info.get("away")
    match_status = match.get("status")
    odds = match.get("odds", {}).get("homeWin")  # Assuming you want the home win odds

    cleaned_data_matches.append({"match_id":match_id,
                       "home_team":home_team,
                       "away_team":away_team,
                       "match_date":match_date,
                       "match_status":match_status,
                       "home_score":home_score,
                       "away_score":away_score,
                       "odds":odds
                       })


df_matches = pd.DataFrame(cleaned_data_matches)

#print(df_matches.head(20))  # Display the first 20 rows of the DataFrame




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
    player_name = scorer.get("player", {}).get("name")
    team_id = scorer.get("team", {}).get("id")
    matches_played = scorer.get("playedMatches")
    goals = scorer.get("goals")


    cleaned_data_scorers.append({"player_id":player_id,
                       "player_name":player_name,
                       "team_id":team_id,
                      "matches_played":matches_played,
                       "goals":goals
                       })


df_scorers = pd.DataFrame(cleaned_data_scorers)

#print(df_scorers.head(10))



#FOR STANDINGS TABLE
#STANDINGS (team_position, team_id, matches_played, points, goals_for_against, goal_difference)

raw_standings = data_standings.get("standings",[])

cleaned_data_standings = []


for standing in raw_standings:
    if standing.get("type") == "TOTAL":
        table_data = standing.get("table", [])
        break




for row in table_data:
    team_position = row.get("position")
    team_id = row.get("team", {}).get("id")
    matches_played = row.get("playedGames")
    points = row.get("points")
    goal_difference = row.get("goalDifference")
    goals_against = row.get("goalsAgainst", 0)
    goals_for = row.get("goalsFor", 0)
    goals_for_against = f"{goals_for} : {goals_against}"


    cleaned_data_standings.append({"team_position":team_position,
                                   "team_id":team_id,
                                   "matches_played":matches_played,
                                   "points":points,
                                   "goal_difference":goal_difference,                      
                                   "goals_for_against":goals_for_against
                                   })


df_standings = pd.DataFrame(cleaned_data_standings)



