from twilio.rest import Client
import os
from dotenv import load_dotenv

load_dotenv()

client = Client(
    os.getenv("TWILIO_ACCOUNT_SID"),
    os.getenv("TWILIO_AUTH_TOKEN")
)

FROM = os.getenv("TWILIO_WHATSAPP_NUMBER")
TO = os.getenv("YOUR_WHATSAPP_NUMBER")


def send_whatsapp_message(message):
    response = client.messages.create(
        body=message,
        from_=FROM,
        to=TO
    )

    print("SENT SID:", response.sid)