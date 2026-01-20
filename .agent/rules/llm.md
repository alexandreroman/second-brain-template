---
trigger: always_on
---

Any call to an LLM MUST always rely on Gemini with the `gemini-3-flash-preview` model. 
The `GEMINI_API_KEY` environment variable must be used (this key is typically defined in the `.env` file at the root of the project).
LLM processing should be executed in parallel whenever possible to optimize performance (e.g., when multiple files are being processed).