import sys
import os
import argparse


def main():
    parser = argparse.ArgumentParser(description="Insert LLM review into a note.")
    parser.add_argument("--input-file", required=True, help="Path to the raw LLM response.")
    parser.add_argument("--note-file", required=True, help="Path to the note file to update.")
    args = parser.parse_args()

    try:
        if not os.path.exists(args.note_file):
            raise FileNotFoundError(f"Note file not found: {args.note_file}")

        with open(args.input_file, "r", encoding="utf-8") as f:
            review = f.read().strip()

        with open(args.note_file, "r", encoding="utf-8") as f:
            note_content = f.read()

        if "## Review" in note_content:
            parts = note_content.split("## Review")
            new_content = parts[0].rstrip() + "\n\n" + review + "\n"
        else:
            new_content = note_content.rstrip() + "\n\n" + review + "\n"

        with open(args.note_file, "w", encoding="utf-8") as f:
            f.write(new_content)

        print(f"Review updated in {args.note_file}", file=sys.stderr)

    except Exception as e:
        print(f"\n[!] Failed to parse review.", file=sys.stderr)
        print(f"Cause: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
