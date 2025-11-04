import streamlit as st

st.set_page_config(page_title='Cricbuzz LiveStats', layout='wide')
st.title('Cricbuzz LiveStats — Cricket Analytics Dashboard')
st.sidebar.title('Navigation')
page = st.sidebar.selectbox('Go to', ['Home', 'Live Matches','Player Stats', 'Match_CRUD','Player_CRUD','SQL Queries' ])

if page == 'Home':
    from pages._1_HOME  import app as home_app
    home_app()
elif page == 'Live Matches':
    from pages._2_Live_Matches import app as live_app
    live_app()
elif page == 'Player Stats':
    from pages._3_Player_Stats import app as player_app
    player_app()
elif page == 'Match_CRUD':
    from pages._5_Match_CRUD import app as crud_app
    crud_app()
elif page == 'Player_CRUD':
    from pages._4_Player_CRUD import app as playercrud_app
    playercrud_app()
elif page == 'SQL Queries':
    from pages._6_SQL_queries import app as sql_app
    sql_app()
