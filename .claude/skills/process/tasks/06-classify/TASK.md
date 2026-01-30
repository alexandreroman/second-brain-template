# 6. Classify Content

## 6a. Build prompt

- `python <TASK_DIR>/build_classify_prompt.py --input-file <WORKDIR>/summary.txt --output-file <WORKDIR>/prompt_classify.txt`

## 6b. Call LLM

- `python <SHARED>/ask_llm.py --prompt-file <WORKDIR>/prompt_classify.txt --output-file <WORKDIR>/raw_classify.txt --response-type json --temperature 0.1`

## 6c. Parse result

- `python <TASK_DIR>/parse_classify.py --input-file <WORKDIR>/raw_classify.txt --output-file <WORKDIR>/classification.json`

## Post-processing

- Read `<WORKDIR>/classification.json` to get `type`, `tags`, `date`, `year`, `month`.
- Ignore the `filename` from classification. Instead, derive the filename from `NOTE_TITLE`: lowercase, replace spaces with hyphens, remove special characters, add `.md` extension.
- Variable: `FILENAME` = derived filename.

## Scripts

- `build_classify_prompt.py` — builds the classification prompt.
- `parse_classify.py` — parses the LLM classification output.
- `<SHARED>/ask_llm.py` — shared LLM caller.
