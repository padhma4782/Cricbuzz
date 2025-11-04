import streamlit as st
import mysql.connector
import pandas as pd
from utils.db_connection import get_connection

@st.cache_data(ttl=60)
def run_query(query, params=None, fetch=False):
    conn = get_connection()
    if conn is None or not conn.is_connected():
        st.warning(" Reconnecting to database...")
        conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())
        data = cursor.fetchall() if fetch else None
    except mysql.connector.Error as err:
        st.error(f"Database error: {err}")
    finally:
        if conn and conn.is_connected():
            conn.commit()
            cursor.close()
            #conn.close()    
    return data

# ---------------------- CREATE Operation ----------------------
def create_player():
    st.subheader("Add New Player")

    with st.form("add_player_form"):
        player_id = st.text_input("Player ID")
        player_name = st.text_input("Player Name")
        nick_name = st.text_input("Nickname")
        role = st.text_input("Role")
        intl_team = st.text_input("International Team")
        batting_style = st.text_input("Batting Style")
        bowling_style = st.text_input("Bowling Style")
        dob = st.date_input("Date of Birth")
        height = st.text_input("Height (e.g., 175 cm)")
        image_url = st.text_input("Image URL")

        submitted = st.form_submit_button("Add Player")

        if submitted:
            query = """
                INSERT INTO Players (player_id,player_name, nick_name, role, intl_team, batting_style,
                bowling_style, dob, height, image_url)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """
            run_query(query, (player_id,player_name, nick_name, role, intl_team, batting_style,
                              bowling_style, dob, height, image_url))
            st.success(f"Player '{player_name}' added successfully!")

# ---------------------- READ Operation ----------------------
def view_players():
    st.subheader("View Players and Related Data")

    players = run_query("SELECT * FROM Players", fetch=True)
    if players:
        df = pd.DataFrame(players)
        st.dataframe(df)
    else:
        st.info("No players found in the database.")

# ---------------------- UPDATE Operation ----------------------
def update_player():
    st.subheader("Update Player Details")

    players = run_query("SELECT player_id, player_name FROM Players", fetch=True)
    player_dict = {p['player_name']: p['player_id'] for p in players}

    selected_player = st.selectbox("Select Player to Update", list(player_dict.keys()))

    if selected_player:
        pid = player_dict[selected_player]
        player_data = run_query("SELECT * FROM Players WHERE player_id=%s", (pid,), fetch=True)[0]

        with st.form("update_form"):
            player_name = st.text_input("Player Name", player_data['player_name'])
            role = st.text_input("Role", player_data['role'])
            intl_team = st.text_input("International Team", player_data['intl_team'])
            batting_style = st.text_input("Batting Style", player_data['batting_style'])
            bowling_style = st.text_input("Bowling Style", player_data['bowling_style'])
            image_url = st.text_input("Image URL", player_data['image_url'])

            update = st.form_submit_button("Update Player")

            if update:
                query = """
                    UPDATE Players SET player_name=%s, role=%s, intl_team=%s,
                    batting_style=%s, bowling_style=%s, image_url=%s
                    WHERE player_id=%s
                """
                run_query(query, (player_name, role, intl_team, batting_style,
                                  bowling_style, image_url, pid))
                st.success(f"Player '{player_name}' updated successfully!")

# ---------------------- DELETE Operation ----------------------
def delete_player():
    st.subheader("Delete Player and Related Records")

    players = run_query("SELECT player_id, player_name FROM Players", fetch=True)
    player_dict = {p['player_name']: p['player_id'] for p in players}

    selected_player = st.selectbox("Select Player to Delete", list(player_dict.keys()))

    if selected_player:
        pid = player_dict[selected_player]

        if st.button(f" Delete '{selected_player}' from all related tables"):
            # Delete related records
            run_query("DELETE FROM Player_Teams WHERE player_id=%s", (pid,))
            run_query("DELETE FROM Player_Rankings WHERE player_id=%s", (pid,))
            run_query("DELETE FROM Recent_Batting WHERE player_id=%s", (pid,))
            run_query("DELETE FROM Recent_Bowling WHERE player_id=%s", (pid,))
            run_query("DELETE FROM Player_Stats_Summary WHERE player_id=%s", (pid,))
            run_query("DELETE FROM Players WHERE player_id=%s", (pid,))

            st.success(f"All records related to '{selected_player}' have been deleted.")

# ---------------------- MAIN APP ----------------------
def app():
    st.title("Player Stats Management (CRUD Operations)")

    menu = ["Create Player", "View Players", "Update Player", "Delete Player"]
    choice = st.sidebar.radio("Select Operation", menu)

    if choice == "Create Player":
        create_player()
    elif choice == "View Players":
        view_players()
    elif choice == "Update Player":
        update_player()
    elif choice == "Delete Player":
        delete_player()
st.sidebar.markdown("⬅️ Use the sidebar to go back to the Home page.")
if __name__ == "__main__":
    app()
