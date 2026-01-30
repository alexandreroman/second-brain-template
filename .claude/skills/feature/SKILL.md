---
name: feature
description: Mark a note as important by adding the 'featured' tag.
---

# Feature Note

This skill adds the `featured` tag to a specific note to mark it as important or featured.

## Instructions

1.  **Identify Note**
    -   Locate the markdown file corresponding to the user's request (by filename or path).
    -   If the path is not provided, search for the note by title.

2.  **Edit Frontmatter**
    -   Read the file content.
    -   Parse the YAML Frontmatter.
    -   Check the `tags` list.
    -   **Action**:
        -   If `tags` exists: Append `featured` if it's not already present.
        -   If `tags` does not exist: Create the field `tags: [featured]`.

3.  **Save Changes**
    -   Update the file with the modified Frontmatter.
    -   Preserve the rest of the file content exactly as is.
