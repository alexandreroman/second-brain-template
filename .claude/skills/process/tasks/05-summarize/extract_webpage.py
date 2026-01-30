import sys
import json
import argparse
import urllib3
import cloudscraper
from bs4 import BeautifulSoup

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def validate_thumbnail_url(url, session, verify=True):
    """Validates that a thumbnail URL is accessible by making a HEAD request."""
    if not url:
        return False
    try:
        response = session.head(url, timeout=3, allow_redirects=True, verify=verify)
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '').lower()
            if 'image' in content_type:
                return True
        return False
    except Exception as e:
        print(f"Thumbnail validation failed for {url}: {e}", file=sys.stderr)
        return False


def get_page_content(url):
    """Fetches the content of a webpage using cloudscraper, falls back to requests if SSL fails."""
    import requests

    # Try cloudscraper first
    session = None
    verify = True
    try:
        scraper = cloudscraper.create_scraper()
        print(f"Fetching page content from {url}...", file=sys.stderr)
        response = scraper.get(url, timeout=(5, 20))
        response.raise_for_status()
        session = scraper
        print("Using cloudscraper", file=sys.stderr)
    except Exception as e:
        error_msg = str(e)
        # If SSL error, fallback to requests with verify=False
        if "SSL" in error_msg or "CERTIFICATE" in error_msg:
            print(f"Cloudscraper failed with SSL error, falling back to requests with SSL disabled...", file=sys.stderr)
            session = requests.Session()
            response = session.get(url, timeout=(5, 20), verify=False)
            response.raise_for_status()
            verify = False
        else:
            # Re-raise if not SSL error
            raise

    soup = BeautifulSoup(response.text, 'html.parser')

    # Get thumbnail URL if available
    thumbnail_url = None

    twitter_image = soup.find("meta", attrs={"name": "twitter:image"}) or \
                   soup.find("meta", property="twitter:image")
    if twitter_image:
        candidate_url = twitter_image.get("content")
        if validate_thumbnail_url(candidate_url, session, verify=verify):
            thumbnail_url = candidate_url

    if not thumbnail_url:
        og_image = soup.find("meta", property="og:image")
        if og_image:
            candidate_url = og_image.get("content")
            if validate_thumbnail_url(candidate_url, session, verify=verify):
                thumbnail_url = candidate_url

    # Get title
    title = None
    if soup.title:
        title = soup.title.string.strip()
    if not title:
        og_title = soup.find("meta", property="og:title")
        if og_title:
            title = og_title.get("content", "").strip()
    if not title:
        title = "Untitled Webpage"

    # Remove noise
    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()

    # Find main content area
    candidates = soup.find_all(['article', 'main'])
    common_names = ['blog-post', 'post-content', 'main-content', 'article-body', 'content', 'post', 'article-content', 'entry-content']
    candidates.extend(soup.find_all(class_=lambda x: x and any(c in x.lower() for c in common_names)))
    candidates.extend(soup.find_all(id=lambda x: x and any(c in x.lower() for c in common_names)))

    best_candidate = None
    max_length = 0
    unique_candidates = {id(cand): cand for cand in candidates}.values()

    for cand in unique_candidates:
        cand_text = cand.get_text(strip=True)
        if len(cand_text) > max_length:
            max_length = len(cand_text)
            best_candidate = cand

    if best_candidate and max_length > 500:
        text_source = best_candidate
    else:
        text_source = soup

    text = text_source.get_text()
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = '\n'.join(chunk for chunk in chunks if chunk)

    return text, thumbnail_url, title


PROMPT_TEMPLATE = """
You are an expert content analysis assistant.
Analyze the following webpage content and provide a structured report.

IMPORTANT: PROVIDE ALL OUTPUT IN ENGLISH, regardless of the language of the source text.

IMPORTANT: Convert any non-ASCII characters (including emojis) in your output to their nearest ASCII equivalent. If no equivalent exists, remove the character entirely. Ensure the final output contains only ASCII characters.

IMPORTANT: NEVER use the '—' (em dash) character in your output. Replace it with a contextual equivalent (such as commas, colons, or parentheses) depending on the sentence structure. NEVER use a simple dash '-' as a replacement for an em dash.

IMPORTANT: If the content is from a social media post (e.g., LinkedIn, Twitter), IGNORE any text or links that are unrelated to the main topic or that are purely promoting products or services (e.g., "Sign up for my newsletter", "Check out my course", "Link in bio"). Focus EXCLUSIVELY on the educational, informative, or core narrative content.

URL: {url}
Original Title: {title}

CONTENT START:
{content}
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

IMPORTANT: Output raw Markdown directly. Do NOT wrap your response in code fences (``` or ```markdown). Your response must start with "TITLE:" directly.

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


def main():
    parser = argparse.ArgumentParser(description="Extract webpage content and build analysis prompt.")
    parser.add_argument("url", help="Webpage URL")
    parser.add_argument("--output-file", required=True, help="Path to write the prompt.")
    parser.add_argument("--metadata-file", required=True, help="Path to write metadata (thumbnail).")
    args = parser.parse_args()

    try:
        text, thumbnail_url, title = get_page_content(args.url)

        prompt = PROMPT_TEMPLATE.format(url=args.url, title=title, content=text[:50000])

        with open(args.output_file, "w", encoding="utf-8") as f:
            f.write(prompt)

        metadata = {"thumbnail": thumbnail_url}
        with open(args.metadata_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f)

        print(f"Prompt written to {args.output_file}", file=sys.stderr)
        print(f"Metadata written to {args.metadata_file}", file=sys.stderr)

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

        print(f"\n[!] The webpage could not be extracted.", file=sys.stderr)
        print(f"Cause: {cause}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
