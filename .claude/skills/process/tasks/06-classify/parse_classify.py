import sys
import json
import argparse
from datetime import datetime


def main():
    parser = argparse.ArgumentParser(description="Parse LLM classification response.")
    parser.add_argument("--input-file", required=True, help="Path to the raw LLM response.")
    parser.add_argument("--output-file", required=True, help="Path to write the classification JSON.")
    args = parser.parse_args()

    try:
        with open(args.input_file, "r", encoding="utf-8") as f:
            raw = f.read()

        data = json.loads(raw)

        now = datetime.now()
        data["date"] = now.strftime("%Y-%m-%d")
        data["year"] = now.strftime("%Y")
        data["month"] = now.strftime("%m")

        with open(args.output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        print(f"Classification written to {args.output_file}", file=sys.stderr)

    except Exception as e:
        print(f"\n[!] Failed to parse classification.", file=sys.stderr)
        print(f"Cause: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
