# main.py

import json
from src.downloader import download_rule
from src.database_manager import get_latest_version, log_new_version
from src.comparator import compare_text
from src.analyzer import analyze_changes
from src.reporter import generate_html_report  # <--- NEW IMPORT

def load_rules():
    try:
        with open('data/tracked_rules.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: data/tracked_rules.json not found.")
        return []

def process_rule(rule):
    rule_id = rule['id']
    rule_name = rule['name']
    rule_url = rule['url']
    
    print(f"\n--- Checking Rule: {rule_id} ({rule_name}) ---")
    
    latest_text = download_rule(rule_url)
    if not latest_text:
        print(f"[{rule_id}] Skipping due to download failure.")
        return

    last_version_text = get_latest_version(rule_id)
    
    if not last_version_text:
        print(f"[{rule_id}] No baseline found. Initializing...")
        log_new_version(rule_id, latest_text, summary="Initial Baseline Version")
    else:
        print(f"[{rule_id}] Baseline found. Comparing...")
        changes = compare_text(last_version_text, latest_text)
        
        if changes:
            print(f"[{rule_id}] ALERT: Changes detected!")
            
            # 1. NLP Analysis (Keep this for the database log)
            analysis_results = analyze_changes(changes)
            import json
            analysis_json = json.dumps(analysis_results, indent=2)
            
            # 2. HTML Report Generation (NEW STEP)
            report_path = generate_html_report(rule_id, rule_name, last_version_text, latest_text)
            
            # 3. Log to DB
            log_new_version(rule_id, latest_text, summary=f"Changes detected. Report: {report_path}")
            
            print(f"[{rule_id}] HTML Redline Report generated at: {report_path}")
            
        else:
            print(f"[{rule_id}] No changes detected.")

def run_tracker():
    print("=== Starting SEC/FINRA Rule Tracker Portfolio Check ===")
    rules = load_rules()
    print(f"Loaded {len(rules)} rules to track.")
    
    for rule in rules:
        process_rule(rule)
        
    print("\n=== Portfolio Check Complete ===")

if __name__ == "__main__":
    run_tracker()