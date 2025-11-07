# utils/db_connection.py
import mysql.connector
import streamlit as st
import atexit

conn = None

@st.cache_resource(show_spinner=False)
def get_connection():
    global conn
    if conn is None or not conn.is_connected():
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root4782",
                password="root@July4782",
                database="cricbuzz"
            )           
        except mysql.connector.Error as err:
            st.error(f" Database connection failed: {err}")
            return None
    return conn
    

def cleanup_connections():
    global conn
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root4782",
            password="root@July4782",
            database="cricbuzz"
        )
        if conn.is_connected():
            conn.close()
    except Exception as e:
        print(f"Error closing connection: {e}")

atexit.register(cleanup_connections)
