import streamlit as st
from pathlib import Path
from utils.db_connection import init_db, seed_sample_data, list_tables
import pandas as pd


st.title("🗄️ Database Setup")

st.write("Use the buttons below to initialize the SQLite database and add sample data.")

if st.button("Create / Initialize Database"):
    try:
        init_db()
        st.success("✅ Database initialized at data/cricbuzz.db")
        st.write("Tables created:")
        st.write(list_tables())
    except Exception as e:
        st.error(f"Initialization error: {e}")

if st.button("Seed Sample Data"):
    try:
        seed_sample_data()
        st.success("✅ Sample data inserted")
        st.write("Tables after seeding:")
        st.write(list_tables())
    except Exception as e:
        st.error(f"Seeding error: {e}")

# Show current files in data folder
data_dir = Path(__file__).resolve().parent.parent / "data"
st.write("📂 Data folder contents:")
if data_dir.exists():
    st.write([p.name for p in sorted(data_dir.iterdir())])
else:
    st.write("No data folder found.")



from utils.db_connection import get_engine
from sqlalchemy import text

if st.button("Show Sample Data"):
    try:
        engine = get_engine()
        with engine.connect() as conn:
            st.subheader("Teams")
            teams = pd.read_sql("SELECT * FROM teams", conn)
            st.dataframe(teams)

            st.subheader("Players")
            players = pd.read_sql("SELECT * FROM players", conn)
            st.dataframe(players)

            st.subheader("Venues")
            venues = pd.read_sql("SELECT * FROM venues", conn)
            st.dataframe(venues)

            st.subheader("Matches")
            matches = pd.read_sql("SELECT * FROM matches", conn)
            st.dataframe(matches)
    except Exception as e:
        st.error(f"Error showing data: {e}")