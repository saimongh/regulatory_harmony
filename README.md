# SEC/FINRA Regulatory Compliance Tracker

A Python-based automated monitoring system designed to track, audit, and analyze changes in financial regulations (FINRA/SEC rules).

## ⚖️ Project Overview

In the dynamic landscape of financial regulation, staying compliant requires constant vigilance. This tool automates the monitoring of a portfolio of regulatory rulebooks. It establishes a baseline for regulatory text and runs scheduled comparisons to detect changes, deletions, or amendments.

When a change is detected, the system uses **Natural Language Processing (NLP)** to:

1.  **Identify** the exact lines modified.
2.  **Extract** key entities (dates, monetary thresholds, organizations).
3.  **Log** the change in an immutable SQLite audit trail.

## 🛠 Technology Stack

- **Python 3.10+**: Core logic and automation.
- **spaCy (NLP)**: Named Entity Recognition (NER) for legal text analysis.
- **SQLite**: Relational database for version control and audit logging.
- **BeautifulSoup4**: Robust web scraping with "Winner Takes All" content extraction strategies.
- **difflib**: Sequence matching algorithms for precise text comparison.

## 🚀 Key Features

- **Multi-Rule Portfolio**: Configurable via `tracked_rules.json` to monitor dozens of distinct rules simultaneously.
- **Robust Extraction**: Implements a "Winner Takes All" scraping strategy to handle inconsistent government website layouts.
- **Immutable Audit Log**: Maintains a `regulations.db` database with a `rule_id` foreign key to track history for specific regulations.
- **Intelligent Summarization**: Parses technical diffs into readable summaries highlighting "Added" vs. "Removed" entities.

## 📋 Usage

1.  **Configuration**: Add rules to `data/tracked_rules.json`:
    ```json
    [
      {
        "id": "FINRA-2111",
        "name": "Suitability",
        "url": "[https://www.finra.org/rules-guidance/rulebooks/finra-rules/2111](https://www.finra.org/rules-guidance/rulebooks/finra-rules/2111)"
      }
    ]
    ```
2.  **Execution**: Run the tracker to fetch baselines or compare against history.
    ```bash
    python3 main.py
    ```
3.  **Output**:
    - **First Run**: Initializes baseline in `data/regulations.db`.
    - **Subsequent Runs**: Compares live text vs. stored baseline.
    - **Alerts**: Prints a JSON summary of NLP-analyzed changes if detected.

## 🔮 Future Development

- **Cloud Deployment**: Containerize with Docker for AWS Lambda execution.
- **Email Integration**: Connect to SendGrid API for real-time compliance officer alerts.
