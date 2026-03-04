from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import os


def create_calendar_event(title, description, date, time, timezone="Asia/Kolkata"):

    creds = Credentials.from_authorized_user_file("token.json")

    # IMPORTANT: build CALENDAR service, not gmail
    service = build("calendar", "v3", credentials=creds)

    start_datetime = f"{date}T{time}:00"

    # 1-hour duration
    start_dt = datetime.fromisoformat(start_datetime)
    end_dt = start_dt + timedelta(hours=1)

    event = {
        "summary": title,
        "description": description,
        "start": {
            "dateTime": start_dt.isoformat(),
            "timeZone": timezone,
        },
        "end": {
            "dateTime": end_dt.isoformat(),
            "timeZone": timezone,
        },
        "reminders": {
            "useDefault": False,
            "overrides": [
                {"method": "popup", "minutes": 1440},  # 1 day before
                {"method": "popup", "minutes": 60},    # 1 hour before
            ],
        },
    }

    created_event = service.events().insert(
        calendarId="primary",
        body=event
    ).execute()

    print("Calendar event created:", created_event.get("htmlLink"))