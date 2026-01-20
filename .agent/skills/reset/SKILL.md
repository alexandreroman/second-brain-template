---
name: reset
description: Reinitialize the project by deleting user profile, notes, and Obsidian vault
---

# Reset Skill

This skill reinitializes the second-brain project by removing all user data and content.

## What it does

1. **Deletes the user profile** (`profile.md`)
2. **Deletes all notes** (entire `notes` folder)
3. **Deletes the Obsidian vault** (entire `obsidian/vault` folder)

## Usage

When the user asks to reset the project or start fresh, use this skill to clean up all user-generated content.

## Implementation Steps

1. **Confirm with the user** before proceeding, as this operation is destructive and cannot be undone

2. **Determine the workspace root**:
   - Use the workspace path from user information (e.g., `alexandreroman/second-brain`)
   - This ensures portability across different operating systems

3. **Delete the user profile**:
   - Remove `<workspace-root>/profile.md`

4. **Delete all notes**:
   - Remove the entire `<workspace-root>/notes` directory

5. **Delete the Obsidian vault**:
   - Remove the entire `<workspace-root>/obsidian/vault` directory

6. **Confirm completion** and inform the user that the project has been reset

## Platform-Specific Commands

Use platform-appropriate commands based on the user's OS:

### Windows (PowerShell)
```powershell
Remove-Item -Path "<path>" -Recurse -Force -ErrorAction SilentlyContinue
```

### macOS/Linux (Bash)
```bash
rm -rf "<path>"
```

## Important Notes

- This operation is **irreversible** - all user data will be permanently deleted
- Always ask for explicit confirmation before executing
- After reset, the user may want to run the `init` skill to set up their profile again
- Consider suggesting a backup before proceeding with the reset

## Safety

- Use the `run_command` tool with OS-appropriate commands
- Check if files/directories exist before attempting to delete them using `list_dir` or `find_by_name`
- Provide clear feedback about what was deleted
- Handle errors gracefully (e.g., if a file/directory doesn't exist)
