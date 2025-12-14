# src/comparator.py

import difflib
from typing import List

def compare_text(old_text: str, new_text: str) -> List[str]:
    """
    Compares two strings of text line-by-line and returns a list of lines
    that represent additions or deletions (the changes).

    Args:
        old_text: The baseline text fetched from the database.
        new_text: The newly downloaded text from the website.

    Returns:
        A list of strings, where each string is a line showing a difference,
        prefixed with '+' (addition) or '-' (deletion).
    """
    print("Starting comparison of old and new rule versions...")
    
    # 1. Split text into lists of lines
    old_lines = old_text.splitlines()
    new_lines = new_text.splitlines()

    # 2. Use difflib SequenceMatcher to find differences
    differ = difflib.SequenceMatcher(None, old_lines, new_lines)
    
    changed_lines = []
    
    # 3. Iterate through the comparisons and capture changes
    #    The 'opcodes' method yields differences as tuples: (tag, i1, i2, j1, j2)
    #    Tags are 'replace', 'delete', 'insert', 'equal'
    for tag, i1, i2, j1, j2 in differ.get_opcodes():
        if tag == 'equal':
            continue
        
        if tag == 'delete':
            # Text was removed from the old version
            for line in old_lines[i1:i2]:
                changed_lines.append(f"- {line}")
        
        elif tag == 'insert':
            # New text was added to the new version
            for line in new_lines[j1:j2]:
                changed_lines.append(f"+ {line}")
                
        elif tag == 'replace':
            # Text was changed (delete the old, insert the new)
            changed_lines.append(f"--- REPLACED BLOCK ---")
            for line in old_lines[i1:i2]:
                changed_lines.append(f"- {line}")
            for line in new_lines[j1:j2]:
                changed_lines.append(f"+ {line}")
            changed_lines.append(f"--- END REPLACED BLOCK ---")

    print(f"Comparison finished. Found {len(changed_lines)} lines of changes.")
    return changed_lines

# End of comparator.py