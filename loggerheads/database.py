import sqlite3
import os
from pathlib import Path
from datetime import datetime, timedelta


def get_db_path():
    """Get the absolute path to the database file in ~/.loggerheads_logs/"""
    log_dir = Path.home() / ".loggerheads_logs"
    log_dir.mkdir(exist_ok=True)
    return str(log_dir / "activity_log.db")


def init_db(db_path=None):
    if db_path is None:
        db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create logs table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            window_name TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create screenshots table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS screenshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_path TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            extracted_text TEXT,
            log_id INTEGER,
            FOREIGN KEY (log_id) REFERENCES logs(id)
        )
    """)

    conn.commit()
    conn.close()


def save_logs(logs):
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.executemany("INSERT INTO logs (window_name) VALUES (?)", [(log,) for log in logs])
    conn.commit()
    conn.close()


def save_screenshot(file_path, extracted_text="", log_id=None, timestamp=None):
    """
    Save screenshot metadata to database.

    Args:
        file_path (str): Path to the screenshot file
        extracted_text (str): OCR-extracted text from the screenshot
        log_id (int, optional): ID of related activity log entry
        timestamp (str, optional): Custom timestamp (ISO format) for demo mode
    """
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    if timestamp:
        # Custom timestamp (for demo mode)
        cursor.execute(
            "INSERT INTO screenshots (file_path, extracted_text, log_id, timestamp) VALUES (?, ?, ?, ?)",
            (file_path, extracted_text, log_id, timestamp)
        )
    else:
        # Auto timestamp (normal operation)
        cursor.execute(
            "INSERT INTO screenshots (file_path, extracted_text, log_id) VALUES (?, ?, ?)",
            (file_path, extracted_text, log_id)
        )
    
    conn.commit()
    conn.close()


def get_screenshots(limit=None):
    """
    Retrieve screenshots from database.

    Args:
        limit (int, optional): Maximum number of screenshots to retrieve

    Returns:
        list: List of tuples containing screenshot data
    """
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    if limit:
        cursor.execute(
            "SELECT id, file_path, timestamp, extracted_text FROM screenshots ORDER BY timestamp DESC LIMIT ?",
            (limit,)
        )
    else:
        cursor.execute(
            "SELECT id, file_path, timestamp, extracted_text FROM screenshots ORDER BY timestamp DESC"
        )

    results = cursor.fetchall()
    conn.close()
    return results


def calculate_hours_worked_today(db_path=None):
    """
    Calculate total hours worked today based on screenshot timestamps.
    Assumes screenshots are taken at regular intervals during active work.

    Returns:
        int: Number of hours worked (rounded)
    """
    if db_path is None:
        db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get all screenshots from today using DATE comparison (works with any timestamp format)
    cursor.execute("""
        SELECT timestamp FROM screenshots
        WHERE DATE(timestamp) = DATE('now')
        ORDER BY timestamp ASC
    """)

    timestamps = cursor.fetchall()
    conn.close()

    if not timestamps or len(timestamps) < 2:
        return 0

    # Parse timestamps
    times = [datetime.fromisoformat(ts[0]) for ts in timestamps]

    # Calculate time span from first to last screenshot
    time_span = times[-1] - times[0]
    hours_worked = time_span.total_seconds() / 3600

    # Return actual hours (round to 1 decimal place for readability)
    return round(hours_worked, 1)
