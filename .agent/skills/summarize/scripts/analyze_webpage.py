import os
import sys
import argparse
import cloudscraper
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load environment variables
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

def validate_thumbnail_url(url, scraper):
    """Validates that a thumbnail URL is accessible by making a HEAD request."""
    if not url:
        return False
    
    try:
        response = scraper.head(url, timeout=3, allow_redirects=True)
        # Check if the response is successful and content-type is an image
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '').lower()
            if 'image' in content_type:
                return True
        return False
    except Exception as e:
        print(f"Thumbnail validation failed for {url}: {e}", file=sys.stderr)
        return False

def get_page_content(url):
    """Fetches the content of a webpage using cloudscraper to bypass bot protections."""
    try:
        scraper = cloudscraper.create_scraper()
        # Set a timeout: 10 seconds for connection, 30 seconds for reading data
        print(f"Fetching page content from {url}...", file=sys.stderr)
        response = scraper.get(url, timeout=(5, 20))
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Get thumbnail URL if available
        # Priority: twitter:image > og:image
        thumbnail_url = None
        
        # Try twitter:image first
        twitter_image = soup.find("meta", attrs={"name": "twitter:image"}) or \
                       soup.find("meta", property="twitter:image")
        if twitter_image:
            candidate_url = twitter_image.get("content")
            if validate_thumbnail_url(candidate_url, scraper):
                thumbnail_url = candidate_url
                print(f"Found valid thumbnail from twitter:image: {thumbnail_url}", file=sys.stderr)
        
        # If no valid twitter:image, try og:image
        if not thumbnail_url:
            og_image = soup.find("meta", property="og:image")
            if og_image:
                candidate_url = og_image.get("content")
                if validate_thumbnail_url(candidate_url, scraper):
                    thumbnail_url = candidate_url
                    print(f"Found valid thumbnail from og:image: {thumbnail_url}", file=sys.stderr)
        
        if not thumbnail_url:
            print("No valid thumbnail found", file=sys.stderr)
        
        # Get title
        title = None
        if soup.title:
            title = soup.title.string.strip()
        
        # If no title tag, try og:title
        if not title:
            og_title = soup.find("meta", property="og:title")
            if og_title:
                title = og_title.get("content", "").strip()
                
        if not title:
             title = "Untitled Webpage"

        # Remove script, style, and navigation/footer elements to reduce noise
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()
            
        # Try to find the main content area by looking at several candidates and picking the one with the most text
        candidates = soup.find_all(['article', 'main'])
        # Common class and id names for main content
        common_names = ['blog-post', 'post-content', 'main-content', 'article-body', 'content', 'post', 'article-content', 'entry-content']
        candidates.extend(soup.find_all(class_=lambda x: x and any(c in x.lower() for c in common_names)))
        candidates.extend(soup.find_all(id=lambda x: x and any(c in x.lower() for c in common_names)))
        
        # Filter candidates and pick the one with the most content
        best_candidate = None
        max_length = 0
        
        # Use a set to avoid duplicates if several rules match the same element
        unique_candidates = {id(cand): cand for cand in candidates}.values()
        
        for cand in unique_candidates:
            # Clean candidate text to get a better length estimate
            cand_text = cand.get_text(strip=True)
            if len(cand_text) > max_length:
                max_length = len(cand_text)
                best_candidate = cand
        
        if best_candidate and max_length > 500: # Threshold to avoid picking small sidebars
            text_source = best_candidate
            print(f"Selected content from container with length {max_length} characters", file=sys.stderr)
        else:
            text_source = soup
            print(f"Using full page content (no large container found)", file=sys.stderr)

        # Get text
        text = text_source.get_text()
        
        # Break into lines and remove leading/trailing space on each
        lines = (line.strip() for line in text.splitlines())
        # Break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # Drop blank lines
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return text, thumbnail_url, title
    except Exception as e:
        raise Exception(f"Could not retrieve page content: {e}")

