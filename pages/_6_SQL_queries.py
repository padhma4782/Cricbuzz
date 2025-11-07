import streamlit as st
import pandas as pd
from utils.db_connection import get_connection

#@st.cache_data(ttl=60)
def run_query(query):
    
    try:
        conn = get_connection()
        if conn is None or not conn.is_connected():
            st.error("No database connection available.")
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
        JOIN Teamsp t1 ON m.team1_id = t1.team_id
        JOIN Teamsp t2 ON m.team2_id = t2.team_id
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

    "17 Toss decision impact on match outcome": 
    """
        WITH Toss_Data AS (
            SELECT
                m.match_id,
                m.status,
                TRIM(SUBSTRING_INDEX(m.status, ' won', 1)) AS winning_team,
                m.toss_winner AS toss_winner_team,
                m.toss_decision AS toss_decision
            FROM Matches m
            WHERE m.status LIKE '%won by%' AND m.toss_winner IS NOT NULL
            ),
        Toss_Stats AS (
            SELECT
                toss_decision,
                COUNT(*) AS total_matches,
                SUM(CASE WHEN winning_team = toss_winner_team THEN 1 ELSE 0 END) AS toss_winner_won
            FROM Toss_Data
            GROUP BY toss_decision
        )
        SELECT
            toss_decision AS decision,
            total_matches,
            toss_winner_won,
            ROUND((toss_winner_won / total_matches) * 100, 2) AS win_percentage
        FROM Toss_Stats
        ORDER BY win_percentage DESC;
    """,
    "18 most economical bowlers": 
    """
        SELECT  
            p.player_id,
            p.player_name,
            COUNT(bs.match_id) AS matches_bowled,
            SUM(bs.overs_bowled) AS total_overs,
            SUM(bs.runs_conceded) AS total_runs_conceded,
            SUM(bs.wickets_taken) AS total_wickets,
            ROUND(SUM(bs.runs_conceded) / SUM(bs.overs_bowled), 2) AS economy_rate
        FROM Bowling_Scorecard bs
        JOIN Players p ON p.player_id = bs.player_id
        JOIN Matches m ON m.match_id = bs.match_id
        WHERE m.match_format IN ('ODI', 'T20')
        GROUP BY p.player_id, p.player_name
        HAVING 
            -- COUNT(bs.match_id) >= 10   AND                   -- at least 10 matches  
            (SUM(bs.overs_bowled) / COUNT(bs.match_id)) >= 2  -- bowled 2+ overs per match on avg
            AND SUM(bs.overs_bowled) > 0
        ORDER BY economy_rate ASC, total_wickets DESC;
    """,
    "19 batsmen are most consistent in their scoring": 
    """
    SELECT 
        p.player_id,
        p.player_name,
        COUNT(b.match_id) AS innings_played,
        AVG(b.runs) AS avg_runs,
        STDDEV(b.runs) AS stddev_runs
    FROM Batting_Scorecard b
    JOIN Players p ON p.player_id = b.player_id
    JOIN Matches m ON m.match_id = b.match_id
    WHERE b.balls >= 10          -- minimum balls faced per innings
    AND m.start_date >= UNIX_TIMESTAMP('2022-01-01') * 1000  -- matches since 2022
    GROUP BY p.player_id, p.player_name
    -- HAVING COUNT(b.match_id) >= 5      -- played at least 5 innings
    ORDER BY stddev_runs ASC, avg_runs DESC;

    """,
    "20 Player Match analysis": 
    """
       SELECT 
            p.player_id,
            p.player_name,

            /* Match counts */
            SUM(CASE WHEN s.matchtype = 'Test' THEN s.matches ELSE 0 END) AS test_matches,
            SUM(CASE WHEN s.matchtype = 'ODI' THEN s.matches ELSE 0 END) AS odi_matches,
            SUM(CASE WHEN s.matchtype = 'T20' THEN s.matches ELSE 0 END) AS t20_matches,

            /*  Batting averages */
            AVG(CASE WHEN s.matchtype = 'Test' THEN s.batting_avg END) AS test_batting_avg,
            AVG(CASE WHEN s.matchtype = 'ODI' THEN s.batting_avg END) AS odi_batting_avg,
            AVG(CASE WHEN s.matchtype = 'T20' THEN s.batting_avg END) AS t20_batting_avg

        FROM Players p
        LEFT JOIN Player_Stats_Summary s 
            ON p.player_id = s.player_id

        GROUP BY p.player_id, p.player_name

        HAVING 
            (test_matches + odi_matches + t20_matches) > 0   -- show players who played any format
        ORDER BY p.player_name;

    """,
    "21 Rank of Players Based on Combined Batting and Bowling Performance": 
    """
        WITH batting AS (
            SELECT
                player_id,
                SUM(runs) AS total_runs,
                AVG(batting_avg) AS avg_batting_avg,
                AVG(strike_rate) AS avg_strike_rate
            FROM Player_Stats_Summary
            GROUP BY player_id
        ),

        bowling_raw AS (
            SELECT
                player_id,
                SUM(runs_conceded) AS total_runs_conceded,
                SUM(overs_bowled) AS total_overs_bowled,
                SUM(wickets_taken) AS total_wickets
            FROM Bowling_Scorecard
            GROUP BY player_id
        ),

        bowling AS (
            SELECT
                player_id,
                total_wickets,
                CASE 
                    WHEN total_overs_bowled > 0 
                    THEN total_runs_conceded / total_overs_bowled
                    ELSE NULL
                END AS economy_rate
            FROM bowling_raw
        ),

        bowling_avg AS (
            SELECT
                player_id,
                AVG(bowling_avg) AS avg_bowling_avg
            FROM Player_Stats_Summary
            GROUP BY player_id
        ),

        joined AS (
            SELECT
                p.player_id,
                p.player_name,

                -- Batting fields
                b.total_runs,
                b.avg_batting_avg,
                b.avg_strike_rate,

                -- Bowling fields
                br.total_wickets,
                ba.avg_bowling_avg,
                br.economy_rate

            FROM Players p
            LEFT JOIN batting b ON b.player_id = p.player_id
            LEFT JOIN bowling br ON br.player_id = p.player_id
            LEFT JOIN bowling_avg ba ON ba.player_id = p.player_id
        )

        SELECT
            player_id,
            player_name,
            total_runs,
            avg_batting_avg,
            avg_strike_rate,
            total_wickets,
            avg_bowling_avg,
            economy_rate,

            /* Batting Score */
            (COALESCE(total_runs,0) * 0.01) +
            (COALESCE(avg_batting_avg,0) * 0.5) +
            (COALESCE(avg_strike_rate,0) * 0.3) AS batting_points,

            /* Bowling Score */
            (COALESCE(total_wickets,0) * 2) +
            ((50 - COALESCE(avg_bowling_avg,50)) * 0.5) +
            ((6 - COALESCE(economy_rate,6)) * 2) AS bowling_points,

            /* Final Score (Batting + Bowling) */
            (
                (COALESCE(total_runs,0) * 0.01) +
                (COALESCE(avg_batting_avg,0) * 0.5) +
                (COALESCE(avg_strike_rate,0) * 0.3) +
                (COALESCE(total_wickets,0) * 2) +
                ((50 - COALESCE(avg_bowling_avg,50)) * 0.5) +
                ((6 - COALESCE(economy_rate,6)) * 2)
            ) AS final_score

        FROM joined
        ORDER BY final_score DESC;

    """,
     "23 Player Form": 
    """
    WITH last_10 AS (
    SELECT 
        rb.player_id,
        rb.match_id,
        CAST(SUBSTRING_INDEX(rb.score, '(', 1) AS UNSIGNED) AS runs,
        bs.balls,
        (CAST(SUBSTRING_INDEX(rb.score, '(', 1) AS UNSIGNED) / bs.balls) * 100 AS strike_rate
    FROM Recent_Batting rb
    JOIN Batting_Scorecard bs 
        ON rb.player_id = bs.player_id AND rb.match_id = bs.match_id
    ),
    ranked AS (
        SELECT *,
            ROW_NUMBER() OVER (PARTITION BY player_id ) AS rn
        FROM last_10
    ),
    filtered AS (
        SELECT * FROM ranked WHERE rn <= 10
    ),

    agg_summary AS (
        SELECT 
            player_id,
            AVG(CASE WHEN rn <= 5 THEN runs END) AS avg_last_5,
            AVG(runs) AS avg_last_10,
            AVG(strike_rate) AS avg_strike_rate,
            SUM(CASE WHEN runs >= 50 THEN 1 ELSE 0 END) AS fifties_last_10,
            STDDEV(runs) AS consistency_stddev
        FROM filtered
        GROUP BY player_id
    ),

    categorized AS (
        SELECT 
            a.player_id,
            a.avg_last_5,
            a.avg_last_10,
            a.avg_strike_rate,
            a.fifties_last_10,
            a.consistency_stddev,

            CASE 
                WHEN a.avg_last_5 >= 60 AND a.avg_last_10 >= 50 AND a.consistency_stddev <= 15 THEN 'Excellent Form'
                WHEN a.avg_last_5 >= 40 AND a.avg_last_10 >= 35 THEN 'Good Form'
                WHEN a.avg_last_5 BETWEEN 25 AND 40 THEN 'Average Form'
                ELSE 'Poor Form'
            END AS form_status
        FROM agg_summary a
    )

    SELECT 
        p.player_name,
        c.*
    FROM categorized c
    JOIN Players p ON c.player_id = p.player_id
    ORDER BY c.avg_last_5 DESC;

    """,
    "24 Partnership Analysis": 
    """
     WITH partnerships AS (
    SELECT
        b1.match_id,
        b1.innings_id,
        b1.player_id AS player1_id,
        p1.player_name AS player1_name,
        b2.player_id AS player2_id,
        p2.player_name AS player2_name,
        (b1.runs + b2.runs) AS partnership_runs
    FROM Batting_Scorecard b1
    JOIN Batting_Scorecard b2 
        ON b1.match_id = b2.match_id
        AND b1.innings_id = b2.innings_id
        AND b2.batting_position = b1.batting_position + 1  -- consecutive batsmen
    JOIN Players p1 ON b1.player_id = p1.player_id
    JOIN Players p2 ON b2.player_id = p2.player_id
        ),

        agg AS (
            SELECT
                player1_id,
                player2_id,
                player1_name,
                player2_name,
                COUNT(*) AS partnership_count,
                AVG(partnership_runs) AS avg_partnership_runs,
                SUM(CASE WHEN partnership_runs >= 50 THEN 1 ELSE 0 END) AS fifty_plus_count,
                MAX(partnership_runs) AS highest_partnership,
                (SUM(CASE WHEN partnership_runs >= 50 THEN 1 ELSE 0 END) / COUNT(*)) * 100
                    AS success_rate
            FROM partnerships
            GROUP BY 
                player1_id, player2_id, 
                player1_name, player2_name
        ),

        ranked AS (
            SELECT *,
                DENSE_RANK() OVER (ORDER BY success_rate DESC, avg_partnership_runs DESC) AS partnership_rank
            FROM agg
        )

        SELECT *
        FROM ranked
        ORDER BY partnership_rank, success_rate DESC;

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
