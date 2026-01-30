# 4. Check Existence

- Search for `SOURCE` in the `source:` frontmatter field of all notes under `notes/`.
- Collect ALL matching file paths into a list.
- If multiple notes share the same `SOURCE`, keep the most recent one and delete the others (both from `notes/` and `obsidian/vault/`).
- Variable: `ACTION` = `Create` (no match) or `Update` (one match found or kept).
- Variable: `TARGET_PATH` = remaining file path (if `Update`) or empty (if `Create`).
