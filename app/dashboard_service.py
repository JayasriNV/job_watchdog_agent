import sqlite3

DB_NAME = "job_tracker.db"


def get_dashboard_stats():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM applications")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM applications WHERE category='Interview'")
    interviews = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM applications WHERE category='Offer'")
    offers = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM applications WHERE category='Rejection'")
    rejections = cursor.fetchone()[0]

    # Pending confirmations = Interviews only
    pending_confirmations = interviews

    # Escalation logic placeholder (can expand later)
    escalated = 0

    success_rate = 0
    if total > 0:
        success_rate = round((offers / total) * 100, 2)

    conn.close()

    return {
        "total_applications": total,
        "interviews": interviews,
        "offers": offers,
        "rejections": rejections,
        "pending_confirmations": pending_confirmations,
        "escalated": escalated,
        "success_rate_percent": success_rate
    }