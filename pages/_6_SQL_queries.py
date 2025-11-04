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
