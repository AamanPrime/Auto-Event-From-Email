import time, base64, json, os, re
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import dateparser
import google.generativeai as genai
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

CHECK_INTERVAL = 300  # seconds
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SCOPES = ["https://www.googleapis.com/auth/gmail.modify",
          "https://www.googleapis.com/auth/calendar"]

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

PROCESSED_FILE = "processed_ids.json"

def load_processed_ids():
    if os.path.exists(PROCESSED_FILE):
        with open(PROCESSED_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_processed_ids(processed_ids):
    with open(PROCESSED_FILE, "w") as f:
        json.dump(list(processed_ids), f)

def authenticate():
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    creds = flow.run_local_server(port=0)
    with open('token.json', 'w') as token:
        token.write(creds.to_json())
    return creds

def load_creds():
    try:
        return Credentials.from_authorized_user_file('token.json', SCOPES)
    except:
        return authenticate()

def clean_and_parse_json(raw_text):
    json_match = re.search(r"\{[\s\S]*\}", raw_text)
    if not json_match:
        raise ValueError(f"No JSON found in Gemini output:\n{raw_text}")
    json_str = json_match.group(0)

    # Remove trailing commas which break json.loads
    json_str = re.sub(r",\s*([\]}])", r"\1", json_str)

    return json.loads(json_str)

def normalize_datetime(date_str):
    if not date_str or not isinstance(date_str, str):
        return None
    parsed = dateparser.parse(date_str)
    if not parsed:
        return None
    return parsed.isoformat()


def extract_event_details(email_text):
    prompt = f"""
    Extract event details from the following text.
    Return ONLY valid JSON with these keys:
    name, start datetime, end datetime, location, description.
    Ensure start and end datetimes are in human-readable form.
    Text: {email_text}
    """
    resp = model.generate_content(prompt)
    return clean_and_parse_json(resp.text)

def create_calendar_event(details, creds):
    start_dt = normalize_datetime(details.get('start datetime'))
    end_dt = normalize_datetime(details.get('end datetime'))

    # Skip if start is missing
    if not start_dt:
        print(f"⚠️ Skipping event '{details.get('name', 'No Title')}' — missing or invalid start date/time.")
        return

    # If end time is missing, set to start + 1 hour
    if not end_dt:
        start_obj = datetime.fromisoformat(start_dt)
        end_obj = start_obj + timedelta(hours=1)
        end_dt = end_obj.isoformat()

    calendar_service = build('calendar', 'v3', credentials=creds)
    event = {
        'summary': details.get('name', 'No Title'),
        'description': details.get('description', ''),
        'start': {'dateTime': start_dt, 'timeZone': 'Asia/Kolkata'},
        'end': {'dateTime': end_dt, 'timeZone': 'Asia/Kolkata'},
        'location': details.get('location', '')
    }
    calendar_service.events().insert(calendarId='primary', body=event).execute()
    
    print(f"✅ Added event: {details.get('name')}")


def get_email_body(payload):
    body_data = ""
    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain' and 'data' in part['body']:
                body_data = base64.urlsafe_b64decode(part['body']['data']).decode()
            elif part['mimeType'] == 'text/html' and 'data' in part['body']:
                html = base64.urlsafe_b64decode(part['body']['data']).decode()
                body_data = BeautifulSoup(html, 'html.parser').get_text()
    elif 'body' in payload and 'data' in payload['body']:
        body_data = base64.urlsafe_b64decode(payload['body']['data']).decode()
    return body_data.strip()

def get_new_emails(gmail_service, processed_ids, creds):
    results = gmail_service.users().messages().list(userId='me', q="is:unread").execute()
    messages = results.get('messages', [])
    for msg in messages:
        if msg['id'] in processed_ids:
            continue
        msg_data = gmail_service.users().messages().get(userId='me', id=msg['id']).execute()
        body_data = get_email_body(msg_data['payload'])
        if not body_data:
            continue

        print("\n📧 Email Content:\n", body_data[:200], "...")
        details = extract_event_details(body_data)
        print("📅 Extracted Event:", details)

        create_calendar_event(details, creds)
        processed_ids.add(msg['id'])
        save_processed_ids(processed_ids)

if __name__ == "__main__":

    creds = load_creds()
    gmail_service = build('gmail', 'v1', credentials=creds)
    processed_ids = load_processed_ids()
    while True:
        get_new_emails(gmail_service, processed_ids, creds)
        time.sleep(CHECK_INTERVAL)
