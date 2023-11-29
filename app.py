import streamlit as st
import pandas as pd
import numpy as np
import datetime
from PIL import Image
from streamlit.proto.RootContainer_pb2 import SIDEBAR
import matplotlib.pyplot as plt
import psycopg2 as psy
import os
import base64
import seaborn as sns

from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Football Market Value Effect App",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="auto",
)

# Load environment variables
DB_HOST = os.environ['DB_HOST']
DB_USERNAME = os.environ['DB_USERNAME']
DB_PASSWORD = os.environ['DB_PASSWORD']
DB_NAME = os.environ['DB_NAME']
# DSN string
dsn = f"host={DB_HOST} user={DB_USERNAME} password={DB_PASSWORD} dbname={DB_NAME}"

hero_content = """
    <style>
        .reportview-container {
            background: url("data:image/png;base64, {data_url}") no-repeat center center fixed;
            background-size: cover;
        }
    </style>
    <div style="">
        <h1 style="text-align: center;"> Football Market Value Effect App </h1>
    </div>
    <img src="./images/pl-hero.png" alt="Premier League Hero" style="width: 100%; height: auto;">
    <div style="background-color: #f5f5f5; padding: 10px; border-radius: 10px;">
        <p style="color: #000000; font-size: 16px; font-weight: bold;">This app is designed for Data Engineering course by Mr. Syukron.</p>
        <p style="color: #000000; font-size: 14px;">Please select a page in the sidebar to get started.</p>
    </div>

"""

# Query
teams_query = """
    SELECT * FROM teams
    -- LIMIT 10;
"""

# Matches query
matches_query = """
    SELECT * FROM matches
    -- LIMIT 10;
"""

# Select all tables
all_tables_query = """
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema='public'
    AND table_type='BASE TABLE';
"""

def executeQuery(query):
    # Connect to elephantSQL
    conn = psy.connect(dsn)
    # Create cursor
    cur = conn.cursor()

    cur.execute(query)
    data = cur.fetchall()

    # Close cursor
    cur.close()
    # Close connection
    conn.close()

    return data

def cleanTeams(data):
    # delete the "Team" column in data
    data = data.drop(columns=['Team'])
    # Move "Rank column to the first column"
    data = data[['Rank','TeamID','TeamName','MarketValue','M','W','D','L','G','GA','PTS','xG','xGA','xPTS']]
    # Sort the data by rank
    data = data.sort_values(by=['Rank'])
    return data

def cleanMatches(data, team_data):
    # change the homeTeamId and awayTeamId into team name
    data['homeTeamId'] = data['homeTeamId'].replace(team_data['TeamID'].tolist(), team_data['TeamName'].tolist())
    data['awayTeamId'] = data['awayTeamId'].replace(team_data['TeamID'].tolist(), team_data['TeamName'].tolist())
    # change the played column into Yes or No
    data['played'] = np.where(data['played'] == True, 'Yes', 'No')
    # add a new column called "result". change the cell color based on the result. home = green, draw = grey, away = red
    # if match is not played yet (played = False), the result is None
    data['result'] = np.where(data['played'] == 'No', None, np.where(data['homeScore'] > data['awayScore'], 'Home', np.where(data['homeScore'] == data['awayScore'], 'Draw', 'Away')))

    return data

# Function to highlight the cell
def highlight_cell():
    def highlight(x):
        if x == 'Home':
            color = '#377B2B'
        elif x == 'Draw':
            color = '#666666'
        elif x == 'Away':
            color = '#C93127'
        else:
            color = '#111111'
        return 'background-color: %s' % color
    return highlight

# Function to change the data type to integer
def cell_to_int():
    def integer_cell(x):
        if x != int:
            return None
        # return integer without comma
        if x is float:
            return x.astype(int)
    return integer_cell

def hero_section():
    st.markdown('<h1 style="text-align: center;"> Football Market Value Effect App </h1>', unsafe_allow_html=True)
    image = Image.open('images/pl-hero.png')
    st.image(image, use_column_width=True)

home_content = """
    <style>
        .reportview-container {
            background: url("https://media3.giphy.com/media/3o6Zt6ML9rBj6ZDvO8/giphy.gif?cid=ecf05e47zv7m3b8k5kx7k0xq5x1k0q8x4m8xq0g5j5j2n8q2&ep=v1&ct=g") no-repeat center center fixed;
            background-size: cover;
        }
    </style>
    <div style="background-color: #f5f5f5; padding: 10px; border-radius: 10px;">
        <p style="color: #000000; font-size: 16px; font-weight: bold;">Football Market Value Effect App</p>
        <p style="color: #000000; font-size: 14px;">This app is designed for Data Engineering course by Mr. Syukron.</p>
        <p style="color: #000000; font-size: 14px;">Please select a page in the sidebar to get started.</p>
    </div>

"""

