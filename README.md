# 📧 Smart Email Feature Extraction & Classification System

This project is an advanced Gmail-based Email Analyzer built with Python, Google Gmail API, and NLP. It extracts and classifies valuable semantic and structural insights from your real Gmail inbox — perfect for email intelligence, behavioral analysis, and smart inbox management.

---

## 🚀 Features

The system detects and analyzes key elements from emails:

| Feature                 | Description |
|-------------------------|-------------|
| **Sender**              | Extracts and links the sender's email |
| **Frequency**           | Tag showing how often the sender emails (placeholder) |
| **Time Sent**           | Extracted and formatted send time |
| **Hyperlink Summary**   | Detects hyperlinks and counts them |
| **Subject Emotion**     | Identifies emotional and curiosity triggers |
| **Subject Explanation** | Explains detected emotion/curiosity |
| **Email Type**          | Classifies as Newsletter, Pitch, Q&A, etc. |
| **CTA Detection**       | Categorizes CTA (Sign Up, Login, Buy, Learn) |
| **Length**              | Word count of the email body |
| **Tone**                | Classifies tone as Casual or Formal |
| **Tone Explanation**    | Explains how tone was inferred |
| **Visuals**             | Detects presence of images |
| **Hook Style**          | Analyzes subject as Question, Statement, etc. |
| **Hook Explanation**    | Describes the hook logic |
| **Category**            | Educational, Promotional, Entertainment, Other |

---

## 📦 Technologies Used

- **Python 3.10+**
- **Google Gmail API**
- **TextBlob** – Sentiment analysis
- **BeautifulSoup4** – HTML parsing
- **Pandas** – DataFrame analysis
- **Regex** – Pattern matching
