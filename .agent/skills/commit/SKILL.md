---
name: commit
description: Commits changes to the git repository with a standardized message.
---

# Commit Changes

This skill performs a git commit of the current repository state, using a standardized message format based on the content title.

## Usage

Use the python script provided in the scripts directory.

```bash
python scripts/commit_changes.py "<Title>"
```

**Arguments:**
- `<Title>`: The title of the content that was added or processed. This will be used in the commit message: "Add content: <Title>".

## Behavior

1.  Checks for the existence of `notes` and `obsidian` directories (including the Obsidian Vault).
2.  Stages changes specifically within these directories.
3.  Checks if any changes were staged in these directories.
4.  If changes exist, commits **only** these paths with the message `Add content: <Title>`.
5.  All other files (like `backlog.txt` or scripts) are explicitly ignored and will not be included in the commit.
6.  If no changes exist in the target directories, it prints a message and exits without error.