def home_section(params_team_data, params_matches_data):
    st.header("Home")
    # st.markdown(home_content, unsafe_allow_html=True)
    st.write("Welcome to the Football Market Value Effect App! This app is designed for **Data Engineering** course by **Mr. Syukron**.")
    st.info("Please select a page in the sidebar to get started.")
    st.image("https://media3.giphy.com/media/q763Sw8dCByWM2oNI6/giphy.gif?cid=ecf05e471j5edwxvokyxz2r10m0uyhcy3z74h74jto59cs6x&ep=v1_gifs_search&rid=giphy.gif&ct=g", use_column_width="True")
    st.markdown("> # ***Siuuuuuuuuuuuuuuuuuuuuuu*** \n > \- Cristiano Ronaldo")

def data_section(params_team_data, params_matches_data):
    st.header("Data")
    st.write("We have 3 data sources from this project:")
    st.write("1. [Transfermarkt](https://www.transfermarkt.com/)")
    st.write("2. [Football-data.org](https://www.football-data.org/)")
    st.write("3. [Understat.com](https://www.understat.com/)")
    st.image("https://media3.giphy.com/media/N97DxHrADyYGovSlRN/giphy.gif?cid=ecf05e47gyar03htuztm57qe3ji8oce75xhmowop7nrx0c0i&ep=v1_gifs_search&rid=giphy.gif&ct=g", use_column_width="True")

    data = params_team_data
    matches = params_matches_data

    st.info("To sort the data based on the column, please select the column name in the table.")
    st.info("***Arrow up: From Lowest, Arrow down: From Highest***")

    tables = executeQuery(all_tables_query)

    # Transform tables into dataframe with these headers: table_name
    tables = pd.DataFrame(tables, columns=['table_name'])

    # TEAMS ==================================================================
    #! For joined_teams.csv:
    #! Team Market Value: A bar chart comparing the market values of different teams.
    #! Points Accumulation Over Time: A line chart showing how each team's points have accumulated over the season.
    #! Goals For vs. Goals Against: A scatter plot comparing goals scored against goals conceded for each team.
    #! Expected vs. Actual Performance: Comparing expected goals (xG, xGA, xPTS) with actual performance (G, GA, PTS) for each team.
    st.header("Teams")
    st.dataframe(data, use_container_width=True, hide_index=True)
    st.warning("**Legend**")
    col1, col2 = st.columns(2)
    with col1:
        st.warning("1. M = Matches Played \n 2. W = Matches Won \n 3. D = Matches Drawn \n 4. L = Matches Lost \n 5. G = Goals Scored")
    with col2:
        st.warning("6. GA = Goals Against \n 7. PTS = Points \n 8. xG = Expected Goals \n 9. xGA = Expected Goals Against \n 10. xPTS = Expected Points")

    # Create 2 columns
    col1, col2 = st.columns(2)

    # Column 1
    with col1:
        # Visualize the chosen column using matplotlib
        fig, ax = plt.subplots()
        sort_by = st.selectbox("Sort by:", ["MarketValue", "M", "W", "D", "L", "G", "GA", "PTS", "xG", "xGA", "xPTS"])
        direction = st.radio("Direction:", ["From Highest", "From Lowest"])
        sorted_data = data.sort_values(by=[sort_by], ascending=(direction == "From Lowest"))
        ax.bar(sorted_data['TeamName'], sorted_data[sort_by])
        plt.xticks(rotation=90)
        plt.title(f"Premier League {sort_by} Comparison")
        plt.xlabel("Team Name")
        plt.ylabel(sort_by)
        st.pyplot(fig)


    # Column 2
    with col2:
        # Show the rank and name of the teams in table form
        data_sorted_by_rank = data.sort_values(by=['Rank'])
        st.write("Premier League Table")
        if sort_by == "MarketValue":
            st.dataframe(data_sorted_by_rank[['Rank', 'TeamName', sort_by]], hide_index=True, use_container_width=True, height=750)
        else:
            st.dataframe(data_sorted_by_rank[['Rank', 'TeamName', 'MarketValue', sort_by]], hide_index=True, use_container_width=True, height=750)
        st.write("")

    # 3 columns: average Market Value, xG, and xGA
    col1, col2, col3 = st.columns(3)

    # Column 1
    with col1:
        # Average Market Value
        st.subheader("Market Value")
        highest_market_value = data['MarketValue'].max().astype(int)
        average_market_value = round(data['MarketValue'].mean(), 0).astype(int)
        lowest_market_value = data['MarketValue'].min().astype(int)
        st.success(f"Highest: {format(highest_market_value, ',d')} ({data[data['MarketValue'] == data['MarketValue'].max()]['TeamName'].values[0]})")
        st.info(f"Average: {format(average_market_value, ',d')}")
        st.error(f"Lowest: {format(lowest_market_value, ',d')} ({data[data['MarketValue'] == data['MarketValue'].min()]['TeamName'].values[0]})")
        # Create a bar chart
        fig, ax = plt.subplots()
        ax.bar(data['TeamName'], data['MarketValue'])
        plt.xticks(rotation=90)
        plt.title("Market Value")
        plt.xlabel("Team Name")
        plt.ylabel("Market Value")
        # add a line which shows the average market value
        plt.axhline(y=data['MarketValue'].mean(), color='r', linestyle='-')
        # add a text which shows the average market value
        ax.text(0.5, 0.95, f"Average Market Value: {data['MarketValue'].mean()}", fontsize=10, weight='bold', ha='center', transform=ax.transAxes)
        st.pyplot(fig)

    # Column 2
    with col2:
        # Average xG
        st.subheader("xG")
        st.success(f"Highest: {data['xG'].max()} ({data[data['xG'] == data['xG'].max()]['TeamName'].values[0]})")
        st.info(f"Average: {round(data['xG'].mean(), 3)}")
        st.error(f"Lowest: {data['xG'].min()} ({data[data['xG'] == data['xG'].min()]['TeamName'].values[0]})")
        # Create a bar chart
        fig, ax = plt.subplots()
        ax.bar(data['TeamName'], data['xG'])
        plt.xticks(rotation=90)
        plt.title("Expected Goals")
        plt.xlabel("Team Name")
        plt.ylabel("xG")
        # add a line which shows the average xG
        plt.axhline(y=data['xG'].mean(), color='r', linestyle='-')
        # add a text which shows the average xG
        ax.text(0.5, 0.95, f"Average xG: {round(data['xG'].mean(), 3)}", fontsize=10, weight='bold', ha='center', transform=ax.transAxes)
        st.pyplot(fig)

    # Column 3
    with col3:
        # Average xGA
        st.subheader("xGA")
        st.error(f"Highest: {data['xGA'].max()} ({data[data['xGA'] == data['xGA'].max()]['TeamName'].values[0]})")
        st.info(f"Average: {round(data['xGA'].mean(), 3)}")
        st.success(f"Lowest: {data['xGA'].min()} ({data[data['xGA'] == data['xGA'].min()]['TeamName'].values[0]})")
        # Create a bar chart
        fig, ax = plt.subplots()
        ax.bar(data['TeamName'], data['xGA'])
        plt.xticks(rotation=90)
        plt.title("Expected Goals Against")
        plt.xlabel("Team Name")
        plt.ylabel("xGA")
        # add a line which shows the average xGA
        plt.axhline(y=data['xGA'].mean(), color='r', linestyle='-')
        # add a text which shows the average xGA
        ax.text(0.5, 0.95, f"Average xGA: {round(data['xGA'].mean(), 3)}", fontsize=10, weight='bold', ha='center', transform=ax.transAxes)
        st.pyplot(fig)


    # MATCHES =========================================
    #! For joined_matches.csv:
    #! Match Results Heatmap: Displaying home and away scores for each match, providing a quick overview of match outcomes.
    #! Goals Per Matchday: A line or bar chart showing the total number of goals scored in each matchday.
    #! Win/Loss Ratio for Teams: A bar chart indicating how many matches each team won, lost, or drew.
    
    st.header("Matches")
    
    # give the color to the result column and make the homeScore and awayScore as integers
    matches_styled = matches.style.applymap(highlight_cell(), subset=['result'])
    matches_styled = matches_styled.applymap(cell_to_int(), subset=['homeScore', 'awayScore'])
    st.dataframe(matches_styled, use_container_width=True)

    # Create 2 columns
    col1, col2 = st.columns(2)

    # Column 1
    with col1:
        # Create a pie chart which shows the percentage of win, draw, and lose in home matches  
        fig, ax = plt.subplots()
        home_win = matches[matches['result'] == 'Home'].count()['matchId']
        home_draw = matches[matches['result'] == 'Draw'].count()['matchId']
        home_lose = matches[matches['result'] == 'Away'].count()['matchId']
        # Win = green (#377B2B)
        # Draw = yellow (#FDBB2F)
        # Lose = red (#C93127)
        ax.pie([home_win, home_draw, home_lose], labels=['Win', 'Draw', 'Lose'], autopct='%1.1f%%', startangle=90, colors=['#377B2B', '#FDBB2F', '#C93127'])
        ax.text(-0.59, -0.05, f"{home_win} matches", fontsize=10, weight='bold', ha='center')
        ax.text(0.16, -0.72, f"{home_draw} matches", fontsize=10, weight='bold', ha='center')
        ax.text(0.5, 0.12, f"{home_lose} matches", fontsize=10, weight='bold', ha='center')
        ax.axis('equal')
        plt.title("Percentage of Win, Draw, and Lose in Home Matches")
        st.pyplot(fig)


    with col2:
        # create a pie chart which shows how many matches have been played
        fig, ax = plt.subplots()
        played = matches[matches['played'] == 'Yes'].count()['matchId']
        not_played = matches[matches['played'] == 'No'].count()['matchId']
        # Pie chart with the percentage and the exact number of matches
        ax.pie([played, not_played], labels=['Played', 'Not Played'], autopct='%1.1f%%', startangle=90, colors=['#377B2B', '#C93127'])
        ax.text(-0.5, 0.1, f"{played} matches", fontsize=10, weight='bold', ha='center')
        ax.text(0.5, -0.2, f"{not_played} matches", fontsize=10, weight='bold', ha='center')
        ax.axis('equal')
        plt.title("Percentage of Played and Not Played Matches")
        st.pyplot(fig)

    # Match Results Heatmap
    st.subheader("Match Results Heatmap")
    # Create a pivot table
    matches_pivot = matches.pivot_table(index='homeTeamId', columns='awayTeamId', values='result', aggfunc='count')
    # Create a heatmap
    fig, ax = plt.subplots()
    ax.imshow(matches_pivot, cmap='RdYlGn', interpolation='nearest')
    # Set the ticks
    ax.set_xticks(np.arange(len(matches_pivot.columns)))
    ax.set_yticks(np.arange(len(matches_pivot.index)))
    # Set the tick labels
    ax.set_xticklabels(matches_pivot.columns)
    ax.set_yticklabels(matches_pivot.index)
    # Rotate the tick labels and set their alignment
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right', rotation_mode='anchor')
    # Loop over data dimensions and create text annotations
    for i in range(len(matches_pivot.index)):
        for j in range(len(matches_pivot.columns)):
            text = ax.text(j, i, matches_pivot.iloc[i, j], ha='center', va='center', color='black', fontsize=2)
    ax.set_title("Match Results Heatmap")
    fig.tight_layout()
    st.pyplot(fig)
    
    # TABLES =========================================
    st.header("Tables")
    st.dataframe(tables, use_container_width=True)

    # 

