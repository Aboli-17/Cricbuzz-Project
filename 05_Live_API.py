# 09_Live_API.py (clean version - no Live Toggle, no Top Performers)
import streamlit as st
import requests
import os
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
RAPID_API_KEY = os.getenv("RAPID_API_KEY")
RAPID_API_HOST = os.getenv("RAPID_API_HOST", "cricbuzz-cricket.p.rapidapi.com")

st.set_page_config(page_title="Live Cricket API", layout="wide")
st.title("🏏 Live Cricbuzz API Data")

if not RAPID_API_KEY:
    st.error("⚠️ RapidAPI Key not found. Please check your .env file.")
else:
    st.success("✅ Connected to RapidAPI")

    url = f"https://{RAPID_API_HOST}/matches/v1/recent"
    headers = {
        "x-rapidapi-key": RAPID_API_KEY,
        "x-rapidapi-host": RAPID_API_HOST
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            st.error(f"API Error {response.status_code}: {response.text}")
        else:
            data = response.json()

            # Build matches list
            matches = []
            for type_match in data.get("typeMatches", []):
                for series in type_match.get("seriesMatches", []):
                    wrapper = series.get("seriesAdWrapper", {})
                    series_name = wrapper.get("seriesName")
                    for match in wrapper.get("matches", []):
                        info = match.get("matchInfo", {})
                        matches.append({
                            "Match ID": info.get("matchId"),
                            "Series": series_name,
                            "Description": info.get("matchDesc"),
                            "Teams": f"{info.get('team1', {}).get('teamName')} vs {info.get('team2', {}).get('teamName')}",
                            "State": info.get("state"),
                            "Status": info.get("status")
                        })

            if not matches:
                st.warning("No recent matches returned by API.")
            else:
                df = pd.DataFrame(matches)

                # Show matches table
                st.dataframe(df.reset_index(drop=True))

                # ⬇️ CSV Download button
                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="⬇️ Download Matches as CSV",
                    data=csv,
                    file_name="matches.csv",
                    mime="text/csv"
                )

                # Match selector
                match_options = df.apply(lambda x: f"{x['Match ID']} - {x['Teams']} ({x['State']})", axis=1).tolist()
                selected = st.selectbox("🔎 Select a match for details:", ["None"] + match_options)

                if selected != "None":
                    match_id = selected.split(" - ")[0]
                    detail_url = f"https://{RAPID_API_HOST}/mcenter/v1/{match_id}"
                    detail_res = requests.get(detail_url, headers=headers, timeout=10)

                    if detail_res.status_code != 200:
                        st.error(f"Failed to fetch match details: HTTP {detail_res.status_code}")
                    else:
                        detail_data = detail_res.json()
                        st.subheader("📊 Match Details")
                        info = detail_data.get("matchInfo", {})
                        st.write(f"**Match:** {info.get('matchDesc')} | **Status:** {info.get('status')}")
                        st.json(detail_data)  # optional raw JSON preview

    except Exception as e:
        st.error(f"Request failed: {e}")






