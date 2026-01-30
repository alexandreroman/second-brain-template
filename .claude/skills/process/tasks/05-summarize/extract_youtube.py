import sys
import re
import json
import argparse
import cloudscraper
from bs4 import BeautifulSoup
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import NoTranscriptFound


def extract_video_id(url):
    """Extracts the video ID from a YouTube URL."""
    pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    return None


def get_transcript(video_id):
    """Fetches the transcript for a given video ID."""
    yt = YouTubeTranscriptApi()
    transcript_list = yt.list(video_id)

    transcript_obj = None

    try:
        transcript_obj = transcript_list.find_transcript(['en', 'en-US', 'en-GB'])
    except NoTranscriptFound:
        try:
            transcript_obj = transcript_list.find_transcript(['fr', 'fr-FR'])
        except NoTranscriptFound:
            for t in transcript_list:
                transcript_obj = t
                break

    if not transcript_obj:
        raise Exception("No suitable transcript found.")

    transcript = transcript_obj.fetch()

    formatted_text = ""
    total_duration = 0
    snippets = list(transcript)

    if snippets:
        last_entry = snippets[-1]
        total_duration = int(last_entry.start + last_entry.duration)

    for entry in snippets:
        start_time = int(entry.start)
        minutes = start_time // 60
        seconds = start_time % 60
        timestamp = f"[{minutes:02d}:{seconds:02d}]"
        formatted_text += f"{timestamp} {entry.text}\n"

    hours = total_duration // 3600
    minutes = (total_duration % 3600) // 60
    seconds = total_duration % 60
    if hours > 0:
        length_str = f"{hours}:{minutes:02d}:{seconds:02d}"
    else:
        length_str = f"{minutes:02d}:{seconds:02d}"

    return formatted_text, length_str


def get_video_title(url):
    """Fetches the title of a YouTube video without a browser."""
    try:
        scraper = cloudscraper.create_scraper()
        response = scraper.get(url, timeout=(10, 30))
        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.text, 'html.parser')

        meta_title = soup.find("meta", attrs={"property": "og:title"}) or soup.find("meta", attrs={"name": "title"})
        if meta_title and meta_title.get("content"):
            return meta_title["content"]

        if soup.title:
            title = soup.title.string
            return re.sub(r" - YouTube$", "", title).strip()

        return None
    except Exception:
        return None


PROMPT_TEMPLATE = """
You are an expert content analysis assistant.
Analyze the following YouTube video transcript and provide a structured report.

IMPORTANT: PROVIDE ALL OUTPUT IN ENGLISH, regardless of the language of the transcript or the video title.

IMPORTANT: Convert any non-ASCII characters (including emojis) in your output to their nearest ASCII equivalent. If no equivalent exists, remove the character entirely. Ensure the final output contains only ASCII characters.

IMPORTANT: NEVER use the '—' (em dash) character in your output. Replace it with a contextual equivalent (such as commas, colons, or parentheses) depending on the sentence structure. NEVER use a simple dash '-' as a replacement for an em dash.

Video URL: {url}
Original Title: {title}

TRANSCRIPT START:
{transcript}
TRANSCRIPT END

1. **English Title**: Translate the "Original Title" to English if it is not already. If it is in English, use it as is.
2. **Summary**: A concise paragraph (3-5 lines) summarizing the main topic and objective of the video based exclusively on the transcript.
   - When referencing titles or specific terms in quotes, place punctuation (commas, periods) OUTSIDE the quotation marks, not inside.
   - Example: titled "Example Title", NOT titled "Example Title,"
3. **Key Points with Timeline**: A list of essential points covered, using the timestamps provided in the transcript output.
4. **Quotes**: Extract up to 3 relevant quotes from the transcript.
   - If the transcript is short or lacks impactful quotes, this section can be omitted.
   - Prioritize quotes that capture the essence of the video or provide significant insight.

IMPORTANT: Output raw Markdown directly. Do NOT wrap your response in code fences (``` or ```markdown). Your response must start with "TITLE:" directly.

Desired Output Format (Markdown):

TITLE: [English Title]

## Summary

[Your summary here]

## Key Points

- [MM:SS] **Theme or Topic**: Brief description (do not add commas or other punctuation before the colon).
- [MM:SS] **Theme or Topic**: Brief description (do not add commas or other punctuation before the colon).
...

## Quotes

> "First quote here."

> "Second quote here."

> "Third quote here."
"""


def main():
    parser = argparse.ArgumentParser(description="Extract YouTube transcript and build analysis prompt.")
    parser.add_argument("url", help="YouTube video URL")
    parser.add_argument("--output-file", required=True, help="Path to write the prompt.")
    parser.add_argument("--metadata-file", required=True, help="Path to write metadata (length, thumbnail).")
    args = parser.parse_args()

    try:
        video_id = extract_video_id(args.url)
        if not video_id:
            raise ValueError("Could not extract video ID from URL")

        print(f"Fetching transcript for video ID: {video_id}...", file=sys.stderr)
        transcript, length = get_transcript(video_id)

        thumbnail_url = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"

        print(f"Fetching video title for {args.url}...", file=sys.stderr)
        title = get_video_title(args.url)

        prompt = PROMPT_TEMPLATE.format(url=args.url, title=title, transcript=transcript)

        with open(args.output_file, "w", encoding="utf-8") as f:
            f.write(prompt)

        metadata = {"length": length, "thumbnail": thumbnail_url}
        with open(args.metadata_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f)

        print(f"Prompt written to {args.output_file}", file=sys.stderr)
        print(f"Metadata written to {args.metadata_file}", file=sys.stderr)

    except Exception as e:
        print(f"\n[!] The video could not be extracted.", file=sys.stderr)
        print(f"Cause: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