# Model Section ====================================================================
def team_performance_section(params_team_data, params_matches_data):
    st.header("Team Performance")
    st.info("This section is used to compare the performance of 2 teams.")
    st.image("https://media1.giphy.com/media/jfXyrRHxJUYJSXoz2u/giphy.gif?cid=ecf05e47myx87z7mzastj0sywe4o5yq8q7pao8m4kpf4s3fn&ep=v1_gifs_search&rid=giphy.gif&ct=g", use_column_width="True")

    matches_data = params_matches_data
    team_data = params_team_data

    # Create 2 columns
    col1, col2 = st.columns(2)

    # Column 1
    with col1:
        team_name1 = st.selectbox("Select team 1:", team_data['TeamName'].tolist())
        st.subheader(team_name1)
        st.write(team_data[team_data['TeamName'] == team_name1])

        # Count how many times team 1 played in home that has been played
        home_matches = matches_data[(matches_data['homeTeamId'] == team_name1) & (matches_data['played'] == 'Yes')].count()['matchId']
        # Count how many times team 1 played in away
        away_matches = matches_data[(matches_data['awayTeamId'] == team_name1) & (matches_data['played'] == 'Yes')].count()['matchId']
        # Create a pie chart which shows the percentage of home and away matches
        fig, ax = plt.subplots()
        ax.pie([home_matches, away_matches], labels=['Home', 'Away'], autopct='%1.1f%%', startangle=90, colors=['#377B2B', '#C93127'])
        ax.axis('equal')
        plt.title("Percentage of Home and Away Matches")
        st.pyplot(fig)
        # 2 subcolumns: home and away matches
        subcol1, subcol2 = st.columns(2)
        with subcol1:
            st.write(f"Home matches: {home_matches}")
        with subcol2:
            st.write(f"Away matches: {away_matches}")

        # Count how many times team 1 won in home
        home_win = matches_data[(matches_data['homeTeamId'] == team_name1) & (matches_data['result'] == 'Home')].count()['matchId']
        home_lose = matches_data[(matches_data['homeTeamId'] == team_name1) & (matches_data['result'] == 'Away')].count()['matchId']
        home_draw = matches_data[(matches_data['homeTeamId'] == team_name1) & (matches_data['result'] == 'Draw')].count()['matchId']
        # Pie chart to show the percentage of win, draw, and lose in home matches
        fig, ax = plt.subplots()
        ax.pie([home_win, home_draw, home_lose], labels=['Win', 'Draw', 'Lose'], autopct='%1.1f%%', startangle=90, colors=['#377B2B', '#FDBB2F', '#C93127'])
        ax.axis('equal')
        plt.title("Percentage of Win, Draw, and Lose in Home Matches")
        st.pyplot(fig)
        # 2 subcolumns: home and away matches
        subcol1, subcol2 = st.columns(2)
        with subcol1:
            st.write(f"Home win: {home_win}")
            st.write(f"Home draw: {home_draw}")
        with subcol2:
            st.write(f"Home lose: {home_lose}")
            st.write(f"Home matches: {home_matches}")

        # Count how many times team 1 won in away
        away_win = matches_data[(matches_data['awayTeamId'] == team_name1) & (matches_data['result'] == 'Away')].count()['matchId']
        away_lose = matches_data[(matches_data['awayTeamId'] == team_name1) & (matches_data['result'] == 'Home')].count()['matchId']
        away_draw = matches_data[(matches_data['awayTeamId'] == team_name1) & (matches_data['result'] == 'Draw')].count()['matchId']
        # Pie chart to show the percentage of win, draw, and lose in away matches
        fig, ax = plt.subplots()
        ax.pie([away_win, away_draw, away_lose], labels=['Win', 'Draw', 'Lose'], autopct='%1.1f%%', startangle=90, colors=['#377B2B', '#FDBB2F', '#C93127'])
        ax.axis('equal')
        plt.title("Percentage of Win, Draw, and Lose in Away Matches")
        st.pyplot(fig)
        # 2 subcolumns: home and away matches
        subcol1, subcol2 = st.columns(2)
        with subcol1:
            st.write(f"Away win: {away_win}")
            st.write(f"Away draw: {away_draw}")
        with subcol2:
            st.write(f"Away lose: {away_lose}")
            st.write(f"Away matches: {away_matches}")
    
    # Column 2
    with col2:
        team_name2 = st.selectbox("Select team 2:", team_data['TeamName'].tolist())
        st.subheader(team_name2)
        st.write(team_data[team_data['TeamName'] == team_name2])

        # Count how many times team 2 played in home that has been played
        home_matches = matches_data[(matches_data['homeTeamId'] == team_name2) & (matches_data['played'] == 'Yes')].count()['matchId']
        # Count how many times team 2 played in away
        away_matches = matches_data[(matches_data['awayTeamId'] == team_name2) & (matches_data['played'] == 'Yes')].count()['matchId']
        # Create a pie chart which shows the percentage of home and away matches
        fig, ax = plt.subplots()
        ax.pie([home_matches, away_matches], labels=['Home', 'Away'], autopct='%1.1f%%', startangle=90, colors=['#377B2B', '#C93127'])
        ax.axis('equal')
        plt.title("Percentage of Home and Away Matches")
        st.pyplot(fig)
        # 2 subcolumns: home and away matches
        subcol1, subcol2 = st.columns(2)
        with subcol1:
            st.write(f"Home matches: {home_matches}")
        with subcol2:
            st.write(f"Away matches: {away_matches}")

        # Count how many times team 2 won in home
        home_win = matches_data[(matches_data['homeTeamId'] == team_name2) & (matches_data['result'] == 'Home')].count()['matchId']
        home_lose = matches_data[(matches_data['homeTeamId'] == team_name2) & (matches_data['result'] == 'Away')].count()['matchId']
        home_draw = matches_data[(matches_data['homeTeamId'] == team_name2) & (matches_data['result'] == 'Draw')].count()['matchId']
        # Pie chart to show the percentage of win, draw, and lose in home matches
        fig, ax = plt.subplots()
        ax.pie([home_win, home_draw, home_lose], labels=['Win', 'Draw', 'Lose'], autopct='%1.1f%%', startangle=90, colors=['#377B2B', '#FDBB2F', '#C93127'])
        ax.axis('equal')
        plt.title("Percentage of Win, Draw, and Lose in Home Matches")
        st.pyplot(fig)
        # 2 subcolumns: home and away matches
        subcol1, subcol2 = st.columns(2)
        with subcol1:
            st.write(f"Home win: {home_win}")
            st.write(f"Home draw: {home_draw}")
        with subcol2:
            st.write(f"Home lose: {home_lose}")
            st.write(f"Home matches: {home_matches}")

        # Count how many times team 2 won in away
        away_win = matches_data[(matches_data['awayTeamId'] == team_name2) & (matches_data['result'] == 'Away')].count()['matchId']
        away_lose = matches_data[(matches_data['awayTeamId'] == team_name2) & (matches_data['result'] == 'Home')].count()['matchId']
        away_draw = matches_data[(matches_data['awayTeamId'] == team_name2) & (matches_data['result'] == 'Draw')].count()['matchId']
        # Pie chart to show the percentage of win, draw, and lose in away matches
        fig, ax = plt.subplots()
        ax.pie([away_win, away_draw, away_lose], labels=['Win', 'Draw', 'Lose'], autopct='%1.1f%%', startangle=90, colors=['#377B2B', '#FDBB2F', '#C93127'])
        ax.axis('equal')
        plt.title("Percentage of Win, Draw, and Lose in Away Matches")
        st.pyplot(fig)
        # 2 subcolumns: home and away matches
        subcol1, subcol2 = st.columns(2)
        with subcol1:
            st.write(f"Away win: {away_win}")
            st.write(f"Away draw: {away_draw}")
        with subcol2:
            st.write(f"Away lose: {away_lose}")
            st.write(f"Away matches: {away_matches}")

    # Comparison between team 1 and team 2
    st.subheader("Comparison Between Team 1 and Team 2")
    # Create a dataframe which contains the data of team 1 and team 2
    team1 = team_data[team_data['TeamName'] == team_name1]
    team2 = team_data[team_data['TeamName'] == team_name2]
    
    # 3 columns: MarketValue Comparison, xG Comparison, and xGA Comparison
    col1, col2, col3 = st.columns(3)

    # Column 1
    with col1:
        # Create a bar chart which shows the market value comparison between team 1 and team 2
        fig, ax = plt.subplots()
        ax.bar(team1['TeamName'], team1['MarketValue'])
        ax.bar(team2['TeamName'], team2['MarketValue'])
        plt.xticks(rotation=0)
        plt.title("Market Value Comparison")
        plt.xlabel("Team Name")
        plt.ylabel("Market Value")
        st.pyplot(fig)
        # 2 subcolumns
        subcol1, subcol2 = st.columns(2)
        # write the market value of team 1 and team 2 with the format of 1,000,000
        with subcol1:
            st.info(f"{team_name1}: {format(team1['MarketValue'].values[0], ',d')}")
        with subcol2:
            st.info(f"{team_name2}: {format(team2['MarketValue'].values[0], ',d')}")
        if team1['MarketValue'].values[0] > team2['MarketValue'].values[0]:
            st.success(f"{team_name1} has a better market value than {team_name2}")
        elif team1['MarketValue'].values[0] < team2['MarketValue'].values[0]:
            st.error(f"{team_name2} has a better market value than {team_name1}")
        else:
            st.warning(f"{team_name1} and {team_name2} have the same market value")


    # Column 2
    with col2:
        # Create a bar chart which shows the xG comparison between team 1 and team 2
        fig, ax = plt.subplots()
        ax.bar(team1['TeamName'], team1['xG'])
        ax.bar(team2['TeamName'], team2['xG'])
        plt.xticks(rotation=0)
        plt.title("xG Comparison")
        plt.xlabel("Team Name")
        plt.ylabel("xG")
        st.pyplot(fig)
        subcol1, subcol2 = st.columns(2)
        with subcol1:
            st.info(f"{team_name1}: {team1['xG'].values[0]}")
        with subcol2:
            st.info(f"{team_name2}: {team2['xG'].values[0]}")
        if team1['xG'].values[0] > team2['xG'].values[0]:
            st.success(f"{team_name1} has a better offense than {team_name2}")
        elif team1['xG'].values[0] < team2['xG'].values[0]:
            st.error(f"{team_name2} has a better offense than {team_name1}")
        else:
            st.warning(f"{team_name1} and {team_name2} have the same offense")

    # Column 3
    with col3:
        # Create a bar chart which shows the xGA comparison between team 1 and team 2
        fig, ax = plt.subplots()
        ax.bar(team1['TeamName'], team1['xGA'])
        ax.bar(team2['TeamName'], team2['xGA'])
        plt.xticks(rotation=0)
        plt.title("xGA Comparison")
        plt.xlabel("Team Name")
        plt.ylabel("xGA")
        st.pyplot(fig)
        subcol1, subcol2 = st.columns(2)
        with subcol1:
            st.info(f"{team_name1}: {team1['xGA'].values[0]}")
        with subcol2:
            st.info(f"{team_name2}: {team2['xGA'].values[0]}")
        if team1['xGA'].values[0] > team2['xGA'].values[0]:
            st.success(f"{team_name1} has a better defense than {team_name2}")
        elif team1['xGA'].values[0] < team2['xGA'].values[0]:
            st.error(f"{team_name2} has a better defense than {team_name1}")
        else:
            st.warning(f"{team_name1} and {team_name2} have the same defense")
    
    # 3 columns
    col1, col2, col3 = st.columns(3)

    # Column 1
    with col1:
        # Comparison of home wins of team 1 and team 2
        fig, ax = plt.subplots()
        team1_home_win = matches_data[(matches_data['homeTeamId'] == team_name1) & (matches_data['result'] == 'Home')].count()['matchId']
        team2_home_win = matches_data[(matches_data['homeTeamId'] == team_name2) & (matches_data['result'] == 'Home')].count()['matchId']
        ax.bar(team1['TeamName'], team1_home_win)
        ax.bar(team2['TeamName'], team2_home_win)
        plt.xticks(rotation=0)
        plt.title("Home Wins Comparison")
        plt.xlabel("Team Name")
        plt.ylabel("Home Wins")
        st.pyplot(fig)

        # 2 subcolumns
        subcol1, subcol2 = st.columns(2)
        # write the home wins of team 1 and team 2
        with subcol1:
            st.info(f"{team_name1}: {team1_home_win}")
        with subcol2:
            st.info(f"{team_name2}: {team2_home_win}")
        if home_win > away_win:
            st.success(f"{team_name1} has more home wins than {team_name2}")
        elif home_win < away_win:
            st.error(f"{team_name2} has more home wins than {team_name1}")
        else:
            st.warning(f"{team_name1} and {team_name2} have the same home wins")

    # Column 2
    with col2:
        # Comparison of away wins of team 1 and team 2
        fig, ax = plt.subplots()
        team1_away_win = matches_data[(matches_data['awayTeamId'] == team_name1) & (matches_data['result'] == 'Away')].count()['matchId']
        team2_away_win = matches_data[(matches_data['awayTeamId'] == team_name2) & (matches_data['result'] == 'Away')].count()['matchId']
        ax.bar(team1['TeamName'], team1_away_win)
        ax.bar(team2['TeamName'], team2_away_win)   
        plt.xticks(rotation=0)
        plt.title("Away Wins Comparison")
        plt.xlabel("Team Name")
        plt.ylabel("Away Wins")
        st.pyplot(fig)
        # 2 subcolumns
        subcol1, subcol2 = st.columns(2)
        # write the away wins of team 1 and team 2
        with subcol1:
            st.info(f"{team_name1}: {team1_away_win}")
        with subcol2:
            st.info(f"{team_name2}: {team2_away_win}")
        if away_win > home_win:
            st.success(f"{team_name1} has more away wins than {team_name2}")
        elif away_win < home_win:
            st.error(f"{team_name2} has more away wins than {team_name1}")
        else:
            st.warning(f"{team_name1} and {team_name2} have the same away wins")

    # Column 3
    with col3:
        # Comparison of performance: 
        # G - xG, GA - xGA, PTS - xPTS
        fig, ax = plt.subplots()
        # G - xG
        team1_g_xg = round(team1['G'].values[0] - team1['xG'].values[0], 3)
        team2_g_xg = round(team2['G'].values[0] - team2['xG'].values[0], 3)
        # GA - xGA
        team1_ga_xga = round(team1['GA'].values[0] - team1['xGA'].values[0], 3)
        team2_ga_xga = round(team2['GA'].values[0] - team2['xGA'].values[0], 3)
        # PTS - xPTS
        team1_pts_xpts = round(team1['PTS'].values[0] - team1['xPTS'].values[0], 3)
        team2_pts_xpts = round(team2['PTS'].values[0] - team2['xPTS'].values[0], 3)
        category_names = ['Offensive', 'Defensive', 'Overall Perf']
        # Create a bar chart
        team1_values = [team1_g_xg, team1_ga_xga, team1_pts_xpts]
        team2_values = [team2_g_xg, team2_ga_xga, team2_pts_xpts]
        
        bar_width = 0.35
        index = np.arange(len(category_names))
        plt.bar(index, team1_values, bar_width, label=team_name1)
        plt.bar(index + bar_width, team2_values, bar_width, label=team_name2)
        plt.xticks(index + bar_width / 2, category_names)
        plt.legend()
        plt.title("Performance Comparison")
        plt.ylabel("Value")
        st.pyplot(fig)

        # 2 subcolumns
        subcol1, subcol2 = st.columns(2)
        # write the performance of team 1 and team 2
        with subcol1:
            st.info(f"{team_name1}: {team1_g_xg}, {team1_ga_xga}, {team1_pts_xpts}")
        with subcol2:
            st.info(f"{team_name2}: {team2_g_xg}, {team2_ga_xga}, {team2_pts_xpts}")
        if team1_g_xg > team2_g_xg and team1_ga_xga < team2_ga_xga and team1_pts_xpts > team2_pts_xpts:
            st.success(f"{team_name1} has a better performance than {team_name2}")
        elif team1_g_xg < team2_g_xg and team1_ga_xga > team2_ga_xga and team1_pts_xpts < team2_pts_xpts:
            st.error(f"{team_name2} has a better performance than {team_name1}")
        else:
            st.warning(f"{team_name1} and {team_name2} have the same performance")


