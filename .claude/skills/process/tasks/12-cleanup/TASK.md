# 12. Cleanup

- Run:
  ```
  python <TASK_DIR>/cleanup.py --workdir <WORKDIR> --url "<URL>"
  ```
  Omit `--url` if the URL was provided by the user (not from `backlog.txt`).
- The script deletes `WORKDIR` and removes the URL from `backlog.txt` if applicable.

## Scripts

- `cleanup.py` — deletes the working directory and cleans the backlog.
