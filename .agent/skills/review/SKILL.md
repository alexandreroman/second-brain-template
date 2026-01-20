---
name: review
description: Give my opinion on a note, taking into account my profile and interests.
---

# Review Note

This skill generates a personalized review for a note based on the user's profile (from the `about-me` skill) and appends it to the note.

## Workflow

1.  **Read User Profile**
    -   Use the `about-me` skill to retrieve the user's profile information.
    -   This will provide the user's background, skills, and interests.
    -   If the profile doesn't exist, the `about-me` skill will handle the error and prompt the user to run the `init` skill first.

2.  **Read Note**
    -   Read the target note file to understand its content, type, and tags.

3.  **Generate & Update Review**
    -   Use the script `scripts/review_note.py` to generate and apply the review.
    -   Pass the **content** of the user profile (retrieved in Step 1) to the script using the `--profile` argument.
    -   Use the `--update` flag to automatically append or replace the `## Review` section in the file.
    -   Example command: `python scripts/review_note.py "/path/to/note.md" --profile "User profile text..." --update`
    -   The prompt for the review takes into account:
        -   The user's technical stack (Java, Spring Boot, Spring AI, Cloud).
        -   The user's interests (AI, Java, Spring, Cloud Computing).
        -   The note's content and its relevance to the user.
        -   The global impact of the content on society and the evolution of technology in general.
        -   If the content does NOT match the user's profile, it is noted as a "curiosity".
    -   **CRITICAL**: The review should NEVER mention the user's employer or specific job title.


