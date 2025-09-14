import streamlit as st
import pandas as pd
from utils.db_connection import get_engine

st.set_page_config(page_title="SQL Analytics", layout="wide")
st.title("📊 SQL Analytics")

engine = get_engine()

# ---------------------------
# BEGIN: SQL Practice — Beginner Q1 to Q5 (fixed for your schema)
# ---------------------------

st.markdown("## 🧮 SQL Practice — Beginner (Q1–Q5)")
st.caption("Click any button below to run that SQL query against the local DB (`data/cricbuzz.db`).")

def run_query(label, query):
    st.markdown(f"**{label}**")
    try:
        with engine.connect() as conn:
            df = pd.read_sql(query, conn)
        if df.empty:
            st.info("Query ran successfully but returned no rows.")
        else:
            st.dataframe(df)
    except Exception as e:
        st.error(f"Error running query: {e}")

# Q1 - Players who represent India
if st.button("Q1 — Players representing India"):
    query = """
    SELECT full_name, role, batting_style, bowling_style
    FROM players p
    JOIN teams t ON p.team_id = t.team_id
    WHERE t.country = 'India';
    """
    run_query("Q1 — Players representing India", query)


# Q2 - Top 10 highest run scorers
if st.button("Q2 — Top 10 run scorers"):
    query = """
    SELECT full_name, runs,
           CASE WHEN matches = 0 THEN NULL ELSE ROUND(runs * 1.0 / matches, 2) END AS batting_avg
    FROM players
    ORDER BY runs DESC
    LIMIT 10;
    """
    run_query("Q2 — Top 10 run scorers", query)


# Q3 - Matches won by each team
if st.button("Q3 — Matches won by each team"):
    query = """
    SELECT t.name AS team_name, COUNT(*) AS wins
    FROM matches m
    JOIN teams t ON m.winner_id = t.team_id
    GROUP BY t.name
    ORDER BY wins DESC;
    """
    run_query("Q3 — Matches won by each team", query)

# Q4 - Count of players per role
if st.button("Q4 — Count players per role"):
    query = """
    SELECT role, COUNT(*) AS total_players
    FROM players
    GROUP BY role
    ORDER BY total_players DESC;
    """
    run_query("Q4 — Count players per role", query)

# Q5 - Highest runs scored by any player
if st.button("Q5 — Highest run scorer overall"):
    query = """
    SELECT full_name, MAX(runs) AS max_runs
    FROM players;
    """
    run_query("Q5 — Highest run scorer overall", query)



# ---------------------------
# END: Beginner Q1–Q5
# ---------------------------

# ---------------------------
# BEGIN: SQL Practice — Intermediate Q6 to Q12 (fixed for your schema)
# ---------------------------

st.markdown("## 🧮 SQL Practice — Intermediate (Q6–Q12)")


# Q6 - Last 20 completed matches
if st.button("Q6 — Last 20 completed matches"):
    query = """
    SELECT m.description,
           t1.name AS team1,
           t2.name AS team2,
           w.name AS winner,
           v.name AS venue,
           m.date
    FROM matches m
    LEFT JOIN teams t1 ON m.team1_id = t1.team_id
    LEFT JOIN teams t2 ON m.team2_id = t2.team_id
    LEFT JOIN teams w ON m.winner_id = w.team_id
    LEFT JOIN venues v ON m.venue_id = v.venue_id
    ORDER BY date(m.date) DESC
    LIMIT 20;
    """
    run_query("Q6 — Last 20 completed matches", query)

# Q7 - Player runs across formats (simplified — no format column, so just show runs & matches)
if st.button("Q7 — Player performance summary"):
    query = """
    SELECT full_name, runs, matches,
           CASE WHEN matches = 0 THEN NULL ELSE ROUND(runs * 1.0 / matches, 2) END AS avg_runs_per_match
    FROM players
    ORDER BY runs DESC
    LIMIT 20;
    """
    run_query("Q7 — Player performance summary", query)

# Q8 - Team wins grouped by country (home vs away cannot be checked without match country, simplified)
if st.button("Q8 — Wins by team (simplified)"):
    query = """
    SELECT t.country, COUNT(*) AS total_wins
    FROM matches m
    JOIN teams t ON m.winner_id = t.team_id
    GROUP BY t.country
    ORDER BY total_wins DESC;
    """
    run_query("Q8 — Wins by team (simplified)", query)

# Q9 - Partnerships (not possible without ball-by-ball data, so show top 20 players by runs instead)
if st.button("Q9 — Top 20 players by runs (partnership proxy)"):
    query = """
    SELECT full_name, runs, matches
    FROM players
    ORDER BY runs DESC
    LIMIT 20;
    """
    run_query("Q9 — Top 20 players by runs", query)

# Q10 - Bowling performance (no overs/wickets data in schema, so just show matches played per venue)
if st.button("Q10 — Matches played per venue"):
    query = """
    SELECT v.name AS venue, v.city, COUNT(m.match_id) AS matches_played
    FROM matches m
    JOIN venues v ON m.venue_id = v.venue_id
    GROUP BY v.name, v.city
    ORDER BY matches_played DESC;
    """
    run_query("Q10 — Matches played per venue", query)

