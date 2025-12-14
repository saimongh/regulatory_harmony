# src/analyzer.py

import spacy
from typing import List, Dict

# Load the small English model (must be done only once)
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Error: spaCy model 'en_core_web_sm' not found. Did you run 'python3 -m spacy download en_core_web_sm'?")
    # Exit or handle error

def analyze_changes(changed_lines: List[str]) -> Dict[str, any]:
    """
    Analyzes the changed lines for named entities (dates, money, organizations)
    and summarizes the changes.

    Args:
        changed_lines: List of strings prefixed with '+' or '-' (add/remove).

    Returns:
        A dictionary containing the summary and extracted entities.
    """
    print("\nStarting NLP analysis of rule changes...")
    
    analysis = {
        'summary': "Rule change detected. NLP analysis completed.",
        'added_entities': {},
        'removed_entities': {},
        'raw_changes': changed_lines
    }
    
    # Concatenate all new (+) and removed (-) lines separately for spaCy processing
    added_text = " ".join([line[2:] for line in changed_lines if line.startswith('+')])
    removed_text = " ".join([line[2:] for line in changed_lines if line.startswith('-')])

    # Process ADDED text
    if added_text:
        doc_added = nlp(added_text)
        analysis['added_entities'] = extract_entities(doc_added)
        
    # Process REMOVED text
    if removed_text:
        doc_removed = nlp(removed_text)
        analysis['removed_entities'] = extract_entities(doc_removed)
        
    print("NLP analysis finished.")
    return analysis

def extract_entities(doc) -> Dict[str, List[str]]:
    """Helper function to extract named entities of interest."""
    entities = {
        'DATE': [],
        'MONEY': [],
        'ORG': [],   # Organizations/Agencies (e.g., SEC, FINRA)
        'GPE': [],   # Geopolitical Entities (Locations)
        'LAW': []    # Named laws, acts, or specific rule sections
    }
    
    for ent in doc.ents:
        if ent.label_ in entities:
            entities[ent.label_].append(ent.text)
            
    # Remove duplicates
    for key in entities:
        entities[key] = sorted(list(set(entities[key])))
        
    return entities

# End of analyzer.py