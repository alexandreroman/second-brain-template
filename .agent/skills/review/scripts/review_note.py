import os
import sys
import argparse
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load environment variables
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

def generate_review(note_content, profile_content):
    if not API_KEY:
        raise Exception("GEMINI_API_KEY environment variable not set.")

    client = genai.Client(
        api_key=API_KEY,
        http_options=types.HttpOptions(timeout=30000)
    )

    prompt = f"""
You are an expert personalized assistant.
Your task is to write a brief "Review" of a note from my perspective, as if I wrote it myself.

### My Profile:
{profile_content}

### Note Content:
{note_content}

### Instructions:
1. Provide a concise review (4-6 sentences) in the first person singular ("I").
2. **Personal Link**: Explain why this note is relevant (or not) to you, reflecting your technical background and interests.
3. **Global Perspective**: Include a perspective on how this content impacts the world, society, or the broader evolution of technology.
4. **CRITICAL**: Do NOT mention your employer, your current position, or your job title. Focus entirely on the technical or thematic relevance to your interests and skills.
5. **Logic for Non-Matching Content**: If the content does not align with your core skills or current projects, identify it as a "curiosity" that you are keeping for potential future use or broader knowledge.
6. The review must be in English.
7. Output ONLY the markdown for the review section, starting with `## Review`.

Example Output (Relevant):
## Review

This content is highly relevant to my interest in [topic], particularly as it relates to [skill/interest]. I see great potential in applying these concepts to my current work with [tech stack]. On a global scale, this shift towards [technology] highlights a significant evolution in how society interacts with [system], potentially democratizing access to [resource]. It's a valuable deep dive into [subject] that reflects the accelerating pace of technological change.

Example Output (Curiosity):
## Review

While this doesn't directly connect to my current projects in [field], I find it to be an interesting curiosity worth keeping. Exploring [topic] provides a fresh perspective on [related field] and might prove useful for future explorations. Broadly speaking, this development underscores the increasing overlap between [Field A] and [Field B], a trend that is reshaping industries worldwide. It's good to have this context in my knowledge base.
"""

    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=[prompt],
        config=types.GenerateContentConfig(
            temperature=0.7
        )
    )
    
    return response.text.strip()

def main():
    parser = argparse.ArgumentParser(description="Generate a personalized review for a note.")
    parser.add_argument("note_path", help="Path to the note file")
    parser.add_argument("--profile", help="User profile content", required=True)
    parser.add_argument("--update", action="store_true", help="Update the note file directly with the review")
    args = parser.parse_args()
    
    try:
        with open(args.note_path, 'r', encoding='utf-8') as f:
            note_content = f.read()
        
        profile_content = args.profile
            
        review = generate_review(note_content, profile_content)
        
        if args.update:
            # Check if ## Review already exists
            if "## Review" in note_content:
                # Replace everything from ## Review to the end
                parts = note_content.split("## Review")
                new_content = parts[0].rstrip() + "\n\n" + review + "\n"
            else:
                # Append to the end
                new_content = note_content.rstrip() + "\n\n" + review + "\n"
                
            with open(args.note_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Review updated in {args.note_path}")
        else:
            print(review)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
