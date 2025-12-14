# src/reporter.py

import difflib
import os
from datetime import datetime

def generate_html_report(rule_id, rule_name, old_text, new_text):
    """
    Generates a side-by-side HTML comparison (redline) of the old vs new text.
    Saves the file to the 'reports/' directory.
    """
    print(f"[{rule_id}] Generating HTML redline report...")
    
    # 1. Prepare the Data
    # difflib expects lists of strings (lines), not big text blocks
    old_lines = old_text.splitlines()
    new_lines = new_text.splitlines()
    
    # 2. Configure the HTML Generator
    d = difflib.HtmlDiff()
    
    # 3. Generate the HTML content
    # We provide a custom header and styling tweaks via 'wrapcolumn' if needed
    html_content = d.make_file(
        old_lines, 
        new_lines, 
        fromdesc=f"Baseline Version ({rule_id})", 
        todesc=f"New Version ({datetime.now().strftime('%Y-%m-%d')})",
        context=True,  # Show context lines around changes? (False = show everything)
        numlines=5     # If context=True, how many lines of context to show
    )
    
    # 4. Save to File
    filename = f"reports/{rule_id}_CHANGE_REPORT.html"
    
    # We can inject a little CSS to make it look modern
    # The default difflib style is a bit 1990s
    custom_css = """
    <style>
        body { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; padding: 20px; }
        h1 { color: #333; }
        .diff_header { background-color: #e0e0e0; }
        td.diff_header { text-align: right; }
        .diff_next { display: none; }
        .diff_add { background-color: #d4fcbc; }
        .diff_chg { background-color: #ffffcc; }
        .diff_sub { background-color: #ffcccc; }
    </style>
    """
    
    # Inject CSS into the head
    html_content = html_content.replace('<head>', f'<head>{custom_css}')
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_content)
        
    print(f"[{rule_id}] Report saved: {filename}")
    return filename
