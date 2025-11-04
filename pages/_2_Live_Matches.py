import streamlit as st
import requests
import pandas as pd

#  API Headers
HEADERS = {
    "x-rapidapi-key": "117991fd2cmsh65e8974e68cd0f5p1507e1jsn77433d6740b5",
    "x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
}

# Fetch live matches from API
def get_live_matches():
    API_URL = "https://cricbuzz-cricket.p.rapidapi.com/matches/v1/live"
    response = requests.get(API_URL, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    return None

# Get match dropdown options including matchId
def get_match_list(data):
    match_options = []
    for type_match in data.get("typeMatches", []):
        match_type = type_match.get("matchType", "")
        for series_match in type_match.get("seriesMatches", []):
            series_data = series_match.get("seriesAdWrapper", {})
            series_name = series_data.get("seriesName", "")
            for match in series_data.get("matches", []):
                match_info = match.get("matchInfo", {})
                match_desc = (
                    f"{match_info.get('team1', {}).get('teamName', '')} vs "
                    f"{match_info.get('team2', {}).get('teamName', '')} "
                    f"({series_name} - {match_type})"
                )
                match_options.append((match_desc, match_info.get("matchId"), match))
    return match_options

# Converts basic match info into DataFrame for summary table
def match_to_table(selected_match):
    match_info = selected_match.get("matchInfo", {})
    match_score = selected_match.get("matchScore", {})

    team1 = match_info.get("team1", {})
    team2 = match_info.get("team2", {})
    team1_score_data = match_score.get("team1Score", {}).get("inngs1", {})
    team2_score_data = match_score.get("team2Score", {}).get("inngs1", {})

    def format_score(score_data):
        return (
            f"{score_data.get('runs', '')}/{score_data.get('wickets', '')} "
            f"({score_data.get('overs', '')} ov)"
            if score_data else "N/A"
        )

    table_data = {
        "Match Description": [match_info.get("matchDesc", "")],
        "Format": [match_info.get("matchFormat", "")],
        "Team 1": [team1.get("teamName", "")],
        "Team 1 Score": [format_score(team1_score_data)],
        "Team 2": [team2.get("teamName", "")],
        "Team 2 Score": [format_score(team2_score_data)],
        "Status": [match_info.get("status", "")],
        "Current State": [match_info.get("stateTitle", "")]
    }

    return pd.DataFrame(table_data)

#  Fetch full scorecard
def fetch_scard(match_id):
    url = f"https://cricbuzz-cricket.p.rapidapi.com/mcenter/v1/{match_id}/scard"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    return None

#  Parse batting details from an innings
def parse_batting(innings):
    batsmen = innings.get("batsman", [])
    data = []
    for player in batsmen:
        data.append({
            "Name": player.get("name", ""),
            "Runs": player.get("runs", ""),
            "Balls": player.get("balls", ""),
            "4s": player.get("fours", ""),
            "6s": player.get("sixes", ""),
            "SR": player.get("strkrate", ""),
            "Dismissal": player.get("outdec", "")
        })
    return pd.DataFrame(data)

#  Parse bowling details from an innings
def parse_bowling(innings):
    bowlers = innings.get("bowler", [])
    data = []
    for bowler in bowlers:
        data.append({
            "Name": bowler.get("name", ""),
            "Overs": bowler.get("overs", ""),
            "Maidens": bowler.get("maidens", ""),
            "Runs": bowler.get("runs", ""),
            "Wickets": bowler.get("wickets", ""),
            "Econ": bowler.get("economy", "")
        })
    return pd.DataFrame(data)

#  Create tab label as requested
def build_tab_label(innings, index):
    team = innings.get("batteamname", "Unknown Team")
    score = innings.get("score", "")
    wickets = innings.get("wickets", "")
    overs = innings.get("overs", "")
    return f"{team} - Innings {index+1} ({score}/{wickets} in {overs} overs)"

#  MAIN Streamlit App page
def app():
    st.title(" Live Cricket Matches")

    # Get live matches
    data = get_live_matches()
    if not data:
        st.error("Failed to fetch live match data.")
        return

    match_list = get_match_list(data)
    selected_match_desc = st.selectbox("Choose a match:", [m[0] for m in match_list])
    selected_mid, selected_match = next((m[1], m[2]) for m in match_list if m[0] == selected_match_desc)

    # Display match summary
    st.write("### 📊 Match Summary")
    st.table(match_to_table({"matchInfo": selected_match.get("matchInfo", {}), "matchScore": selected_match.get("matchScore", {})}))

    # Fetch detailed scorecard
    scard = fetch_scard(selected_mid)
    if not scard or "scorecard" not in scard:
        st.warning("No scorecard available for this match.")
        return

    innings_list = scard["scorecard"]
    tabs = st.tabs([build_tab_label(inn, idx) for idx, inn in enumerate(innings_list)])

    for idx, inn in enumerate(innings_list):
        with tabs[idx]:
            st.subheader("Batting")
            st.table(parse_batting(inn))

            st.subheader("Bowling")
            st.table(parse_bowling(inn))
