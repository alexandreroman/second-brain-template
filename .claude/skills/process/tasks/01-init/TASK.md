# 1. Initialize Environment

- Run: `python <TASK_DIR>/init_workdir.py`
- The script creates `tmp/<id>/` and prints the path to stdout.
- Variable: `WORKDIR` = the path printed by the script.
- Variable: `SHARED` = `.claude/skills/process/scripts`
- All temporary files for this execution MUST be placed in `WORKDIR`.

## Scripts

- `init_workdir.py` — creates the unique working directory.
