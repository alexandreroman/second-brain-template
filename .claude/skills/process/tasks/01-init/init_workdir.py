import uuid
import sys
from pathlib import Path


def main():
    base = Path("tmp")
    workdir = base / uuid.uuid4().hex[:8]
    workdir.mkdir(parents=True, exist_ok=True)
    print(workdir)


if __name__ == "__main__":
    main()
