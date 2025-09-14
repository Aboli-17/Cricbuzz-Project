# pages/05_CRUD_Operations.py
import streamlit as st
import pandas as pd
from sqlalchemy import text
from utils.db_connection import get_engine

st.set_page_config(page_title="CRUD - Players", layout="wide")
st.title("⚙️ Player Management (CRUD)")

engine = get_engine(echo=False)

# Load players
def load_players():
    with engine.connect() as conn:
        return pd.read_sql("SELECT * FROM players", conn)

# Insert player
def insert_player(name, role, team_id):
    sql = text("INSERT INTO players (full_name, role, team_id) VALUES (:n,:r,:t)")
    with engine.begin() as conn:
        conn.execute(sql, {"n": name, "r": role, "t": team_id})

# Update player
def update_player(pid, name, role, team_id):
    sql = text("UPDATE players SET full_name=:n, role=:r, team_id=:t WHERE player_id=:id")
    with engine.begin() as conn:
        conn.execute(sql, {"id": pid, "n": name, "r": role, "t": team_id})

# Delete player
def delete_player(pid):
    sql = text("DELETE FROM players WHERE player_id=:id")
    with engine.begin() as conn:
        conn.execute(sql, {"id": pid})

# --- UI ---
st.subheader("➕ Add Player")
with st.form("add_form", clear_on_submit=True):
    name = st.text_input("Full Name")
    role = st.selectbox("Role", ["Batsman","Bowler","Allrounder","Wicketkeeper"])
    team_id = st.number_input("Team ID (from Teams table)", min_value=1, step=1)
    add_btn = st.form_submit_button("Add")
    if add_btn and name:
        insert_player(name, role, team_id)
        st.success("✅ Player added!")

st.markdown("---")

st.subheader("✏️ Edit / Delete Player")
df = load_players()
if df.empty:
    st.info("No players yet. Add some above or seed DB first.")
else:
    st.dataframe(df)
    ids = df["player_id"].tolist()
    pid = st.selectbox("Select Player ID", ids)
    player = df[df["player_id"]==pid].iloc[0]
    with st.form("edit_form"):
        new_name = st.text_input("Full Name", value=player["full_name"])
        new_role = st.selectbox("Role", ["Batsman","Bowler","Allrounder","Wicketkeeper"], index=["Batsman","Bowler","Allrounder","Wicketkeeper"].index(player["role"]) if player["role"] in ["Batsman","Bowler","Allrounder","Wicketkeeper"] else 0)
        new_team = st.number_input("Team ID", value=int(player["team_id"]), step=1)
        col1,col2 = st.columns(2)
        with col1:
            update_btn = st.form_submit_button("Update")
        with col2:
            delete_btn = st.form_submit_button("Delete")
        if update_btn:
            update_player(pid,new_name,new_role,new_team)
            st.success("✅ Updated!")
            st.experimental_rerun()
        if delete_btn:
            delete_player(pid)
            st.success("🗑️ Deleted!")
            st.experimental_rerun()

st.markdown("---")

st.subheader("⬇️ Export Players")
if not df.empty:
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Download as CSV", csv, "players.csv","text/csv")
