---
name: format
description: Standardize note layout and typography for a professional look.
---

# Format Note

This skill ensures that all notes follow a consistent visual structure, with proper spacing and normalized formatting.

## Instructions

1.  **Read Note**
    -   Read the markdown content of the target note.

2.  **Apply Logic**
    -   Execute the script `scripts/format_note.py <File Path>`.
    -   This script performs:
        -   **Date Normalization**: Ensures `created: YYYY-MM-DD` format.
        -   **Typography Fixes**: Removes AI-specific artifacts (double spaces) and normalizes punctuation.
        -   **Spacing**: Ensures headers (`## Summary`, `## Key Points`, `## Review`) have proper blank lines before and after.
        -   **Style Enhancements**: Converts generic "Warning" blocks into professional **Obsidian Callouts** (`> [!WARNING]`).

3.  **Validate**
    -   Verify that the frontmatter is still valid YAML.
    -   Ensure no content was lost during the formatting process.

## Usage

To format a single note:
```bash
python scripts/format_note.py <path_to_note>
```

To format ALL notes in the vault:
```bash
python scripts/format_all_notes.py
```
