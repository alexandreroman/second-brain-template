# 5. Summarize Content

## 5a. Extract content

- If YouTube URL: `python <TASK_DIR>/extract_youtube.py "<SOURCE>" --output-file <WORKDIR>/prompt_summary.txt --metadata-file <WORKDIR>/metadata.json`
- Otherwise: `python <TASK_DIR>/extract_webpage.py "<SOURCE>" --output-file <WORKDIR>/prompt_summary.txt --metadata-file <WORKDIR>/metadata.json`

## 5b. Call LLM

- `python <SHARED>/ask_llm.py --prompt-file <WORKDIR>/prompt_summary.txt --output-file <WORKDIR>/raw_summary.txt --temperature 0.2`

## 5c. Parse result

- `python <TASK_DIR>/parse_summary.py --input-file <WORKDIR>/raw_summary.txt --metadata-file <WORKDIR>/metadata.json --output-file <WORKDIR>/summary.txt`

## Post-processing

- Read `<WORKDIR>/summary.txt` to get the content (with `TITLE:`, `THUMBNAIL:`, `LENGTH:` metadata lines).
- Variable: `ORIGINAL_TITLE` = the `TITLE:` value from the summary.
- Generate `NOTE_TITLE`: a short, concise summary of the content in English (max 10 words). Do NOT reuse the original title. This summary must capture the essence of the content in a neutral, descriptive way.

## Scripts

- `extract_webpage.py` — extracts content from a web page.
- `extract_youtube.py` — extracts transcript and metadata from a YouTube video.
- `parse_summary.py` — parses the LLM summary output.
- `<SHARED>/ask_llm.py` — shared LLM caller.
