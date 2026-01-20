#!/usr/bin/env python3
"""
Format a markdown note for consistency and aesthetics.
Includes spacing, typography, date normalization, and callout styling.
Refined to strictly manage empty lines (collapsing duplicates) and header spacing.
"""

import os
import re
import sys
import argparse
from datetime import datetime
from pathlib import Path

# Fix Windows console encoding issues
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def format_note(file_path):
    """Apply full formatting to a markdown note."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # --- Global String Manipulations ---

    # 1. Normalize Dates in Frontmatter
    def normalize_date(match):
        date_str = match.group(1).strip()
        try:
            # Try to parse and re-format
            dt = datetime.fromisoformat(date_str.replace('/', '-'))
            return f"created: {dt.strftime('%Y-%m-%d')}"
        except:
            return match.group(0)

    content = re.sub(r'created:\s*([0-9\-/]+)', normalize_date, content)
    
    # 2. Typography: Fix AI artifacts
    # Replace double spaces (except for indented blocks/list items potentially? - simplified to global for now as originally requested)
    content = re.sub(r'(?<!\s)  (?!\s)', ' ', content)
    
    # 3. Callout Styling: Transform "Warning" blocks into Obsidian Callouts
    content = re.sub(
        r'> \*\*Warning\*\*:\s*(.*)', 
        r'> [!WARNING]\n> \1', 
        content, 
        flags=re.IGNORECASE
    )

    # 4. Typography: non-ASCII Replacement (dashes, quotes, ellipsis)
    replacements = [
        ('\u2014', '--'),   # Em dash
        ('\u2013', '-'),    # En dash
        ('\u201c', '"'),    # Left double quote
        ('\u201d', '"'),    # Right double quote
        ('\u2018', "'"),    # Left single quote
        ('\u2019', "'"),    # Right single quote
        ('\u2026', '...'),  # Ellipsis
        ('\u00A0', ' '),    # Non-breaking space
        ('\u0092', "'"),    # Windows-1252 right quote
        ('\u0091', "'"),    # Windows-1252 left quote
        ('\u0093', '"'),    # Windows-1252 left double
        ('\u0094', '"'),    # Windows-1252 right double
        ('\ufffd', ''),     # Replacement character
    ]
    
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)

    # --- Line-by-Line Structural Formatting ---
    
    lines = content.splitlines()
    new_lines = []
    
    in_frontmatter = False
    frontmatter_done = False
    in_code_block = False
    
    for i, line in enumerate(lines):
        striped = line.strip()
        
        # Frontmatter Logic
        if striped == '---':
            if not frontmatter_done:
                if not in_frontmatter:
                    in_frontmatter = True # Start of File
                else:
                    in_frontmatter = False
                    frontmatter_done = True
                new_lines.append(line)
                continue # Done with this line
            # If we see --- later, it might be a horizontal rule suitable for body
        
        if in_frontmatter:
            new_lines.append(line)
            continue
            
        # Code Block Logic
        if line.lstrip().startswith('```'):
            in_code_block = not in_code_block
            new_lines.append(line)
            continue
            
        if in_code_block:
            new_lines.append(line)
            continue
            
        # Body Logic
        
        # 1. Empty Lines: Collapse
        if striped == '':
            # If the last line added was also blank, skip this one
            if new_lines and new_lines[-1].strip() == '':
                continue
            new_lines.append('')
            continue
            
        # 2. Headers
        # Identify headers #, ##, ### etc followed by space
        # Or standard "Specific Headers" if we want to be strict, but general headers is better
        is_header = re.match(r'^#{1,6}\s', line)
        
        if is_header:
            # Ensure blank line BEFORE header
            # (Unless it's the very first line of body - i.e. previous line was ---)
            if new_lines and new_lines[-1].strip() != '' and new_lines[-1].strip() != '---':
                 new_lines.append('')
            elif new_lines and new_lines[-1].strip() == '---':
                 # Ensure separation from frontmatter? Usually one blank line is good.
                 # If new_lines has ---, append blank
                 new_lines.append('')

            new_lines.append(line)
            
            # Ensure blank line AFTER header
            # We add it proactively. The "Collapse" rule will prevent double blanks if next line is blank.
            new_lines.append('')
        else:
            # Standard Text
            new_lines.append(line)
            
    # --- Final Cleanup ---
    
    # Remove leading blank lines at start of file? (Unlikely due to frontmatter)
    # Remove trailing blank lines
    while new_lines and new_lines[-1].strip() == '':
        new_lines.pop()
    
    # Ensure exactly one trailing newline
    new_lines.append('')
    
    new_content = '\n'.join(new_lines)
    
    if new_content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    return False

def main():
    parser = argparse.ArgumentParser(description="Format a markdown note.")
    parser.add_argument("note_path", help="Path to the note file")
    args = parser.parse_args()
    
    try:
        note_path = Path(args.note_path)
        if not note_path.exists():
            print(f"Error: File not found: {note_path}", file=sys.stderr)
            sys.exit(1)
        
        changed = format_note(note_path)
        if changed:
            print(f"✅ Formatted successfully: {note_path}")
        else:
            print(f"✨ Note already formatted: {note_path}")
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
