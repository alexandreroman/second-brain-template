# 7. Assemble Note

- Run:
  ```
  python <TASK_DIR>/assemble_note.py \
    --summary-file <WORKDIR>/summary.txt \
    --classification-file <WORKDIR>/classification.json \
    --source "<SOURCE>" \
    --note-title "<NOTE_TITLE>" \
    --filename "<FILENAME>" \
    --target-path "<TARGET_PATH>"
  ```
  Omit `--target-path` if `ACTION` is `Create`.
- The script:
  - Deletes the old note and its obsidian counterpart (if updating).
  - Creates the directory structure and writes the assembled note.
  - Prints the note path to stdout.
- Variable: `NOTE_PATH` = the path printed by the script.

## Scripts

- `assemble_note.py` — assembles the note from summary, classification, and metadata.
