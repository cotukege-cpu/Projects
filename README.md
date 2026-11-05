Premier League Matchday Pipeline & Dashboard
A Python application that fetches live Premier League matches, top scorers, and standings from the Football-Data API, stores them in a MySQL database, and displays everything through a clean desktop GUI (tkinter)


Features:

- Live Data Fetching: Pulls matches, scorers, and standings directly from the Football-Data.org API.

- Auto Database Setup (initialize_database): Automatically creates the required MySQL tables (`teams`, `matches`, `scorers`, `standings`) with foreign key relations on startup.

- Live UK Time Clock: A real-time digital clock in the bottom-left corner of the interface showing the current UK time.

- Data Cleaning: Uses Pandas to process and clean raw API data before saving it to the database.

- Logs & UI Feedback: Includes a scrollable log panel and status popups to track pipeline progress.




THE PROGRAMMING LANGUAGE AND LIBRARIES USED:

- Python (3.9+)
- Tkinter (GUI)
- Pandas (Data processing)
- Requests(API requests)
- MySQL Connector & MySQL(Database)
- python-dotenv (Environment & API key management)
- Zoneinfo (Timezone management)



SET UP:

1.Clone Repository:

"""Bash
git clone https://github.com/cotukege-cpu/Projects.git
cd Projects/"Project API"


2.Activate virtual enviroment:
python -m venv .venv

# On Windows:
.venv\Scripts\activate


3.Install Requirements:

pip install -r requirements.txt



4. Configure Enviroment:
Create a .env file inside the Project API folder and add your add your own API key and your own database password

API_KEY=your_football_data_api_key
DB_PASSWORD=your_mysql_password



5. Run the Application

python "Football API projecte.py"



6. Execution And Verification:
Database Initialization:  When starting up, the app automatically checks for MySQL connections and creates the teams, matches, scorers, and standings tables if they do not exist.

Run pipeline: Click the Run Pipeline button on the interface to start fetching data

Monitor Logs: Follow real-time log messages and check the UK Time in the bottom left corner to confirm execution status.

Inspect Database: Open your MySQL workbench to verify that the latest Premier League data is there
