"""
database.py - Handles all database operations for the Store Manager app.
Includes user authentication, account creation, and login history tracking.
"""

import sqlite3
import hashlib
import os
import json
from datetime import datetime

# Path to the SQLite database file
DB_PATH = os.path.join(os.path.dirname(__file__), "store_manager.db")


def hash_password(password: str) -> str:
    """Hash a password using SHA-256 for secure storage."""
    return hashlib.sha256(password.encode()).hexdigest()


def get_connection() -> sqlite3.Connection:
    """Create and return a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Allows column access by name
    return conn


def initialize_db():
    """
    Initialize the database by creating required tables if they don't exist.
    Also inserts a default manager account for first-time setup.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Users table: stores login credentials and role
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            userID      TEXT PRIMARY KEY,
            password    TEXT NOT NULL,
            role        TEXT NOT NULL CHECK(role IN ('manager', 'employee')),
            created_at  TEXT NOT NULL
        )
    """)

    # Login history table: used for username autocomplete feature
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS login_history (
            userID      TEXT NOT NULL,
            last_login  TEXT NOT NULL,
            PRIMARY KEY (userID)
        )
    """)

    # Insert default manager account if no users exist yet
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            INSERT INTO users (userID, password, role, created_at)
            VALUES (?, ?, ?, ?)
        """, ("admin", hash_password("admin123"), "manager", datetime.now().isoformat()))
        print("[DB] Default manager account created: admin / admin123")

    conn.commit()
    conn.close()


def verify_login(userID: str, password: str):
    """
    Verify user credentials against the database.
    Returns the user row (with role) if valid, otherwise None.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM users WHERE userID = ? AND password = ?
    """, (userID, hash_password(password)))

    user = cursor.fetchone()
    conn.close()
    return user


def create_user(userID: str, password: str, role: str) -> tuple[bool, str]:
    """
    Create a new user account. Only callable by managers.
    Returns (success: bool, message: str).
    """
    if not userID or not password:
        return False, "UserID and password cannot be empty."

    if role not in ("manager", "employee"):
        return False, "Invalid role specified."

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO users (userID, password, role, created_at)
            VALUES (?, ?, ?, ?)
        """, (userID, hash_password(password), role, datetime.now().isoformat()))
        conn.commit()
        return True, f"Account '{userID}' created successfully."
    except sqlite3.IntegrityError:
        return False, f"UserID '{userID}' already exists."
    finally:
        conn.close()


def record_login(userID: str):
    """Record a successful login to the login history for autocomplete."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO login_history (userID, last_login)
        VALUES (?, ?)
        ON CONFLICT(userID) DO UPDATE SET last_login = excluded.last_login
    """, (userID, datetime.now().isoformat()))

    conn.commit()
    conn.close()


def get_login_history() -> list[str]:
    """Return a list of previously used userIDs for autocomplete suggestions."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT userID FROM login_history ORDER BY last_login DESC")
    history = [row["userID"] for row in cursor.fetchall()]

    conn.close()
    return history
