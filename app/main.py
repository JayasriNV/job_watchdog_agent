from fastapi import FastAPI
from datetime import datetime, timedelta
import asyncio

from app.gmail_service import get_latest_email
from app.ai_service import classify_email
from app.whatsapp_service import send_whatsapp_message
from app.database import (
    init_db, save_application,
    get_upcoming_interviews,
    mark_reminder_sent
)
from app.dashboard_service import get_dashboard_stats

app = FastAPI()


def safe(value):
    return value if value else "N/A"


def build_full_message(data, stats):
    category = data["category"]

    if category == "Offer":
        header = "🚨 OFFER RECEIVED 🚨"
    elif category == "Interview":
        header = "🚀 JOB ALERT"
    else:
        header = "❌ APPLICATION UPDATE"

    lines = [header, ""]

    lines.append(f"Company: {safe(data.get('company'))}")
    lines.append(f"Role: {safe(data.get('role'))}")
    lines.append(f"Category: {category}")

    if category == "Interview":
        lines.extend([
            "",
            f"Interview Date: {safe(data.get('interview_date'))}",
            f"Interview Time: {safe(data.get('interview_time'))}",
            f"Mode: {safe(data.get('mode'))}",
            f"Link: {safe(data.get('location_or_link'))}"
        ])

    lines.extend([
        "",
        f"Action Required: {safe(data.get('action_required'))}",
        f"Deadline: {safe(data.get('deadline'))}"
    ])

    lines.extend([
        "",
        "📊 CURRENT CAREER STATS",
        f"Total Applications: {stats['total_applications']}",
        f"Interviews: {stats['interviews']}",
        f"Offers: {stats['offers']}",
        f"Rejections: {stats['rejections']}",
        f"Success Rate: {stats['success_rate_percent']}%",
        f"Pending Confirmations: {stats['pending_confirmations']}",
        f"Escalated: {stats['escalated']}"
    ])

    return "\n".join(lines)


async def reminder_engine():
    while True:
        now = datetime.now()
        interviews = get_upcoming_interviews()

        for app_id, company, role, interview_dt, r24, r1 in interviews:
            if not interview_dt:
                continue

            interview_time = datetime.strptime(interview_dt, "%Y-%m-%d %H:%M:%S")

            diff = interview_time - now

            if diff <= timedelta(hours=24) and diff > timedelta(hours=23) and r24 == 0:
                send_whatsapp_message(
                    f"⏰ 24-HOUR REMINDER\n\nCompany: {company}\nRole: {role}\nInterview At: {interview_dt}"
                )
                mark_reminder_sent(app_id, "24")

            if diff <= timedelta(hours=1) and diff > timedelta(minutes=59) and r1 == 0:
                send_whatsapp_message(
                    f"🚨 1-HOUR REMINDER\n\nCompany: {company}\nRole: {role}\nInterview At: {interview_dt}"
                )
                mark_reminder_sent(app_id, "1hr")

        await asyncio.sleep(60)


@app.on_event("startup")
async def startup():
    init_db()
    asyncio.create_task(reminder_engine())


@app.get("/check-now")
def check_now():
    email = get_latest_email()

    if not email:
        return {"message": "No unread emails"}

    data = classify_email(email["subject"], email["body"], email["sender"])

    if not data.get("is_job_related"):
        return {"message": "Not job related"}

    save_application(
        email["id"],
        email["subject"],
        email["sender"],
        data.get("company"),
        data.get("role"),
        data.get("category"),
        data.get("interview_date"),
        data.get("interview_time"),
        data.get("category")
    )

    stats = get_dashboard_stats()
    message = build_full_message(data, stats)
    send_whatsapp_message(message)

    return {"message": "Processed"}