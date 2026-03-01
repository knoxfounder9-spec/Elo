import psycopg2
from psycopg2 import OperationalError
from config import DATABASE_URL
import time
import sys

conn = None
cursor = None


# ================= CONNECTION ================= #

def connect():
    global conn, cursor

    if not DATABASE_URL:
        raise Exception("❌ DATABASE_URL not found!")

    while True:
        try:
            conn = psycopg2.connect(DATABASE_URL)
            conn.autocommit = False
            cursor = conn.cursor()
            print("✅ Database Connected")
            break

        except Exception as e:
            print("❌ DB Connection Failed:", e)
            print("🔁 Retrying in 5 seconds...")
            time.sleep(5)


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


# ================= SAFE EXECUTE ================= #

def execute(query, values=()):
    global conn, cursor

    try:
        cursor.execute(query, values)
        conn.commit()

    except OperationalError:
        print("⚠️ Lost DB connection. Reconnecting...")
        connect()
        cursor.execute(query, values)
        conn.commit()

    except Exception as e:
        conn.rollback()
        print("❌ SQL Execute Error:", e)


# ================= SAFE FETCH ================= #

def fetch(query, values=()):
    global conn, cursor

    try:
        cursor.execute(query, values)
        return cursor.fetchall()

    except OperationalError:
        print("⚠️ Lost DB connection. Reconnecting...")
        connect()
        cursor.execute(query, values)
        return cursor.fetchall()

    except Exception as e:
        print("❌ SQL Fetch Error:", e)
        return []
