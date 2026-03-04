import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import base64

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]


def get_service():
    creds = Credentials(
        None,
        refresh_token=os.getenv("GMAIL_REFRESH_TOKEN"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.getenv("GMAIL_CLIENT_ID"),
        client_secret=os.getenv("GMAIL_CLIENT_SECRET"),
        scopes=SCOPES,
    )

    service = build("gmail", "v1", credentials=creds)
    return service


def get_latest_email():
    service = get_service()

    results = service.users().messages().list(
        userId="me",
        q="is:unread",
        maxResults=1
    ).execute()

    messages = results.get("messages", [])

    if not messages:
        return None

    msg = messages[0]

    msg_data = service.users().messages().get(
        userId="me",
        id=msg["id"],
        format="full"
    ).execute()

    headers = msg_data["payload"]["headers"]

    subject = ""
    sender = ""

    for header in headers:
        if header["name"] == "Subject":
            subject = header["value"]
        if header["name"] == "From":
            sender = header["value"]

    body = ""

    if "parts" in msg_data["payload"]:
        for part in msg_data["payload"]["parts"]:
            if part["mimeType"] == "text/plain":
                body = base64.urlsafe_b64decode(
                    part["body"]["data"]
                ).decode()
    else:
        body = base64.urlsafe_b64decode(
            msg_data["payload"]["body"]["data"]
        ).decode()

    # Mark as read
    service.users().messages().modify(
        userId="me",
        id=msg["id"],
        body={"removeLabelIds": ["UNREAD"]}
    ).execute()

    return {
        "id": msg["id"],
        "subject": subject,
        "sender": sender,
        "body": body
    }