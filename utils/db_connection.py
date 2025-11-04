# utils/db_connection.py
import mysql.connector
import streamlit as st

@st.cache_resource(show_spinner=False)
def get_connection():
    """Create or reuse a cached MySQL connection."""
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root4782",
            password="root@July4782",
            database="cricbuzz"
        )
        if conn.is_connected():
            return conn
    except mysql.connector.Error as err:
        st.error(f" Database connection failed: {err}")
        return None
