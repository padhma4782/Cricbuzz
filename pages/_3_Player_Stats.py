# pages/_3_Player_Statistics.py
import streamlit as st
import requests
import pandas as pd

API_BASE = "https://cricbuzz-cricket.p.rapidapi.com"
HEADERS = {
    "x-rapidapi-key": "117991fd2cmsh65e8974e68cd0f5p1507e1jsn77433d6740b5",
    "x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
}

# Cache network calls
@st.cache_data(ttl=60)
def search_players_api(name: str):
    url = f"{API_BASE}/stats/v1/player/search"
    params = {"plrN": name}
    resp = requests.get(url, headers=HEADERS, params=params, timeout=10)
    if resp.status_code != 200:
        return {"error": f"Search API error {resp.status_code}: {resp.text}"}
    try:
        j = resp.json()
    except Exception as e:
        return {"error": f"Invalid JSON from search API: {e}"}

    # Common patterns: {"player": [...]} or direct list or {"players": [...]}
    if isinstance(j, dict):
        for key in ("player", "players", "data", "results"):
            if key in j and isinstance(j[key], list):
                return {"players": j[key]}
        # if dict contains direct list under unknown key, try to find first list
        for v in j.values():
            if isinstance(v, list):
                return {"players": v}
        return {"players": []}
    elif isinstance(j, list):
        return {"players": j}
    else:
        return {"players": []}

@st.cache_data(ttl=60)
def fetch_player_details(player_id: str):
    """Fetch full player details by player id."""
    url = f"{API_BASE}/stats/v1/player/{player_id}"
    resp = requests.get(url, headers=HEADERS, timeout=10)
    if resp.status_code != 200:
        return {"error": f"Player API error {resp.status_code}: {resp.text}"}
    try:
        return resp.json()
    except Exception as e:
        return {"error": f"Invalid JSON: {e}"}

def rows_to_df(section: dict):
    """Convert API rows/headers structure into a DataFrame if present."""
    if not section:
        return None
    headers = section.get("headers")
    rows = section.get("rows")
    if not headers or not rows:
        return None
    cols = headers
    data = []
    for r in rows:
        vals = r.get("values") if isinstance(r, dict) else r
        # if number of values doesn't match headers, pad/truncate
        if not isinstance(vals, list):
            vals = []
        if len(vals) < len(cols):
            vals = vals + [""] * (len(cols) - len(vals))
        if len(vals) > len(cols):
            vals = vals[: len(cols)]
        data.append(vals)
    return pd.DataFrame(data, columns=cols)

def safe_get(d, *keys, default=""):
    """Safe get nested simple: safe_get(d,'a','b') -> d.get('a',{}).get('b',default)"""
    cur = d
    for k in keys:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(k, default)
    return cur if cur is not None else default

def app():
    st.title(" Player Career / Recent Stats (Search by name)")

    q = st.text_input("Search player name (partial is ok):", value="", placeholder="e.g. Virat Kohli")
    if not q:
        st.info("Type a player name above to search the Cricbuzz player api.")
        return

    # Search
    search_result = search_players_api(q.strip())
    if "error" in search_result:
        st.error(search_result["error"])
        return

    players = search_result.get("players", [])
    if not players:
        st.warning("No players found for that name. Try a different query or broaden the name.")
        return

    # Build display 
    options = []
    id_map = {}
    for p in players:
        pid = p.get("id") or p.get("playerId") or p.get("player_id") or p.get("playerID")
        name = p.get("name") or p.get("playerName") or p.get("fullName") or "Unknown"
        country = p.get("country") or p.get("team") or p.get("countryName") or ""
        display = f"{name}" + (f" — {country}" if country else "")
        if pid:
            options.append(display)
            id_map[display] = str(pid)

    if not options:
        st.warning("Search returned results but no valid player IDs were found.")
        return

    selected = st.selectbox("Select player from results:", options)
    player_id = id_map[selected]

    # Fetch details
    with st.spinner("Fetching player details..."):
        details = fetch_player_details(player_id)

    if not details or "error" in details:
        st.error(details.get("error", "Failed to fetch player details."))
        return

    # Basic profile
    st.header(safe_get(details, "name", default="Unknown Player"))
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"**Role:** {safe_get(details, 'role', default='-')}")
        st.markdown(f"**Bat:** {safe_get(details, 'bat', default='-')}")
        st.markdown(f"**Bowl:** {safe_get(details, 'bowl', default='-')}")
        st.markdown(f"**Team:** {safe_get(details, 'intlTeam', default=safe_get(details, 'country', default='-'))}")
        st.markdown(f"**Born:** {safe_get(details, 'DoBFormat', default=safe_get(details, 'DoB', default='-'))}")
        teams = safe_get(details, "teams", default="")
        if teams:
            st.markdown(f"**Teams:** {teams}")
    with col2:
        img = safe_get(details, "image", default="")
        if img:
            st.image(img, use_column_width=True)

    st.markdown("---")

    # Recent batting
    df_bat = rows_to_df(details.get("recentBatting", {}))
    if df_bat is not None and not df_bat.empty:
        st.subheader("Recent Batting Performance")
        st.table(df_bat)
    else:
        st.info("No recent batting rows available for this player.")

    # Recent bowling
    df_bowl = rows_to_df(details.get("recentBowling", {}))
    if df_bowl is not None and not df_bowl.empty:
        st.subheader("Recent Bowling Performance")
        st.table(df_bowl)
    else:
        st.info("No recent bowling rows available for this player.")

    # Get Rankings
    rankings = details.get("rankings")
    if isinstance(rankings, dict):
        st.subheader("Rankings (if available)")
        # Flatten some useful ranking fields if present
        bat = rankings.get("bat", {})
        bowl = rankings.get("bowl", {})
        allr = rankings.get("all", {})
        ranking_rows = []
        if bat:
            ranking_rows.append({"Type": "Bat - ODI Rank", "Value": bat.get("odiRank") or bat.get("odiBestRank") or ""})
        if bowl:
            ranking_rows.append({"Type": "Bowl - T20 Best", "Value": bowl.get("t20BestRank", "")})
        if allr:
            ranking_rows.append({"Type": "All - T20 Best", "Value": allr.get("t20BestRank", "")})
        if ranking_rows:
            st.table(pd.DataFrame(ranking_rows))
    else:
        st.info("No ranking information available.")

    # Raw JSON toggle for debugging
    with st.expander("Show raw player JSON (debug)"):
        st.json(details)


if __name__ == "__main__":
    app()
