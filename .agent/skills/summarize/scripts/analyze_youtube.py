import os
import sys
import argparse
import re
from dotenv import load_dotenv
from google import genai
from google.genai import types
import cloudscraper
from bs4 import BeautifulSoup
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter

# Load environment variables
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

def extract_video_id(url):
    """Extracts the video ID from a YouTube URL."""
    # Pattern to match various YouTube URL formats including short URLs and standard URLs
    pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    return None

def get_transcript(video_id):
    """Fetches the transcript for a given video ID."""
    try:
        # Import specific exceptions for better error reporting
        from youtube_transcript_api._errors import (
            TranscriptsDisabled, 
            NoTranscriptFound, 
            CouldNotRetrieveTranscript,
            YouTubeRequestFailed
        )
        
        # Instantiate the API client
        yt = YouTubeTranscriptApi()
        transcript_list = yt.list(video_id)
        
        transcript_obj = None
        
        # 1. Try finding a direct English transcript
        try:
            transcript_obj = transcript_list.find_transcript(['en', 'en-US', 'en-GB'])
        except NoTranscriptFound:
            # 2. If no English transcript, try finding French
            try:
                transcript_obj = transcript_list.find_transcript(['fr', 'fr-FR'])
            except NoTranscriptFound:
                # 3. If no French, try finding ANY transcript
                try:
                    # Get the first available transcript
                    for t in transcript_list:
                        transcript_obj = t
                        break
                except Exception:
                    pass

        # We do NOT translate the transcript here using .translate('en').
        # We pass the original (potentially non-English) transcript to Gemini,
        # which is capable of understanding multiple languages and will be instructed to output in English.
                
        if not transcript_obj:
            raise Exception("No suitable transcript found.")

        transcript = transcript_obj.fetch()
        
        # Format transcript with timestamps for the model
        formatted_text = ""
        total_duration = 0
        
        # Access snippets from the fetched object
        snippets = list(transcript) # transcript is a list of dicts when using fetch() on Transcript object? 
        # Wait, transcript_obj.fetch() returns a list of dictionaries, same as get_transcript()
        
        if snippets:
            # The structure of items in snippets is FetchedTranscriptSnippet object
            last_entry = snippets[-1]
            total_duration = int(last_entry.start + last_entry.duration)

        for entry in snippets:
            start_time = int(entry.start)
            minutes = start_time // 60
            seconds = start_time % 60
            timestamp = f"[{minutes:02d}:{seconds:02d}]"
            formatted_text += f"{timestamp} {entry.text}\n"
            
        # Calculate pretty length
        hours = total_duration // 3600
        minutes = (total_duration % 3600) // 60
        seconds = total_duration % 60
        if hours > 0:
            length_str = f"{hours}:{minutes:02d}:{seconds:02d}"
        else:
            length_str = f"{minutes:02d}:{seconds:02d}"

        return formatted_text, length_str
    except Exception as e:
        error_msg = str(e)
        if "TranscriptsDisabled" in error_msg:
            cause = "Transcripts are disabled for this video."
        elif "NoTranscriptFound" in error_msg:
            cause = "No transcript was found for this video."
        elif any(keyword in error_msg for keyword in ["YouTubeRequestFailed", "RequestBlocked", "blocked", "proxies", "IP address"]):
            cause = "YouTube blocked the request (possibly due to bot detection). Try again later or use a proxy."
        elif "CookiesConfigError" in error_msg or "cookies" in error_msg.lower():
            cause = "Transcript retrieval requires cookies/authentication."
        elif "Timeout" in error_msg or "timed out" in error_msg.lower():
            cause = "The request timed out. YouTube or the connection is too slow."
        else:
            first_line = error_msg.split('\n')[0].strip()
            cause = f"An unexpected error occurred: {first_line}" if first_line else error_msg
        
        raise Exception(cause)

def get_video_title(url):
    """Fetches the title of a YouTube video without a browser."""
    try:
        scraper = cloudscraper.create_scraper()
        # Set a timeout: 10 seconds for connection, 30 seconds for reading data
        response = scraper.get(url, timeout=(10, 30))
        if response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Try to find title in meta tags first (often more reliable for YouTube)
        meta_title = soup.find("meta", attrs={"property": "og:title"}) or soup.find("meta", attrs={"name": "title"})
        if meta_title and meta_title.get("content"):
            return meta_title["content"]
        
        # Fallback to <title> tag
        if soup.title:
            title = soup.title.string
            # YouTube titles often end with " - YouTube"
            return re.sub(r" - YouTube$", "", title).strip()
            
        return None
    except Exception:
        return None

def analyze_transcript(transcript_text, video_url, video_title=None):
    if not API_KEY:
        raise Exception("GEMINI_API_KEY environment variable not set.")

    client = genai.Client(
        api_key=API_KEY,
        http_options=types.HttpOptions(timeout=30000)
    )

    prompt = f"""
    You are an expert content analysis assistant.
    Analyze the following YouTube video transcript and provide a structured report.
    
    IMPORTANT: PROVIDE ALL OUTPUT IN ENGLISH, regardless of the language of the transcript or the video title.
    
    IMPORTANT: Convert any non-ASCII characters (including emojis) in your output to their nearest ASCII equivalent. If no equivalent exists, remove the character entirely. Ensure the final output contains only ASCII characters.

    Video URL: {video_url}
    Original Title: {video_title}
    
    TRANSCRIPT START:
    {transcript_text}
    TRANSCRIPT END

    1. **English Title**: Translate the "Original Title" to English if it is not already. If it is in English, use it as is.
    2. **Summary**: A concise paragraph (3-5 lines) summarizing the main topic and objective of the video based exclusively on the transcript.
       - When referencing titles or specific terms in quotes, place punctuation (commas, periods) OUTSIDE the quotation marks, not inside.
       - Example: titled "Example Title", NOT titled "Example Title,"
    3. **Key Points with Timeline**: A list of essential points covered, using the timestamps provided in the transcript output.
    4. **Quotes**: Extract up to 3 relevant quotes from the transcript.
       - If the transcript is short or lacks impactful quotes, this section can be omitted.
       - Prioritize quotes that capture the essence of the video or provide significant insight.
    
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
    
    print(f"Generating analysis for {video_url}...", file=sys.stderr)
    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=[prompt],
        config=types.GenerateContentConfig(
            temperature=0.2
        )
    )
    
    return response.text

def main():
    parser = argparse.ArgumentParser(description="Analyze YouTube video with Gemini using transcripts.")
    parser.add_argument("url", help="YouTube video URL")
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
        
        analysis = analyze_transcript(transcript, args.url, title)
        
        # Determine output order. 
        # Note: If title was None, we still might get a TITLE from Gemini if it inferred it (unlikely without input, but possible if in transcript).
        # We rely on Gemini outputting TITLE: ... line.
        
        print(f"LENGTH: {length}")
        print(f"THUMBNAIL: {thumbnail_url}")
        print(analysis)

        
    except Exception as e:
        print(f"\n[!] The video could not be analyzed.", file=sys.stderr)
        print(f"Cause: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
