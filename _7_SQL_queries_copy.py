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
   
   "12 international team's performance": 
    """
    SELECT t.team_id,t.team_name,v.country AS venue_country,
    CASE 
        WHEN v.country = t.team_name THEN 'Home'
        ELSE 'Away'
    END AS match_location,
    COUNT(m.match_id) AS total_matches,
    SUM(CASE 
            WHEN m.status LIKE CONCAT('%', t.team_name, ' won%') THEN 1 
            ELSE 0 
        END) AS total_wins,
    ROUND(
        (SUM(CASE WHEN m.status LIKE CONCAT('%', t.team_name, ' won%') THEN 1 ELSE 0 END) / COUNT(m.match_id)) * 100, 
        2
    ) AS win_percentage
    FROM Matches m
    JOIN Teamsp t 
        ON t.team_id IN (m.team1_id, m.team2_id)
    JOIN Venues v 
        ON v.venue_id = m.venue_id
    WHERE t.is_international = 1
    GROUP BY t.team_id, t.team_name, match_location, v.country
    ORDER BY t.team_name, match_location;
    """,
    "13 batting partnerships of 100+ runs": 
    """
        SELECT b1.match_id,b1.innings_id,b1.player_id AS player1_id,p1.player_name AS player1_name,
        b2.player_id AS player2_id,p2.player_name AS player2_name,b1.runs + b2.runs AS partnership_runs
        FROM Batting_Scorecard b1
        JOIN Batting_Scorecard b2
            ON b1.match_id = b2.match_id
            AND b1.innings_id = b2.innings_id
            AND b2.batting_position = b1.batting_position + 1 
        JOIN Players p1 ON b1.player_id = p1.player_id
        JOIN Players p2 ON b2.player_id = p2.player_id
        WHERE (b1.runs + b2.runs) >= 100
        ORDER BY b1.match_id, b1.innings_id, partnership_runs DESC;
    """,
    "14 bowling performance at different venues": 
    """
        SELECT b.player_id,p.player_name,v.venue_id,v.ground AS venue_name,
            COUNT(DISTINCT b.match_id) AS matches_played,
            SUM(b.wickets_taken) AS total_wickets,
            ROUND(SUM(b.runs_conceded) / SUM(b.overs_bowled), 2) AS avg_economy_rate
        FROM Bowling_Scorecard b
        JOIN Players p ON b.player_id = p.player_id
        JOIN Venues v ON b.venue_id = v.venue_id
        WHERE b.overs_bowled >= 4  
        GROUP BY b.player_id, p.player_name, v.venue_id, v.ground
        ORDER BY avg_economy_rate ASC, total_wickets DESC;
    """,
    "15 Identify exceptional players in close matches": 
    """
       WITH Close_Matches AS (
            SELECT
            match_id,
            CASE
            WHEN status LIKE '%won by%' THEN TRIM(SUBSTRING_INDEX(status, ' won', 1))
            ELSE NULL
            END AS winning_team,
            CASE
            WHEN status LIKE '%won by%' AND status LIKE '%runs%' 
            THEN CAST(SUBSTRING_INDEX(SUBSTRING_INDEX(status, 'won by ', -1), ' runs', 1) AS UNSIGNED)
            WHEN status LIKE '%won by%' AND status LIKE '%wickets%'
            THEN CAST(SUBSTRING_INDEX(SUBSTRING_INDEX(status, 'won by ', -1), ' wickets', 1) AS UNSIGNED)
            ELSE NULL
            END AS margin_value,
            CASE
            WHEN status LIKE '%runs%' THEN 'runs'
            WHEN status LIKE '%wickets%' THEN 'wickets'
            ELSE NULL
            END AS margin_type
            FROM Matches
            WHERE status LIKE '%won by%'
        ),

    Filtered_Close AS (
    SELECT *
    FROM Close_Matches
    WHERE 
        (margin_type = 'runs' AND margin_value < 50)
        OR (margin_type = 'wickets' AND margin_value < 5)
    )

    SELECT
        p.player_name,
        COUNT(DISTINCT bs.match_id) AS close_matches_played,
        ROUND(AVG(bs.runs), 2) AS avg_runs_in_close_matches,
        SUM(CASE WHEN t.team_name = fc.winning_team THEN 1 ELSE 0 END) AS matches_won_when_batted
    FROM Batting_Scorecard bs
    JOIN Players p ON bs.player_id = p.player_id
    JOIN Matches m ON bs.match_id = m.match_id
    JOIN Teamsp t ON bs.team_id = t.team_id
    JOIN Filtered_Close fc ON bs.match_id = fc.match_id
    GROUP BY p.player_name
    HAVING close_matches_played > 0
    ORDER BY avg_runs_in_close_matches DESC;

    """,
    "16 players' batting performance over different years": 
    """
    WITH Player_Performance AS (
    SELECT
        p.player_id,
        p.player_name,
        YEAR(FROM_UNIXTIME(m.start_date / 1000)) AS match_year,
        bs.match_id,
        bs.runs,
        bs.balls,
        CASE 
            WHEN bs.balls > 0 THEN (bs.runs / bs.balls) * 100
            ELSE 0
        END AS strike_rate
    FROM Batting_Scorecard bs
    JOIN Players p ON bs.player_id = p.player_id
    JOIN Matches m ON bs.match_id = m.match_id
    WHERE YEAR(FROM_UNIXTIME(m.start_date / 1000)) >= 2020
    ),

    Aggregated_Stats AS (
    SELECT
        player_id,
        player_name,
        match_year,
        COUNT(DISTINCT match_id) AS matches_played,
        ROUND(AVG(runs), 2) AS avg_runs_per_match,
        ROUND(AVG(strike_rate), 2) AS avg_strike_rate
    FROM Player_Performance
    GROUP BY player_id, player_name, match_year
    )

    SELECT player_name,match_year,matches_played,avg_runs_per_match,avg_strike_rate
    FROM Aggregated_Stats
    -- WHERE matches_played >= 5
    ORDER BY player_name, match_year;
    """,
    
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
