import psycopg2
from config import DATABASE_URL
import time
import sys

conn = None
cursor = None


def connect():
    global conn, cursor

    if not DATABASE_URL:
        raise Exception("❌ DATABASE_URL not found!")

    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = False
        cursor = conn.cursor()
        print("✅ Database Connected")

    except Exception as e:
        print("❌ DB Connection Failed:", e)
        time.sleep(5)
        connect()


connect()


# ================= TABLE SETUP ================= #

try:
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
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

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bot_settings (
        key TEXT PRIMARY KEY,
        value TEXT
    );
    """)

    conn.commit()

    print("✅ Tables Verified")

except Exception as e:
    print("❌ Table Creation Error:", e)
    sys.exit(1)


# ================= QUERY FUNCTIONS ================= #

def execute(query, values=()):
    try:
        cursor.execute(query, values)
        conn.commit()
    except Exception as e:
        conn.rollback()
        print("❌ SQL Execute Error:", e)


def fetch(query, values=()):
    try:
        cursor.execute(query, values)
        return cursor.fetchall()
    except Exception as e:
        print("❌ SQL Fetch Error:", e)
        return []