def analyze_text(text, url, title="Untitled"):
    if not API_KEY:
        raise Exception("GEMINI_API_KEY environment variable not set.")

    client = genai.Client(
        api_key=API_KEY,
        http_options=types.HttpOptions(timeout=30000)
    )

    prompt = f"""
    You are an expert content analysis assistant.
    Analyze the following webpage content and provide a structured report.

    IMPORTANT: PROVIDE ALL OUTPUT IN ENGLISH, regardless of the language of the source text.
    
    IMPORTANT: Convert any non-ASCII characters (including emojis) in your output to their nearest ASCII equivalent. If no equivalent exists, remove the character entirely. Ensure the final output contains only ASCII characters.

    IMPORTANT: If the content is from a social media post (e.g., LinkedIn, Twitter), IGNORE any text or links that are unrelated to the main topic or that are purely promoting products or services (e.g., "Sign up for my newsletter", "Check out my course", "Link in bio"). Focus EXCLUSIVELY on the educational, informative, or core narrative content.
    
    URL: {url}
    Original Title: {title}
    
    CONTENT START:
    {text[:50000]} 
    CONTENT END
    
    (Note: Content may be truncated if excessively long)

    1. **English Title**: Translate the "Original Title" to English if it is not already. If it is in English, use it as is.
    2. **Summary**: A concise paragraph (3-5 lines) summarizing the main topic and objective of the page.
       - When referencing titles or specific terms in quotes, place punctuation (commas, periods) OUTSIDE the quotation marks, not inside.
       - Example: titled "Example Title", NOT titled "Example Title,"
    3. **Key Points**: A list of essential insights, arguments, or data points found in the text.
    4. **Quotes**: Extract up to 3 relevant quotes from the source text. 
       - If the text is short or lacks impactful quotes, this section can be omitted.
       - Prioritize quotes that capture the essence of the article or provide significant insight.
    
    Desired Output Format (Markdown):
    
    TITLE: [English Title]
    
    ## Summary
    
    [Your summary here]
    
    ## Key Points
    
    - **Theme or Topic**: Brief description (do not add commas or other punctuation before the colon).
    - **Theme or Topic**: Brief description (do not add commas or other punctuation before the colon).
    ...
    
    ## Quotes
    
    > "First quote here."
    
    > "Second quote here."
    
    > "Third quote here."
    """
    
    print(f"Generating analysis for {url}...", file=sys.stderr)
    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=[prompt],
        config=types.GenerateContentConfig(
            temperature=0.2
        )
    )
    
    return response.text

def main():
    parser = argparse.ArgumentParser(description="Analyze webpage content with Gemini.")
    parser.add_argument("url", help="Webpage URL")
    args = parser.parse_args()
    
    try:
        print(f"Fetching content for URL: {args.url}...", file=sys.stderr)
        text, thumbnail_url, title = get_page_content(args.url)
        
        analysis = analyze_text(text, args.url, title)
        
        # Check if Gemini returned a TITLE: line, if so, use it.
        # Otherwise fall back to original title (printed with TITLE: prefix)
        
        # We print the analysis directly. The analysis should contain "TITLE: ..." as the first line per instructions.
        if thumbnail_url:
            print(f"THUMBNAIL: {thumbnail_url}")
        print(analysis)
        
    except Exception as e:
        error_msg = str(e)
        if "403" in error_msg or "Forbidden" in error_msg:
             cause = "Access to the page was forbidden (403). The site may block bots or require a login."
        elif "404" in error_msg or "Not Found" in error_msg:
             cause = "The page was not found (404). Check the URL."
        elif "NameResolutionError" in error_msg or "ConnectionError" in error_msg:
             cause = "Could not connect to the server. Check your internet connection or the URL."
        elif "Timeout" in error_msg or "timed out" in error_msg.lower():
             cause = "The request timed out. The server might be too slow or unresponsive."
        else:
             first_line = error_msg.split('\n')[0]
             cause = f"An unexpected error occurred: {first_line}"

        print(f"\n[!] The webpage could not be analyzed.", file=sys.stderr)
        print(f"Cause: {cause}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
