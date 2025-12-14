# src/database_manager.py

import sqlite3
import datetime

# Define the path to the database file in the 'data' directory
DB_PATH = 'data/regulations.db'

def create_connection():
    """Create a database connection."""
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
    return conn

def setup_database():
    """Create the table needed to store regulatory rule versions."""
    conn = create_connection()
    if conn:
        try:
            # UPDATED: Added 'rule_id' column to track different rules separately
            conn.execute("""
                CREATE TABLE IF NOT EXISTS rule_versions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    rule_id TEXT NOT NULL,
                    rule_text TEXT NOT NULL,
                    change_summary TEXT,
                    check_date TEXT NOT NULL
                );
            """)
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            print(f"Error setting up database table: {e}")

def get_latest_version(rule_id: str):
    """Retrieve the text of the latest saved version for a SPECIFIC rule."""
    conn = create_connection()
    latest_text = ""
    if conn:
        try:
            cursor = conn.cursor()
            # UPDATED: Filter by rule_id
            cursor.execute("SELECT rule_text FROM rule_versions WHERE rule_id = ? ORDER BY id DESC LIMIT 1;", (rule_id,))
            result = cursor.fetchone()
            if result:
                latest_text = result[0]
            conn.close()
        except sqlite3.Error as e:
            print(f"Error retrieving latest version: {e}")
    return latest_text

def log_new_version(rule_id: str, new_text: str, summary: str = "Initial or Minor Change"):
    """Insert a new rule version into the database for a specific rule."""
    conn = create_connection()
    if conn:
        try:
            timestamp = datetime.datetime.now().isoformat()
            # UPDATED: Insert rule_id
            conn.execute(
                "INSERT INTO rule_versions (rule_id, rule_text, change_summary, check_date) VALUES (?, ?, ?, ?)",
                (rule_id, new_text, summary, timestamp)
            )
            conn.commit()
            conn.close()
            print(f"[{rule_id}] New version logged on {timestamp}.")
            return True
        except sqlite3.Error as e:
            print(f"Error logging new version: {e}")
            return False
    return False

# Run setup immediately on import to ensure table exists
setup_database()