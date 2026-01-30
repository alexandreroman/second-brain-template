import sys
import json
import argparse


def main():
    parser = argparse.ArgumentParser(description="Combine LLM response with metadata into final summary.")
    parser.add_argument("--input-file", required=True, help="Path to the raw LLM response.")
    parser.add_argument("--metadata-file", required=True, help="Path to the metadata JSON file.")
    parser.add_argument("--output-file", required=True, help="Path to write the final summary.")
    args = parser.parse_args()

    try:
        with open(args.input_file, "r", encoding="utf-8") as f:
            analysis = f.read()

        with open(args.metadata_file, "r", encoding="utf-8") as f:
            metadata = json.load(f)

        output_parts = []

        if metadata.get("length"):
            output_parts.append(f"LENGTH: {metadata['length']}")

        if metadata.get("thumbnail"):
            output_parts.append(f"THUMBNAIL: {metadata['thumbnail']}")

        output_parts.append(analysis)

        with open(args.output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(output_parts))

        print(f"Summary written to {args.output_file}", file=sys.stderr)

    except Exception as e:
        print(f"\n[!] Failed to parse summary.", file=sys.stderr)
        print(f"Cause: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
