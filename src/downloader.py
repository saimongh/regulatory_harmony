# src/downloader.py

import requests
from bs4 import BeautifulSoup

def download_rule(url: str) -> str:
    """
    Fetches raw HTML and uses a 'Winner Takes All' strategy to find
    the main regulatory text body.
    """
    print(f"Attempting to download content from: {url}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the URL: {e}")
        return ""

    soup = BeautifulSoup(response.content, 'html.parser')
    
    # --- Robust Extraction Logic ---
    # We define a list of potential containers where rule text might live.
    # We will try ALL of them and keep the one with the most text.
    candidates = []
    
    # 1. Try specific Drupal/CMS content classes (common on gov/reg sites)
    candidates.append(soup.find('div', class_='field-name-body'))
    candidates.append(soup.find('div', class_='rule-book-content'))
    candidates.append(soup.find('div', id='block-system-main'))
    candidates.append(soup.find('article'))
    candidates.append(soup.find('main'))
    
    best_text = ""
    
    for content_area in candidates:
        if not content_area:
            continue
            
        # Extract text, stripping out empty lines
        current_text = content_area.get_text(separator='\n')
        
        # Simple Cleaning: Filter out obviously short/junk lines
        clean_lines = []
        for line in current_text.splitlines():
            line = line.strip()
            # Heuristic: Keep lines that aren't navigation links
            if len(line) > 5 and "Book traversal" not in line and "›" not in line:
                clean_lines.append(line)
        
        cleaned_candidate = "\n".join(clean_lines)
        
        # If this candidate has more text than our current best, it's the winner
        if len(cleaned_candidate) > len(best_text):
            best_text = cleaned_candidate

    if len(best_text) > 200:
        print(f"Successfully extracted {len(best_text)} characters.")
        return best_text
    else:
        # Fallback: If specific containers fail, grab all paragraphs in the body
        print("Standard containers empty. Attempting fallback paragraph scan...")
        all_paragraphs = soup.find_all('p')
        fallback_lines = [p.get_text().strip() for p in all_paragraphs if len(p.get_text().strip()) > 50]
        fallback_text = "\n".join(fallback_lines)
        
        if fallback_text:
             print(f"Fallback extracted {len(fallback_text)} characters.")
             return fallback_text
             
        print("Could not locate substantial content.")
        return ""