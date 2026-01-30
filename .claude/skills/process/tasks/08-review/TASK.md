# 8. Review Note

## 8a. Get profile

- Read `.profile.md` at the project root. If it does not exist, skip this task.

## 8b. Build prompt

- `python <TASK_DIR>/build_review_prompt.py --note-file <NOTE_PATH> --profile-file .profile.md --output-file <WORKDIR>/prompt_review.txt`

## 8c. Call LLM

- `python <SHARED>/ask_llm.py --prompt-file <WORKDIR>/prompt_review.txt --output-file <WORKDIR>/raw_review.txt --temperature 0.7`

## 8d. Insert review

- `python <TASK_DIR>/parse_review.py --input-file <WORKDIR>/raw_review.txt --note-file <NOTE_PATH>`

## Scripts

- `build_review_prompt.py` — builds the review prompt from the note and profile.
- `parse_review.py` — inserts the review section into the note.
- `<SHARED>/ask_llm.py` — shared LLM caller.
