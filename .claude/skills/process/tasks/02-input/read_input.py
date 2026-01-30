import sys
from pathlib import Path


def main():
    # Check if URL was provided as argument
    if len(sys.argv) > 1:
        url = sys.argv[1].strip()
        if url:
            print(url)
            return

    # Read from backlog.txt
    backlog_file = Path("backlog.txt")

    if not backlog_file.exists():
        print("ERROR: No URL provided and backlog.txt not found", file=sys.stderr)
        sys.exit(1)

    lines = backlog_file.read_text(encoding="utf-8").splitlines()

    # Find first non-comment, non-empty URL
    url = None

    for line in lines:
        line = line.strip()
        # Skip empty lines and comments
        if line and not line.startswith("#"):
            url = line
            break

    if not url:
        print("ERROR: No URL found in backlog.txt", file=sys.stderr)
        sys.exit(1)

    print(url)


if __name__ == "__main__":
    main()
