import sqlite3
from datetime import datetime, timedelta


def init_db():
    conn = sqlite3.connect("activity_log.db")
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
    conn = sqlite3.connect("activity_log.db")
    cursor = conn.cursor()
    cursor.executemany("INSERT INTO logs (window_name) VALUES (?)", [(log,) for log in logs])
    conn.commit()
    conn.close()


def save_screenshot(file_path, extracted_text="", log_id=None):
    """
    Save screenshot metadata to database.

    Args:
        file_path (str): Path to the screenshot file
        extracted_text (str): OCR-extracted text from the screenshot
        log_id (int, optional): ID of related activity log entry
    """
    conn = sqlite3.connect("activity_log.db")
    cursor = conn.cursor()
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
    conn = sqlite3.connect("activity_log.db")
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


def calculate_hours_worked_today(db_path="activity_log.db"):
    """
    Calculate total hours worked today based on screenshot timestamps.
    Assumes screenshots are taken at regular intervals during active work.

    Returns:
        int: Number of hours worked (rounded)
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get today's date range
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)

    # Get all screenshots from today
    cursor.execute("""
        SELECT timestamp FROM screenshots
        WHERE timestamp >= ? AND timestamp < ?
        ORDER BY timestamp ASC
    """, (today_start.isoformat(), today_end.isoformat()))

    timestamps = cursor.fetchall()
    conn.close()

    if not timestamps or len(timestamps) < 2:
        return 0

    # Parse timestamps
    times = [datetime.fromisoformat(ts[0]) for ts in timestamps]

    # Calculate time span from first to last screenshot
    time_span = times[-1] - times[0]
    hours_worked = time_span.total_seconds() / 3600

    # Round to nearest hour
    return int(round(hours_worked))
