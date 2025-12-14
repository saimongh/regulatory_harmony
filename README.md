# ⚖️ Regulatory Harmony: SEC/FINRA Compliance Monitor

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://sec-rule-tracker-cxascf3jtfknzfvqi47mrs.streamlit.app/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![Status](https://img.shields.io/badge/Status-Live-success)](https://sec-rule-tracker-cxascf3jtfknzfvqi47mrs.streamlit.app/)

**A full-stack LegalTech application that automates the monitoring, analysis, and visualization of financial regulations.**

---

## 🚀 Live Demo
**Click here to launch the application:**
👉 **[View Live Dashboard](https://sec-rule-tracker-cxascf3jtfknzfvqi47mrs.streamlit.app/)**

---

## 🧐 The "Why"
In the high-stakes world of financial compliance, regulations (like FINRA Rule 2111 or SEC Reg BI) are not static documents. They evolve.

**The Problem:** Compliance officers and legal teams often rely on manual checks or expensive, opaque subscriptions to track these changes.
**The Solution:** I built **Regulatory Harmony** to bridge the gap between Law and Code. It is an automated engine that treats legal text as data, providing a 24/7 watchdog for regulatory drift without human intervention.

## ✨ Key Features

### 1. Automated Surveillance
* **Portfolio Tracking:** Monitors a configurable list of high-impact rules (defined in `tracked_rules.json`).
* **Intelligent Scraping:** Uses a "Winner-Takes-All" extraction algorithm to parse inconsistent government HTML structures and isolate legal text from boilerplate noise.

### 2. Natural Language Processing (NLP)
* **Entity Extraction:** Leverages **spaCy** to scan amendments for critical entities—specifically dates, monetary thresholds, and organization names.
* **Semantic Analysis:** Differentiates between "boilerplate" updates and material changes to the law.

### 3. "Dark Glass" User Experience
* **Dieter Rams x Cyberpunk:** The UI abandons the sterile white spreadsheets of traditional law for a sleek, **Dark Mode Glassmorphic** aesthetic.
* **Visual Redlines:** Features a custom-built comparison engine that renders side-by-side "redlines" (additions in Mint, deletions in Rose) directly in the browser.

---

## 🏗️ The Building Process & Architecture

This project was built in iterative stages, moving from a raw script to a cloud-native application.

### The Stack
* **Frontend:** [Streamlit](https://streamlit.io/) (Python-based web framework)
* **Backend Logic:** Python 3.10+
* **Database:** SQLite (Relational tracking of versions and history)
* **NLP Engine:** spaCy (`en_core_web_sm`)
* **Web Scraping:** BeautifulSoup4 & Requests

### Architecture Pipeline
1.  **Ingestion:** The system iterates through the target URL list, mimicking a legitimate browser User-Agent to bypass basic scrapers.
2.  **Normalization:** Raw HTML is cleaned, stripped of navigation links, and normalized into pure string data.
3.  **Comparison:** The new string is hashed and compared against the latest stored version in `regulations.db`.
4.  **Logging:** If a delta is detected, the new version is timestamped, analyzed for named entities, and committed to the immutable audit log.
5.  **Visualization:** The Streamlit dashboard queries the SQLite database to render the interactive timeline and redlines.

---

## 💻 Local Installation

If you prefer to run the monitoring engine on your own machine (to keep a persistent local database), follow these steps:

1.  **Clone the Repository**
    ```bash
    git clone [https://github.com/saimongh/sec-rule-tracker.git](https://github.com/saimongh/sec-rule-tracker.git)
    cd sec-rule-tracker
    ```

2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    python -m spacy download en_core_web_sm
    ```

3.  **Run the Dashboard**
    ```bash
    streamlit run dashboard.py
    ```

---

## ⚙️ Configuration

To add new rules to the tracker, simply edit `data/tracked_rules.json`. No code changes are required.

```json
[
    {
        "id": "FINRA-2111",
        "name": "Suitability",
        "url": "[https://www.finra.org/rules-guidance/rulebooks/finra-rules/2111](https://www.finra.org/rules-guidance/rulebooks/finra-rules/2111)"
    }
]
