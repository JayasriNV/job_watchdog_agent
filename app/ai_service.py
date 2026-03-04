import os
import json
import re
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


SPAM_INDICATORS = [
    "sale",
    "discount",
    "black friday",
    "cyber monday",
    "offer ends",
    "limited time",
    "subscribe",
    "unsubscribe",
    "promo",
    "reward points",
]


def is_spam(subject, body):
    text = (subject + " " + body).lower()
    return any(word in text for word in SPAM_INDICATORS)


def detect_category(subject, body):
    text = (subject + " " + body).lower()

    # Rejection first
    if any(x in text for x in [
        "regret to inform",
        "not selected",
        "unfortunately",
        "we will not be moving forward"
    ]):
        return "Rejection"

    # Interview detection
    if any(x in text for x in [
        "interview",
        "final round",
        "technical round",
        "hr round",
        "shortlisted"
         
    ]):
        return "Interview"

    # Offer detection
    if any(x in text for x in [
        "offer letter",
        "employment offer",
        "official offer",
        "appointment letter",
        "we are pleased to offer",
        "we are pleased to confirm your appointment",
        "job offer",
        "employment offer",
        "congratulations",
        "selected for the role"
    ]):
        return "Offer"

    return None


def extract_json(text):
    try:
        text = re.sub(r"```json|```", "", text).strip()
        start = text.find("{")
        end = text.rfind("}") + 1
        if start != -1 and end != -1:
            return json.loads(text[start:end])
    except:
        pass
    return None


def classify_email(subject, body, sender):

    # STEP 1 — detect job category first
    category = detect_category(subject, body)

    if not category:
        # only apply spam filter if no job keywords found
        if is_spam(subject, body):
            return {"is_job_related": False}
        return {"is_job_related": False}

    # If we reach here → it IS job related
    result = {
        "is_job_related": True,
        "category": category,
        "company": None,
        "role": None,
        "interview_date": None,
        "interview_time": None,
        "time_zone": None,
        "mode": None,
        "location_or_link": None,
        "action_required": None,
        "deadline": None,
        "prep_brief": {},
        "company_insight": {}
    }

    try:
        prompt = f"""
Extract structured job information.

Return ONLY valid JSON.

Subject: {subject}
Body: {body[:1500]}

JSON format:
{{
"company": "",
"role": "",
"interview_date": "",
"interview_time": "",
"time_zone": "",
"mode": "",
"location_or_link": "",
"action_required": "",
"deadline": ""
}}
"""

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=400
        )

        raw_output = response.choices[0].message.content
        parsed = extract_json(raw_output)

        if parsed:
            result.update(parsed)

    except Exception as e:
        print("AI extraction failed:", e)

    return result