---
name: summarize
description: Generate a summary and key points from a text content.
---

# Summarize Link

This skill defines how to transform raw text content into a concise summary for a note.

## Instructions

1.  **Analyze Content**
    -   **Strict Source Constraint**: You MUST base the summary **EXCLUSIVELY** on the content retrieved from the provided URL. Do NOT use external knowledge, search results, or assumptions.
    -   **Ignore Promotional Content**: For social media posts, exclude any text or links that are promoting products or services. Focus on value-added content.
    -   **For YouTube Links**: MUST execute the script `scripts/analyze_youtube.py <url>` to generate the summary and timeline using the Gemini model. Use the output of this script as the content for the note. Captured `LENGTH:` and `THUMBNAIL:` outputs must be added to the note frontmatter.
    -   **For Other Links (e.g., Medium, Articles)**: MUST execute the script `scripts/analyze_webpage.py <url>` to generate the summary and key points using the Gemini model. Use the output of this script as the content for the note. Captured `THUMBNAIL:` output must be added to the note frontmatter.

2.  **Error Handling (CRITICAL)**
    -   If the content cannot be retrieved, the script fails, or the summary cannot be generated for ANY reason:
        -   **Capture the error message**: output by the script (e.g., in stderr).
        -   **MUST** add the tag `warning` to the note's frontmatter `tags` list.
        -   In the note body, explicitly state: `> **Warning**: Unable to generate summary. Cause: <Captured Error Message>`
        -   If no specific error message is captured, use: `> **Warning**: Unable to generate summary from the provided source.`
        -   Do NOT attempt to "fill in gaps" with outside information or hallucinatory content.

3.  **Generate Structure**
    -   Create a **Summary** section: A brief paragraph (3-5 lines) describing the main topic.
    -   Create a **Key Points** section: A bulleted list of the most important insights, arguments, or data points.
        -   *For Video content*: Prepend the approximate timestamp to each key point if available in the source (e.g., `[05:20] Key point description`).
    -   Create a **Quotes** section: Includes up to 3 relevant quotes from the source text (if applicable).

4.  **Tone & Style**
    -   Maintain a neutral, objective tone.
    -   Use concise language.
    -   Focus on long-term value for a "Second Brain" (retrievability).
