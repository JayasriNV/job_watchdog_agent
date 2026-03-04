import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")


TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")

TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")
MY_WHATSAPP_NUMBER = os.getenv("MY_WHATSAPP_NUMBER")

# Spam Filtering
DOMAIN_IGNORE_LIST = ["marketing", "noreply", "no-reply", "newsletter", "promotions", "updates"]
SPAM_KEYWORDS = ["unsubscribe", "view in browser", "click here to unsubscribe", "opt out"]