import sqlite3
from datetime import datetime

DB_NAME = "job_tracker.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email_id TEXT UNIQUE,
        subject TEXT,
        sender TEXT,
        company TEXT,
        role TEXT,
        category TEXT,
        interview_datetime TEXT,
        status TEXT,
        reminder_24_sent INTEGER DEFAULT 0,
        reminder_1hr_sent INTEGER DEFAULT 0,
        created_at TEXT
    )
    """)

    conn.commit()
    conn.close()


def save_application(email_id, subject, sender, company, role,
                     category, interview_date, interview_time, status):

    interview_datetime = None

    if interview_date and interview_time:
        try:
            combined = f"{interview_date} {interview_time}"
            parsed = datetime.strptime(combined, "%Y-%m-%d %H:%M")
            interview_datetime = parsed.strftime("%Y-%m-%d %H:%M:%S")
        except:
            try:
                parsed = datetime.strptime(
                    f"{interview_date} {interview_time}",
                    "%B %d, %Y %I:%M %p"
                )
                interview_datetime = parsed.strftime("%Y-%m-%d %H:%M:%S")
            except:
                interview_datetime = None

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT OR IGNORE INTO applications
    (email_id, subject, sender, company, role, category,
     interview_datetime, status, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        email_id, subject, sender, company, role,
        category, interview_datetime,
        status, datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()


def get_upcoming_interviews():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, company, role, interview_datetime,
           reminder_24_sent, reminder_1hr_sent
    FROM applications
    WHERE category='Interview'
      AND interview_datetime IS NOT NULL
    """)

    rows = cursor.fetchall()
    conn.close()
    return rows


def mark_reminder_sent(app_id, reminder_type):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    if reminder_type == "24":
        cursor.execute("UPDATE applications SET reminder_24_sent=1 WHERE id=?", (app_id,))
    elif reminder_type == "1hr":
        cursor.execute("UPDATE applications SET reminder_1hr_sent=1 WHERE id=?", (app_id,))

    conn.commit()
    conn.close()