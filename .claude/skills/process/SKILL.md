---
name: process
description: Use this skill when you are asked to process a link.
allowed-tools: Bash(python:*) Bash(git:*) Bash(rm:tmp/*) Bash(rmdir:tmp/*) Read(tmp/**) Write(tmp/**) Edit(tmp/**)
---

# Process Link

This skill orchestrates the creation of a note in the second brain from a URL.

Each execution creates a dedicated subdirectory inside `tmp/` (e.g., `tmp/<id>/`) to isolate all temporary files. This allows parallel execution without conflicts.

## Variables

| Variable    | Value                                                            |
|-------------|------------------------------------------------------------------|
| `WORKDIR`   | `tmp/<id>` (unique per execution)                                |
| `SHARED`    | `.claude/skills/process/scripts`                                 |
| `TASK_DIR`  | `.claude/skills/process/tasks/<nn>-<name>` (resolved per task)   |

## Execution

**MANDATORY**: Before executing any step, you MUST create a visible task list to track progress.

### Option A: TaskCreate/TaskUpdate tools (preferred)

If the `TaskCreate` and `TaskUpdate` tools are available, use them:

1. Call `TaskCreate` for ALL 12 tasks below, with:
   - `subject`: the task name (e.g., "1. Initialize Environment")
   - `description`: the instructions file path (e.g., "Read and follow tasks/01-init/TASK.md")
   - `activeForm`: the present continuous form (e.g., "Initializing environment")
2. For each task:
   - Call `TaskUpdate` with `status: "in_progress"` BEFORE starting.
   - Read the corresponding `TASK.md` file and follow its instructions.
   - Call `TaskUpdate` with `status: "completed"` AFTER finishing.

### Option B: Markdown checklist (fallback)

If the task tools are NOT available, output a Markdown checklist at the start:

```
- [ ] 1. Initialize Environment
- [ ] 2. Determine Input
- [ ] 3. Clean URL
- [ ] 4. Check Existence
- [ ] 5. Summarize Content
- [ ] 6. Classify Content
- [ ] 7. Assemble Note
- [ ] 8. Review Note
- [ ] 9. Format Note
- [ ] 10. Transform to Obsidian
- [ ] 11. Commit Changes
- [ ] 12. Cleanup
```

Before each task, output: `▶ N. Task Name`
After each task, output: `✓ N. Task Name`

---

You MUST execute ALL tasks sequentially from 1 to 12. Do NOT stop mid-pipeline.

## Tasks

| #  | Task                      | Instructions                      |
|----|---------------------------|-----------------------------------|
| 1  | Initialize Environment    | `tasks/01-init/TASK.md`           |
| 2  | Determine Input           | `tasks/02-input/TASK.md`          |
| 3  | Clean URL                 | `tasks/03-clean/TASK.md`          |
| 4  | Check Existence           | `tasks/04-check/TASK.md`          |
| 5  | Summarize Content         | `tasks/05-summarize/TASK.md`      |
| 6  | Classify Content          | `tasks/06-classify/TASK.md`       |
| 7  | Assemble Note             | `tasks/07-assemble/TASK.md`       |
| 8  | Review Note               | `tasks/08-review/TASK.md`         |
| 9  | Format Note               | `tasks/09-format/TASK.md`         |
| 10 | Transform to Obsidian     | `tasks/10-transform/TASK.md`      |
| 11 | Commit Changes            | `tasks/11-commit/TASK.md`         |
| 12 | Cleanup                   | `tasks/12-cleanup/TASK.md`        |
