import os
import base64
import re
from email import message_from_string
from bs4 import BeautifulSoup
from textblob import TextBlob
from datetime import datetime
import pandas as pd
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
CREDENTIALS_FILE = 'credentials.json'

def is_casual_text(text):
    casual_words = ['hey', 'yo', 'lol', 'thanks', 'cheers']
    formal_words = ['regards', 'dear', 'sincerely']
    casual_score = sum(word in text.lower() for word in casual_words)
    formal_score = sum(word in text.lower() for word in formal_words)
    return 'Casual' if casual_score > formal_score else 'Formal'

def detect_email_type(text):
    text_lower = text.lower()
    if 'newsletter' in text_lower:
        return 'Newsletter'
    if 'question' in text_lower or 'Q&A' in text:
        return 'Q&A'
    if 'pitch' in text_lower:
        return 'Pitch'
    return 'General'

def classify_value(text):
    text_lower = text.lower()
    if 'learn' in text_lower or 'how to' in text_lower:
        return 'Educational'
    if 'fun' in text_lower or 'joke' in text_lower:
        return 'Entertainment'
    if 'buy now' in text_lower or 'offer' in text_lower:
        return 'Promotional'
    return 'Other'

def detect_subject_pattern(subject):
    subject_lower = subject.lower()
    explanations = []
    if re.search(r'[!?🔥]', subject):
        explanations.append("Curiosity")
    emotion_keywords = {
        'amazing': 'amazement',
        'love': 'positive sentiment',
        'hate': 'negative sentiment',
        'exclusive': 'exclusivity',
        'secret': 'intrigue',
        'shocking': 'surprise',
        'unbelievable': 'astonishment'
    }
    found = [desc for word, desc in emotion_keywords.items() if word in subject_lower]
    if found:
        explanations.append("Emotion – " + ", ".join(found))
    return " + ".join(explanations) if explanations else "None"

def detect_hook_style(text):
    if '?' in text:
        if re.search(r'how|why|what|when|where', text.lower()):
            return "Question – Curiosity"
        elif re.search(r'do you|have you|can you', text.lower()):
            return "Question – CTA"
        else:
            return "Question – Generic"
    return "Statement or List"

def extract_email_features(raw_email):
    msg = message_from_string(raw_email)
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == 'text/plain':
                body = part.get_payload(decode=True).decode(errors='ignore')
                break
            elif part.get_content_type() == 'text/html' and not body:
                body = part.get_payload(decode=True).decode(errors='ignore')
    else:
        body = msg.get_payload(decode=True).decode(errors='ignore')

    subject = msg.get('Subject', '')
    sender = msg.get('From', '')
    date_str = msg.get('Date', '')
    try:
        try:
            date = datetime.strptime(date_str[:25], '%a, %d %b %Y %H:%M:%S')
        except ValueError:
            date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ')
        time_sent = date.strftime('%I:%M %p, %A')
    except:
        time_sent = 'Unknown'

    soup = BeautifulSoup(body, 'html.parser')
    text = soup.get_text(separator=' ')

    links = soup.find_all('a', href=True)
    valid_links = [a['href'] for a in links if 'http' in a['href'] or 'mailto:' in a['href']]
    hyperlink_summary = f"✅ {len(valid_links)} links found" if valid_links else "❌"

    casual_words = ['hey', 'yo', 'lol', 'thanks', 'cheers']
    formal_words = ['regards', 'dear', 'sincerely']
    casual_count = sum(word in text.lower() for word in casual_words)
    formal_count = sum(word in text.lower() for word in formal_words)
    tone = 'Casual' if casual_count > formal_count else 'Formal'
    tone_reason = f"{'Casual indicators' if casual_count else 'Formal indicators'} found in text"

    def classify_cta(soup):
        for link in soup.find_all('a', href=True):
            href = link['href'].lower()
            text = link.get_text().strip().lower()
            classes = link.get('class', [])
            if any(kw in href or kw in text for kw in ['sign', 'register', 'signup']):
                return f"Button – Sign Up"
            elif 'login' in href or 'login' in text:
                return f"Button – Login"
            elif 'buy' in href or 'shop' in text:
                return f"Button – Buy"
            elif 'learn' in href or 'learn' in text:
                return f"Button – Learn"
        return "❌ No clear CTA"

    subject_emotion_explanation = []
    if re.search(r'[!?🔥]', subject):
        subject_emotion_explanation.append("Uses punctuation/symbols to provoke curiosity")
    emotion_keywords = {
        'amazing': 'amazement', 'love': 'positive sentiment', 'hate': 'negative sentiment',
        'exclusive': 'exclusivity', 'secret': 'intrigue', 'shocking': 'surprise'
    }
    found_emotions = [desc for word, desc in emotion_keywords.items() if word in subject.lower()]
    if found_emotions:
        subject_emotion_explanation.append("Emotion: " + ", ".join(found_emotions))
    subject_explained = " + ".join(subject_emotion_explanation) if subject_emotion_explanation else "None"

    if '?' in subject:
        if re.search(r'how|why|what|when|where', subject.lower()):
            hook = "Question – Curiosity"
            hook_explained = "Uses 'wh' question to provoke curiosity"
        elif re.search(r'do you|have you|can you', subject.lower()):
            hook = "Question – CTA"
            hook_explained = "Direct question implying action"
        else:
            hook = "Question – Generic"
            hook_explained = "Generic question in subject"
    else:
        hook = "Statement or List"
        hook_explained = "No question structure in subject"

    sentiment = TextBlob(text).sentiment.polarity
    email_type = detect_email_type(text)
    value_category = classify_value(text)
    has_image = bool(soup.find('img'))

    return {
        "Metric": [
            "Sender", "Frequency", "Time Sent", "Contains Hyperlinks", "Subject Emotion",
            "Subject Emotion Reason", "Type", "CTA", "Length", "Tone", "Tone Reason",
            "Contains Visuals", "Hook Style", "Hook Explanation", "Category"
        ],
        "Value": [
            f"[{sender}](mailto:{sender})",
            "3 emails/week",
            time_sent,
            hyperlink_summary,
            subject_explained,
            subject_explained if subject_explained != "None" else "No emotional/curiosity triggers found",
            email_type,
            classify_cta(soup),
            f"{len(text.split())} words",
            tone,
            tone_reason,
            "✅" if has_image else "❌",
            hook,
            hook_explained,
            value_category
        ]
    }

def get_raw_email(service, msg_id):
    try:
        message = service.users().messages().get(userId='me', id=msg_id, format='raw').execute()
        return base64.urlsafe_b64decode(message['raw']).decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Error fetching email {msg_id}: {str(e)}")
        return None

def analyze_real_emails(service, num_emails=3):
    results = service.users().messages().list(userId='me', maxResults=num_emails, labelIds=['INBOX']).execute()
    messages = results.get('messages', [])
    all_dfs = []

    for msg in messages:
        raw_email = get_raw_email(service, msg['id'])
        if raw_email:
            features = extract_email_features(raw_email)
            features["Metric"].append("Message ID")
            features["Value"].append(msg['id'])
            df = pd.DataFrame(features)
            all_dfs.append(df)

    return pd.concat(all_dfs, ignore_index=True) if all_dfs else pd.DataFrame()

email_analysis_df = analyze_real_emails(service, 3)
email_analysis_df
