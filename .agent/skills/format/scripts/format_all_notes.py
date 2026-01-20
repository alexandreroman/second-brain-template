#!/usr/bin/env python3
"""
Batch format all notes in the library using format_note.py logic.
"""

import sys
from pathlib import Path

# Add script directory to path to import format_note
sys.path.insert(0, str(Path(__file__).parent))
from format_note import format_note

def main():
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent.parent.parent
    notes_dir = project_root / 'notes'
    
    if not notes_dir.exists():
        print(f"Notes directory not found: {notes_dir}")
        return
    
    formatted_count = 0
    total_count = 0
    
    print(f"Scanning for notes in: {notes_dir}")
    for md_file in notes_dir.rglob('*.md'):
        total_count += 1
        try:
            if format_note(md_file):
                formatted_count += 1
                print(f"✅ Formatted: {md_file.relative_to(notes_dir)}")
        except Exception as e:
            print(f"❌ Error formatting {md_file}: {e}")
    
    print(f"\nSummary: Processed {total_count} files, updated {formatted_count}.")

if __name__ == '__main__':
    main()