# About Section ====================================================================
def about_section():
    st.header("About")
    st.write("This app was created by [Izzat Arroyan](https://www.linkedin.com/in/izzatarroyan/), [Giga Hidjrika Aura Adkhy](https://www.linkedin.com/in/gigahidjrikaaa/), and [Daffa Kamal](https://www.linkedin.com/in/daffakamal/).")

def test_section():
    # Title
    st.title("Test Page")
    st.write("This is my first Streamlit app!")

    st.write("Here's our first attempt at using data to create a table:")
    st.write(pd.DataFrame({
        'first column': [1, 2, 3, 4],
        'second column': [10, 20, 30, 40]
    }))

    button = st.button("Say hello")
    if button:
        st.write("Why hello there")
    else:
        st.write("Goodbye")

    agree = st.checkbox("I agree")
    if agree:
        st.write("Great!")
    else:
        st.write("Nothing for you")

    genre = st.radio(
        "What's your favorite movie genre",
        ('Comedy', 'Drama', 'Documentary')
    )
    if genre == 'Comedy':
        st.write("You selected comedy.")
    else:
        st.write("You didn't select comedy.")

    option = st.selectbox(
        'How would you like to be contacted?',
        ('Email', 'Home phone', 'Mobile phone')
    )
    st.write('You selected:', option)

    options = st.multiselect(
        'What are your favorite colors',
        ['Green', 'Yellow', 'Red', 'Blue'],
        ['Yellow', 'Red']
    )
    st.write('You selected:', options)

    age = st.slider('How old are you?', 0, 130, 25)
    st.write("I'm ", age, 'years old')

    values = st.slider(
        'Select a range of values',
        0.0, 100.0, (25.0, 75.0)
    )
    st.write('Values:', values)

    title = st.text_input('Movie title', 'Life of Brian')
    st.write('The current movie title is', title)

    number = st.number_input('Insert a number')
    st.write('The current number is ', number)

    txt = st.text_area('Text to analyze', '''
        It was the best of times, it was the worst of times, it was
        the age of wisdom, it was the age of foolishness, it was
        the epoch of belief, it was the epoch of incredulity, it
        was the season of Light, it was the season of Darkness, it
        was the spring of hope, it was the winter of despair, (...)
    ''')
    st.write('Sentiment:', txt)

    d = st.date_input(
        "When's your birthday",
        datetime.date(2019, 7, 6)
    )
    st.write('Your birthday is:', d)

    t = st.time_input('Set an alarm for', datetime.time(8, 45))
    st.write('Alarm is set for', t)

    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    if uploaded_file is not None:
        data = pd.read_csv(uploaded_file)
        st.write(data)

    color = st.color_picker('Pick A Color', '#00f900')
    st.write('The current color is', color)

    st.write("This is the `st.code` function:")
    st.code("import numpy as np\nimport pandas as pd")

    st.write("And this is the `st.echo` function:")
    st.echo("import numpy as np\nimport pandas as pd")

    st.write("This is the `st.latex` function:")
    st.latex(r''' e^{i\pi} + 1 = 0 ''')

    st.write("This is the `st.markdown` function:")
    st.markdown("Streamlit is **_really_ cool**.")

    st.write("This is the `st.pyplot` function:")
    arr = np.random.normal(1, 1, size=100)
    plt.hist(arr, bins=20)
    st.pyplot(plt)

    st.write("This is the `st.table` function:")
    df = pd.DataFrame(
        np.random.randn(10, 5),
        columns=('col %d' % i for i in range(5))
    )
    st.table(df)

    st.write("This is the `st.dataframe` function:")
    df = pd.DataFrame(
        np.random.randn(10, 5),
        columns=('col %d' % i for i in range(5))
    )
    st.dataframe(df)

    st.write("This is the `st.json` function:")
    st.json({
        'foo': 'bar',
        'baz': 'boz',
        'stuff': [
            'stuff 1',
            'stuff 2',
            'stuff 3',
            'stuff 5',
        ],
    })

    st.write("This is the `st.balloons` function:")
    st.balloons()

    st.write("This is the `st.error` function:")
    st.error("This is an error")

    st.write("This is the `st.warning` function:")
    st.warning("This is a warning")

    st.write("This is the `st.info` function:")
    st.info("This is a purely informational message")

    st.write("This is the `st.success` function:")
    st.success("This is a success message!")

    st.write("This is the `st.exception` function:")
    e = RuntimeError('This is an exception of type RuntimeError')
    st.exception(e)

    st.write("This is the `st.help` function:")
    st.help(pd.DataFrame)

def main():
    st.sidebar.title("Navigation")
    st.sidebar.subheader("Go to")
    app_mode = st.sidebar.radio("", ["Home", "Data", "Team Performance", "About", "TestPage"])
    
    team_data = None
    matches_data = None
    if team_data is None or matches_data is None:
        team_data = executeQuery(teams_query)
        team_data = pd.DataFrame(team_data, columns=['TeamID','TeamName','MarketValue','Rank','Team','M','W','D','L','G','GA','PTS','xG','xGA','xPTS'])
        team_data = cleanTeams(team_data)

        matches_data = executeQuery(matches_query)
        matches_data = pd.DataFrame(matches_data, columns=['matchId','matchday','homeTeamId','awayTeamId','homeScore','awayScore', 'played'])
        matches_data = cleanMatches(matches_data, team_data)


    hero_section()
    if app_mode == "Home":
        home_section(team_data, matches_data)
    if app_mode == "Data":
        data_section(team_data, matches_data)
    if app_mode == "Team Performance":
        team_performance_section(team_data, matches_data)
    if app_mode == "About":
        about_section(team_data, matches_data)
    if app_mode == "TestPage":
        test_section()

if __name__ == "__main__":
    main()