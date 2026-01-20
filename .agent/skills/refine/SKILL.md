---
name: refine
description: Use this skill to update or improve an existing note based on user feedback.
---

# Refine Note

This skill allows you to regenerate or modify parts of an existing note (Summary, Key Points, or Review) based on specific user instructions.

## Workflow

1.  **Identify Note**
    -   Locate the markdown file in `notes/` based on the user's request.

2.  **Read Context**
    -   Read the existing note content.
    -   Retrieve the original source URL from the frontmatter.
    -   Use `read_url_content` (or `scripts/analyze_youtube.py` for videos) to get the fresh/original content if needed.

3.  **Process Instructions**
    -   Apply the user's specific feedback (e.g., "Make the summary more technical", "Focus on the Spring Boot part", "Translate to French").

4.  **Update Note**
    -   Update the relevant sections in the source note in `notes/`.
    -   Preserve the existing frontmatter (especially `created` and `source`).

5.  **Re-run Quality Checks**
    -   Invoke the `format` skill on the updated note to ensure spacing and style are maintained.
    -   Invoke the `transform` skill to sync the changes to the Obsidian vault.

## Usage

Example requests:
- "/refine this note to focus more on the Kubernetes part"
- "/refine the summary of the last article to be in French"
- "/refine the review to reflect my new interest in Cloud Native"
