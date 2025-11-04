import streamlit as st
import pandas as pd
from utils.db_connection import get_connection

#@st.cache_data(ttl=60)
def run_query(query):
    try:
        conn = get_connection()
        df = pd.read_sql(query, conn)
        return df
    except Exception as e:
        st.error(f"Error executing query: {e}")
        return pd.DataFrame()



# 25 SQL Queries

queries = {
    "1 All Indian Players": 
    """
        SELECT player_name, role, batting_style, bowling_style, intl_team
        FROM Players WHERE intl_team = 'India';
    """,
    "2 All cricket matches that were played in the last Few days":
    """
        SELECT 
        match_id,
        match_desc,
        match_format,
        FROM_UNIXTIME(start_date / 1000) AS start_date,
        FROM_UNIXTIME(end_date / 1000) AS end_date,
        state,
        status
        FROM Matches
        WHERE FROM_UNIXTIME(end_date / 1000) >= NOW() - INTERVAL 180 DAY
        ORDER BY end_date DESC;
    """,
    "3 Top 10 ODI Run Scorers": 
    """
        SELECT p.player_name, s.matchtype, s.runs, s.batting_avg,s.hundreds
        FROM Player_Stats_Summary s
        JOIN Players p ON s.player_id = p.player_id
        WHERE s.matchtype = 'ODI'
        ORDER BY s.runs DESC
        LIMIT 10;
    """,
    "4 Cricket venues with seating capacity >30000": 
    """
        select ground,city,country,seating_capacity
        From Venues 
        where seating_capacity>30000
        order by seating_capacity desc;
    """,
    "5 Team win": 
    """
        select state_title as Team_win,count(*) as total_wins
        from matches
        group by state_title
        order by total_wins desc;
    """,
    "6 Count of player roles": 
    """
        select role,count(*) 
        from players
        group by role;
    """,
    "7 Highest Run Scorer Per Format": 
    """
        SELECT matchtype, MAX(runs) AS max_runs
        FROM Player_Stats_Summary
        GROUP BY matchtype;
    """,
    "8 Series that started in the year 2024.": 
    """
        SELECT s.series_name,COUNT(m.match_id) AS total_matches,GROUP_CONCAT(DISTINCT v.country) AS countries,MIN(FROM_UNIXTIME(s.series_start_dt / 1000)) AS series_start_date
        FROM Matches m
        JOIN Series s ON m.series_id = s.series_id
        JOIN Venues v ON m.venue_id = v.venue_id
        WHERE YEAR(FROM_UNIXTIME(s.series_start_dt / 1000)) = 2024
        GROUP BY s.series_name;
    """,
   "9 all-rounder scored >1000 runs AND taken >50 wickets": 
    """
        SELECT p.player_id,p.player_name,SUM(s.runs)   AS total_runs,SUM(s.wickets) AS total_wickets
        FROM Player_Stats_Summary s
        JOIN Players p ON p.player_id = s.player_id
        WHERE p.role LIKE '%All-Rounder%'
        GROUP BY p.player_id, p.player_name
        HAVING SUM(s.runs) > 1000 AND SUM(s.wickets) > 50
        ORDER BY total_runs DESC;
    """,
    "10 last 20 completed matches": 
    """
        SELECT m.match_id,m.match_desc,t1.team_name AS team1,t2.team_name AS team2,TRIM(SUBSTRING_INDEX(m.status, ' won', 1)) AS winning_team,TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(m.status, 'won by ', -1), ' ', 2)) AS victory_info,
        CASE
        WHEN m.status LIKE '%won by%runs%' THEN 'runs'
        WHEN m.status LIKE '%won by%wickets%' THEN 'wickets'
        ELSE NULL
        END AS victory_type,  v.ground AS venue,FROM_UNIXTIME(m.start_date / 1000) AS match_date
        FROM Matches m
        JOIN Teams t1 ON m.team1_id = t1.team_id
        JOIN Teams t2 ON m.team2_id = t2.team_id
        JOIN Venues v ON m.venue_id = v.venue_id
        WHERE m.state = 'Complete'
        ORDER BY m.start_date DESC;
    """,
    "11 player's performance across different cricket formats": 
    """
    SELECT
    p.player_id,
    p.player_name,
    SUM(CASE WHEN s.matchtype = 'Test' THEN s.runs ELSE 0 END)    AS test_runs,
    SUM(CASE WHEN s.matchtype = 'ODI'  THEN s.runs ELSE 0 END)    AS odi_runs,
    SUM(CASE WHEN s.matchtype = 'T20'  THEN s.runs ELSE 0 END)    AS t20_runs,
    (SUM(s.runs) / NULLIF(SUM(s.matches),0))                      AS overall_batting_avg,
    COUNT(DISTINCT s.matchtype)                                   AS formats_played
    FROM Player_Stats_Summary s
    JOIN Players p ON p.player_id = s.player_id
    GROUP BY p.player_id, p.player_name
    HAVING formats_played >= 2
    ORDER BY overall_batting_avg DESC;
    """,
    "4 Top 10 Wicket Takers (ODI)": """
        SELECT p.player_name, s.matchtype, s.wickets, s.bowling_avg
        FROM Player_Stats_Summary s
        JOIN Players p ON s.player_id = p.player_id
        WHERE s.matchtype = 'ODI'
        ORDER BY s.wickets DESC
        LIMIT 10;
    """,
    "12 Batting Average > 50 (All Formats)": """
        SELECT p.player_name, s.matchtype, s.batting_avg
        FROM Player_Stats_Summary s
        JOIN Players p ON p.player_id = s.player_id
        WHERE s.batting_avg > 50
        ORDER BY s.batting_avg DESC;
    """,

    "13 Player with Most Centuries": """
        SELECT p.player_name, SUM(s.hundreds) AS total_centuries
        FROM Player_Stats_Summary s
        JOIN Players p ON p.player_id = s.player_id
        GROUP BY p.player_name
        ORDER BY total_centuries DESC
        LIMIT 1;
    """,

    "14 Recent Top Batting Performances": """
        SELECT p.player_name, r.opponent_team, r.score, r.matchtype, r.match_date
        FROM Recent_Batting r
        JOIN Players p ON p.player_id = r.player_id
        ORDER BY r.match_date DESC
        LIMIT 15;
    """,

    "15 Recent Top Bowling Performances": """
        SELECT p.player_name, r.opponent_team, r.wickets, r.matchtype, r.match_date
        FROM Recent_Bowling r
        JOIN Players p ON p.player_id = r.player_id
        ORDER BY r.match_date DESC
        LIMIT 15;
    """,

    "16 Team-wise Player Count": """
        SELECT team_name, COUNT(player_id) AS total_players
        FROM Player_Teams
        GROUP BY team_name
        ORDER BY total_players DESC;
    """,


    "17 Fastest Century Scorers": """
        SELECT p.player_name, s.matchtype, s.strike_rate
        FROM Player_Stats_Summary s
        JOIN Players p ON s.player_id = p.player_id
        WHERE s.strike_rate > 120 AND s.matchtype = 'T20'
        ORDER BY s.strike_rate DESC
        LIMIT 10;
    """,

    "18 Matches Played per Year": """
        SELECT YEAR(FROM_UNIXTIME(start_date/1000)) AS year, COUNT(*) AS total_matches
        FROM Matches
        GROUP BY year
        ORDER BY year DESC;
    """,

    "19 Venues Hosting Most Matches": """
        SELECT v.ground, v.city, COUNT(m.match_id) AS matches_hosted
        FROM Venues v
        JOIN Matches m ON v.venue_id = m.venue_id
        GROUP BY v.ground, v.city
        ORDER BY matches_hosted DESC
        LIMIT 10;
    """,

    "20 Match Results Summary": """
        SELECT state, COUNT(*) AS total_matches
        FROM Matches
        GROUP BY state
        ORDER BY total_matches DESC;
    """,

    "21 Top Players by Ranking (All-Round)": """
        SELECT p.player_name, r.format, r.all_round_rank
        FROM Player_Rankings r
        JOIN Players p ON p.player_id = r.player_id
        WHERE r.all_round_rank IS NOT NULL
        ORDER BY r.all_round_rank ASC
        LIMIT 20;
    """,

    "22 Compare Players by Batting Average": """
        SELECT p.player_name, s.matchtype, s.batting_avg
        FROM Player_Stats_Summary s
        JOIN Players p ON s.player_id = p.player_id
        WHERE p.player_name IN ('Virat Kohli', 'Rohit Sharma', 'Joe Root', 'Babar Azam');
    """,

    "23 Top Strike Rate Players (T20)": """
        SELECT p.player_name, s.strike_rate
        FROM Player_Stats_Summary s
        JOIN Players p ON s.player_id = p.player_id
        WHERE s.matchtype = 'T20'
        ORDER BY s.strike_rate DESC
        LIMIT 10;
    """,

    "24 Average Wickets per Match (Bowler)": """
        SELECT p.player_name, s.matchtype, ROUND(s.wickets / s.matches, 2) AS wkts_per_match
        FROM Player_Stats_Summary s
        JOIN Players p ON s.player_id = p.player_id
        WHERE s.wickets > 0
        ORDER BY wkts_per_match DESC
        LIMIT 10;
    """,

    "25 Player vs Team Head-to-Head Stats": """
        SELECT p.player_name, r.opponent_team, AVG(r.score) AS avg_runs
        FROM Recent_Batting r
        JOIN Players p ON p.player_id = r.player_id
        GROUP BY p.player_name, r.opponent_team
        ORDER BY avg_runs DESC
        LIMIT 20;
    """

    
}


# Streamlit App

def app():
    st.set_page_config(page_title="SQL Analytics Dashboard", page_icon="📊", layout="wide")
    st.title("📊 Advanced SQL Analytics Dashboard")

    st.sidebar.header("Select a SQL Query")
    query_choice = st.sidebar.selectbox("Choose a query to run", list(queries.keys()))

    st.markdown(f"### {query_choice}")
    st.code(queries[query_choice], language="sql")

    if st.button("Run Query"):
        df = run_query(queries[query_choice])
        if not df.empty:
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("No results or query returned empty data.")
        

    st.markdown("---")
    st.caption(" 25 Cricket Database Insights")

if __name__ == "__main__":
    app()
