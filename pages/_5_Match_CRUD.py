import streamlit as st
import mysql.connector
import pandas as pd
from utils.db_connection import get_connection



@st.cache_data(ttl=60)
def fetch_dropdown_data():
    conn = get_connection()
    if conn is None or not conn.is_connected():
        st.warning("Not connected to database...")
    try:
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT series_id, series_name FROM Series")
        series = cursor.fetchall()

        cursor.execute("SELECT team_id, team_name FROM teamsp")
        teams = cursor.fetchall()

        cursor.execute("SELECT venue_id, ground FROM Venues")
        venues = cursor.fetchall()
    except Exception as e:
            st.error(f"Error executing query: {e}") 
    finally:
        cursor.close()
       
    
    return series, teams, venues

@st.cache_data(ttl=60)
def fetch_all_matches():
    try:
        conn = get_connection()
        df = pd.read_sql("SELECT * FROM Matches", conn)
    except Exception as e:
            st.error(f"Error executing query: {e}") 
    return df

@st.cache_data(ttl=60)
def insert_match(data):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        sql = """
            INSERT INTO Matches 
            (match_id, series_id, match_desc, match_format, start_date, end_date, 
            state, status, team1_id, team2_id, venue_id, curr_bat_team_id, state_title)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """
        cursor.execute(sql, data)
    except Exception as e:
            st.error(f"Error executing query: {e}") 
    finally:
        cursor.close()
        conn.commit()



def update_match(data):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        sql = """
            UPDATE Matches SET 
                series_id=%s, match_desc=%s, match_format=%s, start_date=%s, end_date=%s,
                state=%s, status=%s, team1_id=%s, team2_id=%s, venue_id=%s, curr_bat_team_id=%s, state_title=%s
            WHERE match_id=%s
        """
        cursor.execute(sql, data)
    except Exception as e:
            st.error(f"Error executing query: {e}") 
    finally:
        cursor.close()
        conn.commit()


@st.cache_data(ttl=60)
def delete_match(match_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Matches WHERE match_id = %s", (match_id,))
    except Exception as e:
            st.error(f"Error executing query: {e}") 
    finally:
        cursor.close()
        conn.commit()


# UI

def app():
    st.title("Match Statistics CRUD Operations")

    st.sidebar.header("Select Operation")
    action = st.sidebar.radio("Action", ["Create", "Read", "Update", "Delete"])

    series, teams, venues = fetch_dropdown_data()

    if action == "Create":
        st.subheader(" Add New Match Record")

        with st.form("create_form"):
            match_id = st.number_input("Match ID", min_value=1, step=1)
            series_id = st.selectbox("Series", [s["series_name"] for s in series])
            match_desc = st.text_input("Match Description")
            match_format = st.selectbox("Match Format", ["Test", "ODI", "T20"])
            start_date = st.number_input("Start Date (epoch ms)", min_value=0)
            end_date = st.number_input("End Date (epoch ms)", min_value=0)
            state = st.text_input("State (e.g. Complete)")
            status = st.text_input("Status (e.g. India won by 5 wickets)")
            team1 = st.selectbox("Team 1", [t["team_name"] for t in teams])
            team2 = st.selectbox("Team 2", [t["team_name"] for t in teams])
            venue = st.selectbox("Venue", [v["ground"] for v in venues])
            curr_bat_team = st.selectbox("Current Batting Team", ["None"] + [t["team_name"] for t in teams])
            state_title = st.text_input("State Title")

            submitted = st.form_submit_button("Add Match")

            if submitted:
                # Map names back to IDs
                series_id_val = next(s["series_id"] for s in series if s["series_name"] == series_id)
                team1_id_val = next(t["team_id"] for t in teams if t["team_name"] == team1)
                team2_id_val = next(t["team_id"] for t in teams if t["team_name"] == team2)
                venue_id_val = next(v["venue_id"] for v in venues if v["ground"] == venue)
                curr_bat_team_id_val = 0 if curr_bat_team == "None" else next(t["team_id"] for t in teams if t["team_name"] == curr_bat_team)

                data = (match_id, series_id_val, match_desc, match_format, start_date, end_date,
                        state, status, team1_id_val, team2_id_val, venue_id_val, curr_bat_team_id_val, state_title)
                insert_match(data)
                st.success("Match record added successfully!")

    elif action == "Read":
        st.subheader("View All Matches")
        df = fetch_all_matches()
        st.dataframe(df)

    elif action == "Update":
        st.subheader("Update Match Record")

        df = fetch_all_matches()
        match_ids = df["match_id"].tolist()
        selected_id = st.selectbox("Select Match ID to Update", match_ids)

        match_row = df[df["match_id"] == selected_id].iloc[0]

        with st.form("update_form"):
            series_id = st.selectbox("Series", [s["series_name"] for s in series])
            match_desc = st.text_input("Match Description", value=match_row["match_desc"])
            match_format = st.text_input("Match Format", value=match_row["match_format"])
            start_date = st.number_input("Start Date", value=int(match_row["start_date"]))
            end_date = st.number_input("End Date", value=int(match_row["end_date"]))
            state = st.text_input("State", value=match_row["state"])
            status = st.text_input("Status", value=match_row["status"])
            team1 = st.selectbox("Team 1", [t["team_name"] for t in teams])
            team2 = st.selectbox("Team 2", [t["team_name"] for t in teams])
            venue = st.selectbox("Venue", [v["ground"] for v in venues])
            curr_bat_team = st.selectbox("Current Batting Team", ["None"] + [t["team_name"] for t in teams])
            state_title = st.text_input("State Title", value=match_row["state_title"])

            submitted = st.form_submit_button("Update Match")

            if submitted:
                series_id_val = next(s["series_id"] for s in series if s["series_name"] == series_id)
                team1_id_val = next(t["team_id"] for t in teams if t["team_name"] == team1)
                team2_id_val = next(t["team_id"] for t in teams if t["team_name"] == team2)
                venue_id_val = next(v["venue_id"] for v in venues if v["ground"] == venue)
                curr_bat_team_id_val = 0 if curr_bat_team == "None" else next(t["team_id"] for t in teams if t["team_name"] == curr_bat_team)

                data = (series_id_val, match_desc, match_format, start_date, end_date,
                        state, status, team1_id_val, team2_id_val, venue_id_val, curr_bat_team_id_val, state_title, selected_id)
                update_match(data)
                st.success("Match record updated successfully!")

    elif action == "Delete":
        st.subheader("Delete Match Record")

        df = fetch_all_matches()
        match_ids = df["match_id"].tolist()
        selected_id = st.selectbox("Select Match ID to Delete", match_ids)

        if st.button("Delete Match"):
            delete_match(selected_id)
            st.success(f"Match ID {selected_id} deleted successfully!")
    st.sidebar.markdown("⬅️ Use the sidebar to go back to the Home page.")



# Run app
if __name__ == "__main__":
    app()
