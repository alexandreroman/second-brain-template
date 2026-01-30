import sys
import shutil
import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Clean up after processing.")
    parser.add_argument("--workdir", required=True, help="Path to the working directory to delete.")
    parser.add_argument("--url", default="", help="URL to remove from backlog.txt (if applicable).")
    args = parser.parse_args()

    workdir = Path(args.workdir)
    if workdir.exists():
        shutil.rmtree(workdir)
        print(f"Deleted {workdir}", file=sys.stderr)

    if args.url:
        backlog = Path("backlog.txt")
        if backlog.exists():
            lines = backlog.read_text(encoding="utf-8").splitlines()
            lines = [l for l in lines if l.strip() != args.url.strip()]
            backlog.write_text("\n".join(lines) + "\n" if lines else "", encoding="utf-8")
            print(f"Removed {args.url} from backlog.txt", file=sys.stderr)


if __name__ == "__main__":
    main()
