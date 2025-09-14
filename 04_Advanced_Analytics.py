# 08_Advanced_Analytics.py
import streamlit as st
import pandas as pd
import plotly.express as px
from utils.db_connection import get_engine

st.set_page_config(page_title="Advanced Analytics", layout="wide")
st.title("📈 Advanced Analytics & KPIs")

engine = get_engine()

# --- Helper to safely run a single-value SQL query ---
def single_value(query):
    try:
        with engine.connect() as conn:
            df = pd.read_sql(query, conn)
            if df.shape[0] > 0:
                return int(df.iloc[0, 0])
    except Exception:
        return None
    return None

# ---------- KPIs row ----------
st.subheader("Key KPIs")
k1 = "SELECT COUNT(*) AS cnt FROM teams;"
k2 = "SELECT COUNT(*) AS cnt FROM players;"
k3 = "SELECT COUNT(*) AS cnt FROM matches;"
k4 = "SELECT COUNT(*) AS cnt FROM venues;"

teams_count = single_value(k1) or 0
players_count = single_value(k2) or 0
matches_count = single_value(k3) or 0
venues_count = single_value(k4) or 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("🏳️ Total Teams", teams_count)
col2.metric("👥 Total Players", players_count)
col3.metric("🏏 Total Matches", matches_count)
col4.metric("🏟️ Total Venues", venues_count)

st.markdown("---")

# ---------- Chart 1: Players by Role ----------
st.subheader("Players by Role")
try:
    query_roles = """
    SELECT role, COUNT(*) AS role_count
    FROM players
    GROUP BY role
    ORDER BY role_count DESC;
    """
    with engine.connect() as conn:
        df_roles = pd.read_sql(query_roles, conn)
    if df_roles.empty:
        st.info("No player-role data available.")
    else:
        st.dataframe(df_roles)

        # CSV download
        csv = df_roles.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Download as CSV",
            csv,
            "players_by_role.csv",
            "text/csv",
            key="download_roles"
        )

        fig = px.bar(df_roles, x="role", y="role_count", title="Players by Role", text="role_count")
        st.plotly_chart(fig, use_container_width=True)
except Exception as e:
    st.error(f"Error fetching players by role: {e}")

# ---------- Chart 2: Top Teams by Player Count ----------
st.subheader("Top Teams by Player Count (Top 5)")
try:
    query_top_teams = """
    SELECT t.name AS team_name, COUNT(p.player_id) AS player_count
    FROM players p
    JOIN teams t ON p.team_id = t.team_id
    GROUP BY t.name
    ORDER BY player_count DESC
    LIMIT 5;
    """
    with engine.connect() as conn:
        df_top_teams = pd.read_sql(query_top_teams, conn)
    if df_top_teams.empty:
        st.info("No team/player mapping found.")
    else:
        st.dataframe(df_top_teams)

        # CSV download
        csv = df_top_teams.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Download as CSV",
            csv,
            "top_teams.csv",
            "text/csv",
            key="download_top_teams"
        )

        fig = px.bar(df_top_teams, x="team_name", y="player_count",
                     title="Top Teams by Player Count",
                     text="player_count", color="team_name")
        st.plotly_chart(fig, use_container_width=True)
except Exception as e:
    st.error(f"Error fetching top teams: {e}")

# ---------- Chart 3: Matches per Year ----------
st.subheader("Matches per Year (Trend)")
try:
    with engine.connect() as conn:
        df_dates = pd.read_sql("SELECT match_id, date, description FROM matches;", conn)

    if df_dates.empty or "date" not in df_dates.columns:
        st.info("No match date data available.")
    else:
        df_dates["date_parsed"] = pd.to_datetime(df_dates["date"], errors="coerce")
        df_dates = df_dates.dropna(subset=["date_parsed"])
        if df_dates.empty:
            st.info("Match dates could not be parsed.")
        else:
            df_dates["year"] = df_dates["date_parsed"].dt.year
            counts = df_dates.groupby("year").size().reset_index(name="match_count").sort_values("year")
            st.dataframe(counts)

            # CSV download
            csv = counts.to_csv(index=False).encode("utf-8")
            st.download_button(
                "⬇️ Download as CSV",
                csv,
                "matches_per_year.csv",
                "text/csv",
                key="download_matches_per_year"
            )

            fig = px.line(counts, x="year", y="match_count", markers=True,
                          title="Matches per Year")
            st.plotly_chart(fig, use_container_width=True)

            # Date range filter
            min_date = df_dates["date_parsed"].min().date()
            max_date = df_dates["date_parsed"].max().date()

            start, end = st.date_input("📅 Filter by date range:", [min_date, max_date])

            mask = (df_dates["date_parsed"].dt.date >= start) & (df_dates["date_parsed"].dt.date <= end)
            filtered = df_dates.loc[mask]

            st.write(f"Matches between {start} and {end}:")
            st.dataframe(filtered[["match_id", "description", "date"]])
except Exception as e:
    st.error(f"Error fetching matches per year: {e}")

st.markdown("---")

# ---------- Chart 4: Top Venues by Matches ----------
st.subheader("Top Venues by Number of Matches (Top 5)")
try:
    query_venues = """
    SELECT v.name AS venue, v.city, v.country, COUNT(m.match_id) AS match_count
    FROM matches m
    JOIN venues v ON m.venue_id = v.venue_id
    GROUP BY v.name, v.city, v.country
    ORDER BY match_count DESC
    LIMIT 5;
    """
    with engine.connect() as conn:
        df_venues = pd.read_sql(query_venues, conn)
    if df_venues.empty:
        st.info("No venue/match data found.")
    else:
        st.dataframe(df_venues)

        # CSV download
        csv = df_venues.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Download as CSV",
            csv,
            "top_venues.csv",
            "text/csv",
            key="download_top_venues"
        )

        # Bar chart
        fig = px.bar(df_venues, x="venue", y="match_count",
                     title="Top Venues by Matches", text="match_count", color="venue")
        st.plotly_chart(fig, use_container_width=True)

        # Pie chart
        fig2 = px.pie(df_venues, names="venue", values="match_count", title="Top Venues by Matches (Pie)")
        st.plotly_chart(fig2, use_container_width=True)
except Exception as e:
    st.error(f"Error fetching top venues: {e}")

st.markdown("---")

# ---------- Quick SQL area ----------
st.subheader("📋 Quick Queries (copy/paste)")
st.write("Try these queries in the SQL Analytics page:")
st.code("""-- Top 5 teams by player count
SELECT t.name AS team_name, COUNT(p.player_id) AS player_count
FROM players p
JOIN teams t ON p.team_id = t.team_id
GROUP BY t.name
ORDER BY player_count DESC
LIMIT 5;

-- Matches in 2023
SELECT * FROM matches WHERE date LIKE '2023-%';
""")
