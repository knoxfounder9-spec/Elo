import psycopg2
from config import DATABASE_URL

conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

# Create tables automatically
cursor.execute("""
CREATE TABLE IF NOT EXISTS players (
    user_id TEXT PRIMARY KEY,
    elo INTEGER DEFAULT 0,
    wins INTEGER DEFAULT 0,
    losses INTEGER DEFAULT 0
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS match_history (
    id SERIAL PRIMARY KEY,
    winner TEXT,
    loser TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

conn.commit()

def execute(query, values=()):
    cursor.execute(query, values)
    conn.commit()

def fetch(query, values=()):
    cursor.execute(query, values)
    return cursor.fetchall()
