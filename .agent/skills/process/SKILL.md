---
name: process
description: Use this skill when you are asked to process a link.
---

# Process Link

This skill processes a URL provided by the user into a structured note in the second brain.

## Workflow

1.  **Determine Input**
    -   **If a URL is provided by the user**:
        -   Proceed to process that single URL.
    -   **If NO URL is provided**:
        -   Read the file `../../../backlog.txt`.
        -   Extract all non-empty lines; each line is a URL.
        -   Ignore lines starting with `#` (comments).
        -   Iterate through each URL and perform the following steps.

2.  **Clean URL**
    -   Execute the script `scripts/clean_url.py <URL>` to remove unnecessary parameters (`utm`, `t`, `pp`, etc.).
    -   Use this **Cleaned URL** for content retrieval and as the `source` metadata.
    -   *Keep track of the **Original URL** for backlog cleanup.*

3.  **Check Existence**
    -   Use the `grep_search` tool:
        -   Query: `source: <Cleaned URL>`
        -   SearchPath: `../../../notes/`
    -   **If found**:
        -   Set **Target File** to the retrieved file path.
        -   Read the file to extract the original `created` date.
        -   Set **Action** to `Update`.
    -   **If NOT found**:
        -   Set **Action** to `Create`.


4.  **Create Summary**
    -   **Refer to specific instructions in the `summarize` skill.**
    -   Follow the structure defined there (Summary + Key Points).

5.  **Classify Content**
    -   **Refer to specific instructions in the `classify` skill.**
    -   Determine the **Type** and **Tags**.
    -   **File Path**:
        -   If **Action** is `Update`: Use **Target File** from Step 3.
        -   If **Action** is `Create`: Derive per `classify` skill instructions.

6.  **Create Note**
    -   Compose the Markdown file.
    -   **Extract Title**:
        -   Look for a line starting with `TITLE:` in the output from the `summarize` step.
        -   Use the text following `TITLE:` as the **Title** of the note (and the file name).
        -   **Remove** the `TITLE:` line from the content body to avoid duplication.
    -   **Frontmatter**:
        -   *Note: If **Update**, preserve the original `created` date.*
        ```markdown
        ---
        created: <YYYY-MM-DD>
        source: <URL>
        type: <Type>
        tags: [<Tag1>, <Tag2>]
        length: <Length> (optional)
        thumbnail: <Thumbnail URL> (optional)
        ---
        ```
    -   **Content**:
        ```markdown
        # <Title>

        <Content from summarize step (without TITLE line)>
        ```
    -   **Save**: Use the `write_to_file` tool to save the note to the **File Path**.

7.  **Create Review**
    -   **Refer to specific instructions in the `review` skill.**
    -   Execute the `review_note.py` script with the `--update` flag to generate and append the review to the note.


8.  **Format Note**
    -   **Refer to specific instructions in the `format` skill.**
    -   Execute the script `../format/scripts/format_note.py <File Path>`.

9.  **Cleanup Backlog** (If applicable)
    -   **If the URL came from `backlog.txt`**:
    -   Remove the **Original URL** from the `backlog.txt` file.
    -   Ensure the file is updated immediately after processing the link to track progress.

10. **Transform to Obsidian**
    -   **Refer to specific instructions in the `transform` skill.**
    -   Invoke the transformation process to ensure the new note is available in Obsidian with appropriate internal links and the review section.

11. **Commit Changes**
    -   **Refer to specific instructions in the `commit` skill.**
    -   Execute the commit script using the **Title** of the note.

