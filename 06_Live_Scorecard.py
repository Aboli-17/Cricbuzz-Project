# pages/10_Live_Scorecard.py
import streamlit as st
import pandas as pd
import plotly.express as px
from utils.db_connection import get_engine
from sqlalchemy import text

# make layout wide for nicer screenshots
st.set_page_config(page_title="Live Scorecard", layout="wide")

# ----------------------------
# Sample / placeholder data (keeps the page usable even if API/DB data missing)
# ----------------------------
sample_data = {
    "team1": {"name": "India", "score": "250/6"},
    "team2": {"name": "Australia", "score": "248/8"},
    "batters": [
        {"name": "Virat Kohli", "runs": 82, "balls": 65},
        {"name": "Rohit Sharma", "runs": 45, "balls": 33}
    ],
    "bowlers": [
        {"name": "Pat Cummins", "overs": 8, "runs": 40, "wickets": 2},
        {"name": "Mitchell Starc", "overs": 10, "runs": 55, "wickets": 1}
    ],
    "progression": [10, 45, 120, 180, 220, 250]
}

st.markdown("## 🏏 Live Scorecard")
st.write("")  # small spacer

# ----------------------------
# Centered match metrics at the top
# ----------------------------
top_cols = st.columns([1, 2, 2, 1])
with top_cols[1]:
    st.metric(label=sample_data["team1"]["name"], value=sample_data["team1"]["score"])
with top_cols[2]:
    st.metric(label=sample_data["team2"]["name"], value=sample_data["team2"]["score"])

# ----------------------------
# Top: Current Batters (left) and Bowler Stats (right) — equal widths and top-aligned
# ----------------------------
col_batters, col_bowlers = st.columns([6, 6])

with col_batters:
    st.markdown("### 👤 Current Batters")
    if sample_data.get("batters"):
        batters_df = pd.DataFrame(sample_data["batters"])
        # compute strike rate safely
        batters_df["SR"] = ((batters_df["runs"] / batters_df["balls"]) * 100).round(2)
        batters_df_display = batters_df[["name", "runs", "balls", "SR"]].reset_index(drop=True)
        st.table(batters_df_display)  # table auto-sizes and avoids scrolling
    else:
        st.info("No batter data available.")

with col_bowlers:
    st.markdown("### 🎯 Bowler Stats")
    if sample_data.get("bowlers"):
        bowlers_df = pd.DataFrame(sample_data["bowlers"])
        bowlers_df_display = bowlers_df[["name", "overs", "runs", "wickets"]].reset_index(drop=True)
        st.table(bowlers_df_display)
    else:
        st.info("No bowler data available.")

st.write("")  # spacer

# ----------------------------
# Below the batters/bowlers: Quick Player Analytics (left) and Runs Progression (right)
# ----------------------------
left_col, right_col = st.columns([6, 6])

engine = get_engine(echo=False)

def load_players():
    """Return a DataFrame with players if available; otherwise empty df with expected cols."""
    try:
        with engine.connect() as conn:
            df = pd.read_sql("SELECT player_id, full_name, matches, runs FROM players", conn)
            # ensure columns exist
            for c in ["player_id", "full_name", "matches", "runs"]:
                if c not in df.columns:
                    df[c] = None
            return df
    except Exception:
        # If DB missing or table not present, return empty frame
        return pd.DataFrame(columns=["player_id", "full_name", "matches", "runs"])

def update_stats(player_id, matches, runs):
    try:
        sql = text("UPDATE players SET matches = :m, runs = :r WHERE player_id = :id")
        with engine.begin() as conn:
            conn.execute(sql, {"id": int(player_id), "m": int(matches), "r": int(runs)})
        return True
    except Exception as e:
        st.error(f"Error saving stats: {e}")
        return False

# LEFT: Quick Player Analytics form (compact)
with left_col:
    st.markdown("### 📊 Quick Player Analytics")
    df_players = load_players()
    if df_players.empty:
        st.info("No players found in DB. Add players on CRUD page first.")
    else:
        player_names = df_players["full_name"].astype(str).tolist()
        selected_name = st.selectbox("Select Player", player_names)
        selected_row = df_players[df_players["full_name"] == selected_name].iloc[0]

        # inline small inputs
        a, b, c = st.columns([3, 2, 1])
        with a:
            matches = st.number_input(
                "Matches",
                min_value=0,
                step=1,
                value=int(selected_row["matches"]) if pd.notnull(selected_row["matches"]) else 0
            )
        with b:
            runs = st.number_input(
                "Runs",
                min_value=0,
                step=1,
                value=int(selected_row["runs"]) if pd.notnull(selected_row["runs"]) else 0
            )
        with c:
            # small inline button
            if st.button("Save"):
                ok = update_stats(selected_row["player_id"], matches, runs)
                if ok:
                    st.success(f"Saved: {selected_name}")

# RIGHT: Runs Progression line chart (compact height)
with right_col:
    st.markdown("### 📈 Runs Progression")
    overs = list(range(1, len(sample_data["progression"]) + 1))
    fig = px.line(x=overs, y=sample_data["progression"], markers=True, labels={"x": "Overs", "y": "Runs"})
    fig.update_layout(height=260, margin=dict(l=10, r=10, t=20, b=10))
    st.plotly_chart(fig, use_container_width=True)



