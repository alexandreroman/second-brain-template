---
name: setup
description: Use this skill to initialize the user profile by asking a series of questions.
compatibility: Requires python, git, and pip
allowed-tools: Bash(python:*) Bash(git:*) Bash(pip:*)
---

# Setup Skill

This skill is used to set up the user's profile which is used by other skills (like `review`) to provide personalized experiences.

## Workflow

1.  **Verify External Tools**
    - Check that all required external tools are installed and accessible.
    - Required tools:
        - **python**: Used by all skills to run scripts.
        - **git**: Used by the commit skill to save changes to the repository.
    - For each tool, run a version check command (e.g., `python --version`, `git --version`).
    - If any tool is missing:
        - **STOP the initialization process immediately.**
        - Display a clear error message to the user listing the missing tools.
        - Provide installation instructions for each missing tool:
            - **git**: Download from https://git-scm.com/downloads or use a package manager (e.g., `winget install Git.Git` on Windows, `brew install git` on macOS, or `apt install git` on Linux).
        - Do NOT proceed to the next steps until all tools are available.

2. **Install Python Dependencies**
    - Install all required Python packages for the skills' scripts using a portable script.
    - Run: `python .claude/skills/setup/scripts/install_deps.py`
    - This script automatically finds and installs all `requirements.txt` files across all skills, ensuring compatibility with Windows, macOS, and Linux.

3.  **Ask Questions (in English)**
    - Ask the user for their:
        - First and last name
        - Profession
        - Current employer
        - Education
        - Current projects
        - Interests

4.  **Save Profile (in English)**
    - Format the answers into a structured text.
    - **The content of `profile.md` must be written in English.**
    - Save the result to `.profile.md` (at the project root).
