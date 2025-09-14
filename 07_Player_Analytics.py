# pages/11_Player_Analytics.py
import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import text
from utils.db_connection import get_engine

st.set_page_config(page_title="Player Analytics", layout="wide")
st.title("📊 Player Analytics")

engine = get_engine(echo=False)

# ----------------------------
# DB helper functions
# ----------------------------
def load_players():
    with engine.connect() as conn:
        return pd.read_sql("SELECT * FROM players", conn)

def insert_stats(player_id, matches, runs):
    sql = text("UPDATE players SET matches=:m, runs=:r WHERE player_id=:id")
    with engine.begin() as conn:
        conn.execute(sql, {"id": player_id, "m": matches, "r": runs})

# ----------------------------
# Add Stats Form
# ----------------------------
st.subheader("➕ Add/Update Player Stats")

df = load_players()
if df.empty:
    st.warning("No players found. Please add players in CRUD page first.")
else:
    pid = st.selectbox("Select Player", df["player_id"])
    player = df[df["player_id"] == pid].iloc[0]

    with st.form("stats_form", clear_on_submit=True):
        matches = st.number_input("Matches", min_value=0, step=1, value=int(player.get("matches", 0)) if "matches" in df.columns else 0)
        runs = st.number_input("Runs", min_value=0, step=1, value=int(player.get("runs", 0)) if "runs" in df.columns else 0)
        submit = st.form_submit_button("Save Stats")
        if submit:
            insert_stats(pid, matches, runs)
            st.success(f"✅ Stats updated for {player['full_name']}!")

st.markdown("---")

# ----------------------------
# Show Analytics
# ----------------------------
st.subheader("📈 Runs vs Matches")

# Reload players after update
df = load_players()

if "matches" not in df.columns or "runs" not in df.columns:
    st.info("No stats available yet. Please add Matches and Runs.")
else:
    st.dataframe(df[["player_id", "full_name", "matches", "runs"]])

    if not df.empty:
        fig = px.scatter(df, x="matches", y="runs", text="full_name",
                         size="runs", color="team_id",
                         title="Player Performance: Runs vs Matches")
        fig.update_traces(textposition="top center")
        st.plotly_chart(fig, use_container_width=True)
