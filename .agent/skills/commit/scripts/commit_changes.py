
import subprocess
import sys
import argparse
import os

def commit_changes(title):
    """
    Stages changes in 'notes' and 'obsidian' directories and commits them.
    """
    message = f"Add content: {title}"
    
    try:
        # Directories to include in the commit
        target_dirs = ["notes", "obsidian"]
        existing_dirs = [d for d in target_dirs if os.path.exists(d)]
        
        if not existing_dirs:
            print(f"None of the target directories ({', '.join(target_dirs)}) exist.")
            return

        # Stage changes only for specific directories
        subprocess.run(["git", "add"] + existing_dirs, check=True)
        
        # Check if there are staged changes specifically in these directories
        # This ensures we don't commit other staged files (like backlog.txt)
        diff_result = subprocess.run(
            ["git", "diff", "--cached", "--quiet", "--"] + existing_dirs, 
            capture_output=True
        )
        
        if diff_result.returncode == 0:
            print(f"No changes in {', '.join(existing_dirs)} to commit.")
            return

        # Commit changes ONLY for specific directories
        # This explicitly ignores any other files that might be staged (e.g., backlog.txt)
        subprocess.run(["git", "commit", "-m", message, "--"] + existing_dirs, check=True)
        
        print(f"Successfully committed changes in {', '.join(existing_dirs)} with message: '{message}'")
        
    except subprocess.CalledProcessError as e:
        print(f"Error executing git command: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Commit changes in notes and obsidian folders.")
    parser.add_argument("title", help="The title of the content being added.")
    args = parser.parse_args()
    
    commit_changes(args.title)
