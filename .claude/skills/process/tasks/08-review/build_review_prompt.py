import sys
import os
import argparse


PROMPT_TEMPLATE = """
You are an expert personalized assistant.
Your task is to write a brief "Review" of a note from my perspective, as if I wrote it myself.

### My Profile:
{profile}

### Note Content:
{note}

### Instructions:
1. Provide a concise review (4-6 sentences) in the first person singular ("I").
2. **Personal Link**: Explain why this note is relevant (or not) to you, reflecting your technical background and interests.
3. **Global Perspective**: Include a perspective on how this content impacts the world, society, or the broader evolution of technology.
4. **NEVER** use the '—' (em dash) character in your output. Replace it with a contextual equivalent (such as commas, colons, or parentheses) depending on the sentence structure. NEVER use a simple dash '-' as a replacement for an em dash.
5. **CRITICAL**: Do NOT mention your employer, your current position, or your job title. Focus entirely on the technical or thematic relevance to your interests and skills.
6. **Logic for Non-Matching Content**: If the content does not align with your core skills or current projects, identify it as a "curiosity" that you are keeping for potential future use or broader knowledge.
7. The review must be in English.
8. Output ONLY the markdown for the review section, starting with `## Review`. Do NOT wrap your response in code fences (``` or ```markdown).

Example Output (Relevant):
## Review

This content is highly relevant to my interest in [topic], particularly as it relates to [skill/interest]. I see great potential in applying these concepts to my current work with [tech stack]. On a global scale, this shift towards [technology] highlights a significant evolution in how society interacts with [system], potentially democratizing access to [resource]. It's a valuable deep dive into [subject] that reflects the accelerating pace of technological change.

Example Output (Curiosity):
## Review

While this doesn't directly connect to my current projects in [field], I find it to be an interesting curiosity worth keeping. Exploring [topic] provides a fresh perspective on [related field] and might prove useful for future explorations. Broadly speaking, this development underscores the increasing overlap between [Field A] and [Field B], a trend that is reshaping industries worldwide. It's good to have this context in my knowledge base.
"""


def main():
    parser = argparse.ArgumentParser(description="Build a review prompt from note and profile.")
    parser.add_argument("--note-file", required=True, help="Path to the note file.")
    parser.add_argument("--profile-file", required=True, help="Path to the user profile file.")
    parser.add_argument("--output-file", required=True, help="Path to write the prompt.")
    args = parser.parse_args()

    try:
        if not os.path.exists(args.note_file):
            raise FileNotFoundError(f"Note file not found: {args.note_file}")
        if not os.path.exists(args.profile_file):
            raise FileNotFoundError(f"Profile file not found: {args.profile_file}")

        with open(args.note_file, "r", encoding="utf-8") as f:
            note = f.read()

        with open(args.profile_file, "r", encoding="utf-8") as f:
            profile = f.read()

        prompt = PROMPT_TEMPLATE.format(profile=profile, note=note)

        with open(args.output_file, "w", encoding="utf-8") as f:
            f.write(prompt)

        print(f"Prompt written to {args.output_file}", file=sys.stderr)

    except Exception as e:
        print(f"\n[!] Failed to build review prompt.", file=sys.stderr)
        print(f"Cause: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
