import sys
import json
import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Assemble a note from summary and classification.")
    parser.add_argument("--summary-file", required=True, help="Path to the summary file.")
    parser.add_argument("--classification-file", required=True, help="Path to the classification JSON.")
    parser.add_argument("--source", required=True, help="Source URL.")
    parser.add_argument("--note-title", required=True, help="Generated note title.")
    parser.add_argument("--filename", required=True, help="Derived filename.")
    parser.add_argument("--target-path", default="", help="Existing note path to update (empty for create).")
    args = parser.parse_args()

    with open(args.classification_file, "r", encoding="utf-8") as f:
        classification = json.load(f)

    with open(args.summary_file, "r", encoding="utf-8") as f:
        summary_lines = f.readlines()

    note_type = classification["type"]
    tags = classification["tags"]
    date = classification["date"]
    year = classification["year"]
    month = classification["month"]

    # Extract metadata lines from summary
    thumbnail = ""
    length = ""
    body_lines = []
    for line in summary_lines:
        if line.startswith("THUMBNAIL: "):
            thumbnail = line.split("THUMBNAIL: ", 1)[1].strip()
        elif line.startswith("LENGTH: "):
            length = line.split("LENGTH: ", 1)[1].strip()
        elif line.startswith("TITLE: "):
            pass  # skip, we use note_title
        else:
            body_lines.append(line)
    body = "".join(body_lines).strip()

    # Delete old note if updating
    if args.target_path:
        old = Path(args.target_path)
        if old.exists():
            old.unlink()
            print(f"Deleted {old}", file=sys.stderr)
        parts = old.parts
        if parts and parts[0] == "notes":
            obsidian_path = Path("obsidian", "vault", *parts[1:])
            if obsidian_path.exists():
                try:
                    obsidian_path.unlink()
                    print(f"Deleted {obsidian_path}", file=sys.stderr)
                except PermissionError:
                    print(f"Warning: Could not delete {obsidian_path} (permission denied)", file=sys.stderr)

    # Build note path
    note_path = Path("notes") / note_type / year / month / args.filename
    note_path.parent.mkdir(parents=True, exist_ok=True)

    # Build frontmatter
    tags_str = "[" + ", ".join(f'"{t}"' for t in tags) + "]"
    fm_lines = [
        "---",
        f"source: {args.source}",
        f"type: {note_type}",
        f"tags: {tags_str}",
        f"created: {date}",
    ]
    if thumbnail:
        fm_lines.append(f"thumbnail: {thumbnail}")
    if length:
        fm_lines.append(f"length: {length}")
    fm_lines.append("---")

    content = "\n".join(fm_lines) + f"\n\n# {args.note_title}\n\n{body}\n"

    with open(note_path, "w", encoding="utf-8") as f:
        f.write(content)

    # Print the note path to stdout for the caller
    print(note_path)


if __name__ == "__main__":
    main()
