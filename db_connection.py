from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from pathlib import Path

def get_engine(db_path: str = None, echo: bool = False) -> Engine:
    """Return a SQLAlchemy Engine for SQLite.
    Creates the `data` dir if missing. On Day-3 we'll add schema create helpers.
    """
    data_dir = Path(__file__).resolve().parent.parent / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    if db_path is None:
        db_path = str(data_dir / "cricbuzz.db")
    engine = create_engine(f"sqlite:///{db_path}", echo=echo, future=True)
    return engine


from sqlalchemy import text
from pathlib import Path

def init_db():
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS teams (
            team_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            country TEXT
        );
        """))
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS players (
            player_id INTEGER PRIMARY KEY,
            full_name TEXT NOT NULL,
            role TEXT,
            batting_style TEXT,
            bowling_style TEXT,
            team_id INTEGER,
            FOREIGN KEY (team_id) REFERENCES teams(team_id)
        );
        """))
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS venues (
            venue_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            city TEXT,
            country TEXT,
            capacity INTEGER
        );
        """))
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS matches (
            match_id INTEGER PRIMARY KEY,
            description TEXT,
            team1_id INTEGER,
            team2_id INTEGER,
            venue_id INTEGER,
            date TEXT,
            winner_id INTEGER,
            FOREIGN KEY (team1_id) REFERENCES teams(team_id),
            FOREIGN KEY (team2_id) REFERENCES teams(team_id),
            FOREIGN KEY (venue_id) REFERENCES venues(venue_id),
            FOREIGN KEY (winner_id) REFERENCES teams(team_id)
        );
        """))

def seed_sample_data():
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(text("""
        INSERT OR IGNORE INTO teams (team_id, name, country) VALUES
        (1, 'India', 'India'),
        (2, 'Australia', 'Australia');
        """))
        conn.execute(text("""
        INSERT OR IGNORE INTO players (player_id, full_name, role, batting_style, bowling_style, team_id) VALUES
        (1, 'Virat Kohli', 'Batsman', 'Right-hand bat', 'Right-arm medium', 1),
        (2, 'Steve Smith', 'Batsman', 'Right-hand bat', 'Right-arm legbreak', 2);
        """))
        conn.execute(text("""
        INSERT OR IGNORE INTO venues (venue_id, name, city, country, capacity) VALUES
        (1, 'Wankhede Stadium', 'Mumbai', 'India', 33000);
        """))
        conn.execute(text("""
        INSERT OR IGNORE INTO matches (match_id, description, team1_id, team2_id, venue_id, date, winner_id) VALUES
        (1001, 'India vs Australia Test', 1, 2, 1, '2025-01-01', 1);
        """))

def list_tables():
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"))
        return [row[0] for row in result]
