---
name: transform
description: Creates Obsidian notes from project notes, adding internal links.
---

# Transform

This skill allows transforming raw notes present in the `../../../notes/` directory into a format optimized for Obsidian, placed in `../../../obsidian/vault/`.

## Features

1.  **Internal Link Generation**: The skill analyzes the content of each note and automatically creates Obsidian links (`[[Title]]`) to other existing notes when a title is mentioned.
2.  **Structure Preservation**: The directory hierarchy is maintained during the copy to the Obsidian Vault.
3.  **Bulk Processing**: All notes are processed to ensure maximum interconnectivity.

## Usage

To transform the notes, run the following script:

```bash
python scripts/transform_to_obsidian.py
```

## Agent Instructions

1.  When the user asks to "transform", "sync to Obsidian", or "create Obsidian notes":
2.  Run the `scripts/transform_to_obsidian.py` script.
3.  Verify that the files have been created in `../../../obsidian/vault/`.
4.  Confirm to the user that the transformation is complete.

## Technical Details

-   The script uses titles (`# Title`) to identify link targets.
-   It avoids self-linking (a note does not link to itself).
-   It preserves existing metadata (frontmatter).
