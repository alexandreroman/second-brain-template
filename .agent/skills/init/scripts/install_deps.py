import os
import subprocess
import sys
from pathlib import Path

def install_requirements():
    """Finds and installs all requirements.txt files in the skills directory."""
    # Base directory for skills (relative to this script)
    # This script is at .agent/skills/init/scripts/install_deps.py
    # Skills root is at .agent/skills/
    scripts_dir = Path(__file__).parent
    skills_root = scripts_dir.parent.parent
    
    print(f"Searching for requirements.txt in {skills_root}...")
    
    requirements_files = list(skills_root.rglob('requirements.txt'))
    
    if not requirements_files:
        print("No requirements.txt files found.")
        return

    for req_file in requirements_files:
        print(f"Installing dependencies from {req_file.relative_to(skills_root.parent.parent)}...")
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", str(req_file)],
                check=True
            )
        except subprocess.CalledProcessError as e:
            print(f"Error installing dependencies from {req_file}: {e}", file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    install_requirements()
