import sys
import argparse


PROMPT_TEMPLATE = """
You are a content classification assistant for a "Second Brain" knowledge base.
Analyze the provided text content to determine its Type and Tags.

Valid Types:
- video: For YouTube videos, Vimeo, or transcripts.
- article: For standard blog posts, news articles, documentation.
- post: For social media content (LinkedIn, Twitter/X, Bluesky).
- code: For GitHub repositories, gists, or code snippets.

Valid Tags (Select all that apply, but ONLY from this list):
- ai: Artificial Intelligence, Machine Learning, LLMs.
- dev: Software development, programming languages, frameworks (except Java/Spring/Temporal).
- ops: Platforms (Docker, Kubernetes, VM) and platform management practices.
- kubernetes: Specifically related to Kubernetes.
- java: Java programming language.
- spring: Spring Framework, Spring Boot, Spring AI.
- temporal: Temporal.io, durable execution.
- security: Cybersecurity, best practices, vulnerabilities.
- tool: Useful tools, CLIs, SaaS products.
- tips: Short tips, tricks, or hacks.
- workshop: Tutorial-style content, hands-on guides.
- talk: Conference talks, presentations.
- news: Industry news, announcements.
- opinion: Personal thoughts, essays, analyses.
- web: Web development, frontend, browsers.
- social: Content about social media or from social platforms.

Instructions:
1. Read the content.
2. Determine the Type based on the content source and format.
3. Select relevant Tags from the valid list.
4. Output the result in pure JSON format. Do NOT wrap your response in code fences (``` or ```json).

CONTENT START:
{content}
CONTENT END

Output JSON Format:
{{
    "type": "one_of_the_valid_types",
    "tags": ["tag1", "tag2"]
}}
"""


def main():
    parser = argparse.ArgumentParser(description="Build a classification prompt.")
    parser.add_argument("--input-file", required=True, help="Path to the content file.")
    parser.add_argument("--output-file", required=True, help="Path to write the prompt.")
    args = parser.parse_args()

    try:
        with open(args.input_file, "r", encoding="utf-8") as f:
            content = f.read()

        prompt = PROMPT_TEMPLATE.format(content=content[:50000])

        with open(args.output_file, "w", encoding="utf-8") as f:
            f.write(prompt)

        print(f"Prompt written to {args.output_file}", file=sys.stderr)

    except Exception as e:
        print(f"\n[!] Failed to build classification prompt.", file=sys.stderr)
        print(f"Cause: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
