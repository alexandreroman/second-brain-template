---
name: classify
description: Determine the appropriate category and file path for a note.
---

# Classify

This skill defines the logic for organizing notes by Type and Tags.

## Instructions

1.  **Determine Type**
    -   Analyze the source URL and content format.
    -   Select one type:
        -   `video` (e.g., YouTube, Vimeo)
        -   `article` (Text-based Webpages, Blogs, News)
        -   `post` (Social Media: LinkedIn, X, Bluesky)
        -   `code` (Code Repositories: GitHub, GitLab)

2.  **Determine Tags**
    -   Analyze the content summary.
    -   Select relevant tags from this **fixed list**:
        -   `ai`
        -   `dev`
        -   `kubernetes`
        -   `news`
        -   `opinion`: content where the author expresses an opinion on a given subject (usually using "I").
        -   `talk`: public sessions, conferences or webinars (not for workshops or courses).
        -   `tips`
        -   `workshop`: hands-on sessions, tutorials, or courses.
        -   `java`
        -   `spring`
        -   `temporal`
        -   `web`
        -   `social`: opinions on social media
        -   `tool`: interesting tool for personal use.
    -   *Only use tags from this list.*

3.  **Determine Length** (Optional)
    -   For `video` content, attempt to determine the total duration.
    -   Format: `MM:SS` or `HH:MM:SS`.
    -   Include this in the metadata if known.

4.  **Define Output Path**
    -   Structure: `../../../notes/<Type>/<Year>/<Month>/<Filename>.md`
    -   **Year**: Current year (e.g., `2025`).
    -   **Month**: Current month (two digits, e.g., `01`).
    -   **Filename**: Convert the title to kebab-case.
        -   Example: Title "The Future of AI" -> Filename `the-future-of-ai.md`

5.  **Validation**
    -   Ensure the directory `../../../notes/<Type>/<Year>/<Month>` exists (create if necessary).
    -   Check for existing files to avoid overwrites.