# Q11 - Close matches (simplified — show last 10 matches only)
if st.button("Q11 — Last 10 matches (close match proxy)"):
    query = """
    SELECT m.description, m.date,
           t1.name AS team1, t2.name AS team2,
           w.name AS winner
    FROM matches m
    LEFT JOIN teams t1 ON m.team1_id = t1.team_id
    LEFT JOIN teams t2 ON m.team2_id = t2.team_id
    LEFT JOIN teams w ON m.winner_id = w.team_id
    ORDER BY date(m.date) DESC
    LIMIT 10;
    """
    run_query("Q11 — Last 10 matches (close match proxy)", query)

# Q12 - Player yearly performance (not possible without year-by-year runs, so just show all players sorted by runs)
if st.button("Q12 — All players sorted by runs"):
    query = """
    SELECT full_name, runs, matches
    FROM players
    ORDER BY runs DESC;
    """
    run_query("Q12 — All players sorted by runs", query)

# ---------------------------
# END: Intermediate Q6–Q12
# ---------------------------

# ---------------------------
# BEGIN: SQL Practice — Advanced Q13 to Q21 (adapted for schema)
# ---------------------------

st.markdown("## 🧮 SQL Practice — Advanced (Q13–Q21)")

# Q13 - Toss vs match outcome (simplified: show winner counts only)
if st.button("Q13 — Match wins by team (toss proxy)"):
    query = """
    SELECT t.name AS team_name, COUNT(*) AS total_wins
    FROM matches m
    JOIN teams t ON m.winner_id = t.team_id
    GROUP BY t.name
    ORDER BY total_wins DESC;
    """
    run_query("Q13 — Match wins by team", query)

# Q14 - Most economical bowlers (no bowling data, so show top players by matches played)
if st.button("Q14 — Top players by matches played"):
    query = """
    SELECT full_name, matches, runs
    FROM players
    ORDER BY matches DESC
    LIMIT 10;
    """
    run_query("Q14 — Top players by matches played", query)

# Q15 - Consistency in scoring (approx: show runs per match for each player)
if st.button("Q15 — Player runs per match (consistency proxy)"):
    query = """
    SELECT full_name, runs, matches,
           CASE WHEN matches = 0 THEN NULL ELSE ROUND(runs * 1.0 / matches, 2) END AS avg_runs_per_match
    FROM players
    ORDER BY avg_runs_per_match DESC
    LIMIT 15;
    """
    run_query("Q15 — Player runs per match", query)

# Q16 - Matches per player (simplified to players sorted by matches)
if st.button("Q16 — Players sorted by matches played"):
    query = """
    SELECT full_name, matches, runs
    FROM players
    ORDER BY matches DESC
    LIMIT 20;
    """
    run_query("Q16 — Players sorted by matches", query)

# Q17 - Performance ranking system (simplified weighted score using runs + matches only)
if st.button("Q17 — Player performance ranking (simplified)"):
    query = """
    SELECT full_name,
           runs,
           matches,
           (runs * 0.1 + matches * 0.5) AS performance_score
    FROM players
    ORDER BY performance_score DESC
    LIMIT 20;
    """
    run_query("Q17 — Player performance ranking", query)

# Q18 - Head-to-head matches (show count of matches played between team pairs)
if st.button("Q18 — Head-to-head team match counts"):
    query = """
    SELECT t1.name AS team1, t2.name AS team2, COUNT(*) AS matches_played
    FROM matches m
    JOIN teams t1 ON m.team1_id = t1.team_id
    JOIN teams t2 ON m.team2_id = t2.team_id
    GROUP BY t1.name, t2.name
    ORDER BY matches_played DESC
    LIMIT 20;
    """
    run_query("Q18 — Head-to-head match counts", query)

# Q19 - Recent player form (simplified: show top 10 run scorers)
if st.button("Q19 — Top 10 run scorers (form proxy)"):
    query = """
    SELECT full_name, runs, matches
    FROM players
    ORDER BY runs DESC
    LIMIT 10;
    """
    run_query("Q19 — Top 10 run scorers", query)

# Q20 - Successful batting partnerships (not possible, so show top 10 players by runs as proxy)
if st.button("Q20 — Top 10 players by runs (partnership proxy)"):
    query = """
    SELECT full_name, runs, matches
    FROM players
    ORDER BY runs DESC
    LIMIT 10;
    """
    run_query("Q20 — Top 10 players by runs", query)

# Q21 - Time-series analysis (not possible, so show all players ordered by matches)
if st.button("Q21 — Player career progression (proxy by matches)"):
    query = """
    SELECT full_name, runs, matches
    FROM players
    ORDER BY matches DESC
    LIMIT 20;
    """
    run_query("Q21 — Player career progression (proxy)", query)

# ---------------------------
# END: Advanced Q13–Q21
# ---------------------------









