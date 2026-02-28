import psycopg2
import os
import time
from config import DATABASE_URL


conn = None
cursor = None


# ================= CONNECTION ================= #

def connect():
    global conn, cursor

    if not DATABASE_URL:
        raise Exception("❌ DATABASE_URL not found in environment variables!")

    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        print("✅ Connected to PostgreSQL")

    except Exception as e:
        print("❌ Database Connection Failed:", e)
        time.sleep(5)
        connect()


connect()


# ================= AUTO TABLE CREATION ================= #

def init_tables():
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

    conn.commit()
    print("✅ Tables Ready")


init_tables()


# ================= SAFE EXECUTION ================= #

def execute(query, values=()):
    try:
        cursor.execute(query, values)
        conn.commit()

    except psycopg2.OperationalError:
        print("⚠ Database disconnected — reconnecting...")
        connect()
        cursor.execute(query, values)
        conn.commit()

    except Exception as e:
        print("❌ DB Execute Error:", e)


def fetch(query, values=()):
    try:
        cursor.execute(query, values)
        return cursor.fetchall()

    except psycopg2.OperationalError:
        print("⚠ Database disconnected — reconnecting...")
        connect()
        cursor.execute(query, values)
        return cursor.fetchall()

    except Exception as e:
        print("❌ DB Fetch Error:", e)
        return []
