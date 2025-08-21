````markdown
# 📅 Smart Email-to-Calendar Assistant

An automation tool that reads **unread Gmail messages**, extracts **event details** using **Google Gemini AI**, and creates corresponding events in **Google Calendar**.  
Designed to save time by automatically scheduling meetings, invites, and reminders directly from your inbox.

---

## 🚀 Features
- ✅ Reads unread Gmail messages via **Gmail API**  
- ✅ Extracts structured event details (**title, datetime, location, description**) from unstructured text using **Gemini LLM**  
- ✅ Creates calendar events in **Google Calendar API**  
- ✅ Handles **OAuth2 authentication** securely  
- ✅ Avoids duplicates by tracking processed message IDs  
- ✅ Supports flexible date/time parsing with `dateparser`  
- ✅ Runs automatically at configurable intervals  

---

## 🛠️ Tech Stack
- **Language:** Python 3  
- **AI Model:** [Google Gemini](https://aistudio.google.com)  
- **APIs:** Gmail API, Google Calendar API  
- **Auth:** OAuth2 (`google-auth`, `google-auth-oauthlib`)  
- **Libraries:**  
  - `google-api-python-client` (Gmail + Calendar API)  
  - `google.generativeai` (Gemini LLM)  
  - `bs4` (HTML email parsing)  
  - `dateparser` (datetime normalization)  

---

## ⚙️ Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/email-calendar-assistant.git
cd email-calendar-assistant
````

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure APIs

* **Google Cloud Project**

  * Enable Gmail API + Calendar API
  * Download `credentials.json` (OAuth client ID) and place it in the project root.

* **Gemini API**

  * Get a Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey).
  * Export it:

    ```bash
    export GEMINI_API_KEY="your_gemini_api_key"
    ```

### 4. First-Time Authentication

On first run, you’ll be asked to authenticate with Google. A `token.json` file will be created for future use.

```bash
python main.py
```

---

## 📂 Project Structure

```
.
├── main.py                # Main script
├── credentials.json       # Google OAuth client secrets
├── token.json             # Generated OAuth token (auto-created)
├── processed_ids.json     # Stores processed Gmail message IDs
├── requirements.txt       # Dependencies
└── README.md              # Project documentation
```

---

## 🧩 How It Works

1. Polls Gmail for unread messages (`is:unread`).
2. Extracts email body (supports plain text + HTML).
3. Passes content to **Gemini LLM**, asking for JSON event details.
4. Normalizes date/time strings (`dateparser`).
5. Creates a calendar event in Google Calendar.
6. Marks the email as processed (to avoid duplicates).

---

## 🖼️ Demo (Example Flow)

**Email Content:**

```
Hi,
Meeting scheduled on 23rd Aug at 3 PM, Office Boardroom.
Agenda: Project status update.
```

**Extracted JSON (via Gemini):**

```json
{
  "name": "Project Status Update Meeting",
  "start datetime": "23rd Aug 2025, 3:00 PM",
  "end datetime": "23rd Aug 2025, 4:00 PM",
  "location": "Office Boardroom",
  "description": "Agenda: Project status update"
}
```

**Calendar Event Created ✅**

```

---

This style makes it **professional and recruiter-friendly**.  

👉 Do you want me to also draft a **requirements.txt** file for your repo so setup becomes copy-paste easy?
```
