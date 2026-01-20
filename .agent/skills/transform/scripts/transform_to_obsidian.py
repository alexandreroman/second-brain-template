import os
import re
import pathlib

# Configuration
SOURCE_DIR = "notes"
DEST_DIR = "obsidian/vault"

# Common topics to link if found
COMMON_TOPICS = [
    "Spring AI", "Spring Boot", "Temporal", "Java", "OpenTelemetry", 
    "Durable Execution", "LLM", "Claude", "OpenAI", "Gemini",
    "Anthropic", "Redis", "Vector Store", "PostgreSQL", "Docker"
]

def timestamp_to_seconds(ts):
    parts = ts.split(':')
    if len(parts) == 2:
        return int(parts[0]) * 60 + int(parts[1])
    elif len(parts) == 3:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    return 0


def get_all_notes():
    notes = []
    all_tags = set()
    for root, _, files in os.walk(SOURCE_DIR):
        for file in files:
            if file.endswith(".md"):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, SOURCE_DIR)
                
                content = ""
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract title
                title = None
                match = re.search(r'^#\s+(.*)$', content, re.MULTILINE)
                if match:
                    title = match.group(1).strip()
                if not title:
                    title = pathlib.Path(file).stem.replace('-', ' ').title()
                
                # Extract tags from frontmatter
                tags = []
                fm_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
                if fm_match:
                    fm_content = fm_match.group(1)
                    tags_match = re.search(r'tags:\s*\[(.*?)\]', fm_content)
                    if tags_match:
                        tags = [t.strip() for t in tags_match.group(1).split(',')]
                        all_tags.update(tags)
                
                notes.append({
                    "full_path": full_path,
                    "rel_path": rel_path,
                    "title": title,
                    "filename_stem": pathlib.Path(file).stem,
                    "content": content,
                    "tags": tags
                })
    return notes, all_tags

def transform():
    notes, all_tags = get_all_notes()
    
    # Titles of all notes
    note_titles = [n['title'] for n in notes]
    
    # Combined list of things to link
    # Sort by length descending to match longest first
    to_link = sorted(list(set(note_titles + list(all_tags) + COMMON_TOPICS)), key=len, reverse=True)
    
    if not os.path.exists(DEST_DIR):
        os.makedirs(DEST_DIR)

    for note in notes:
        content = note['content']
        frontmatter = ""
        body = content
        
        # Separate frontmatter if exists
        fm_match = re.match(r'^(---\s*\n(.*?)\n---\s*\n)(.*)', content, re.DOTALL)
        youtube_id = None
        thumbnail_url = None
        source_url = None
        length_str = ""

        if fm_match:
            original_fm = fm_match.group(1)
            fm_content = fm_match.group(2)
            body = fm_match.group(3)
            
            # Extract metadata from original frontmatter
            url_match = re.search(r'source:\s*(\S+)', fm_content)
            if url_match:
                source_url = url_match.group(1)
            
            thumb_match = re.search(r'thumbnail:\s*(\S+)', fm_content)
            if thumb_match:
                thumbnail_url = thumb_match.group(1)
                
            len_match = re.search(r'length:\s*(.*)', fm_content)
            if len_match:
                length_str = f" ({len_match.group(1).strip()})"
            
            # Extract YouTube ID if applicable
            if source_url:
                yt_match = re.search(r'(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]+)', source_url)
                if yt_match:
                    youtube_id = yt_match.group(1)

            # Rebuild frontmatter: only source and tags remain in YAML (visible in Obsidian Properties)
            # Other attributes are moved to a hidden HTML comment block
            visible_keys = ['source', 'tags', 'aliases']
            new_fm_lines = []
            hidden_fm_lines = []
            has_aliases = False
            
            for line in fm_content.split('\n'):
                line = line.strip()
                if not line: continue
                
                key_match = re.match(r'^([a-zA-Z0-9_-]+):\s*(.*)', line)
                if key_match:
                    key = key_match.group(1)
                    val = key_match.group(2)
                    if key == 'aliases':
                        has_aliases = True

                    if key in visible_keys:
                        new_fm_lines.append(f"{key}: {val}")
                    else:
                        # Skip if it was already there, we will add it unconditionally below
                        if key != 'obsidianUIMode':
                            hidden_fm_lines.append(f"{key}: {val}")
                else:
                    new_fm_lines.append(line)
            
            # Add title as alias if not present to support [[Title]] links
            if not has_aliases:
                # Simple quoting for YAML compatibility if needed, though basic string usually works
                # strictly we might want to ensure it's a list. 
                new_fm_lines.append(f"aliases: [\"{note['title']}\"]")
            
            # Always ensure obsidianUIMode is present and hidden for Obsidian
            hidden_fm_lines.append("obsidianUIMode: preview")
            
            frontmatter = "---\n" + "\n".join(new_fm_lines) + "\n---\n"
            if hidden_fm_lines:
                frontmatter += "<!--\n" + "\n".join(hidden_fm_lines) + "\n-->\n"

        # Extract and transform Review section to callout
        review_callout = ""
        # Look for ## Review or ### Review
        review_match = re.search(r'(^#{2,}\s+Review\s*\n)(.*?)(?=\n#{2,}\s|\Z)', body, re.MULTILINE | re.DOTALL)
        if review_match:
            content_part = review_match.group(2).strip()
            # Remove from body
            body = body[:review_match.start()] + body[review_match.end():]
            
            if content_part:
                quoted = "\n".join([f"> {line}" for line in content_part.splitlines()])
                review_callout = f"\n> [!info] Review\n{quoted}\n\n"

        # Extract and transform Quotes section to callout
        quotes_callout = ""
        # Look for ## Quotes or ### Quotes
        quotes_match = re.search(r'(^#{2,}\s+Quotes\s*\n)(.*?)(?=\n#{2,}\s|\Z)', body, re.MULTILINE | re.DOTALL)
        if quotes_match:
            content_part = quotes_match.group(2).strip()
            # Remove from body
            body = body[:quotes_match.start()] + body[quotes_match.end():]
            
            if content_part:
                quoted = "\n".join([f"> {line}" for line in content_part.splitlines()])
                quotes_callout = f"\n> [!quote] Quotes\n{quoted}\n\n"

        # Add Preview if thumbnail or YouTube found
        preview = ""
        if youtube_id:
            # Fallback for thumbnail if not explicitly set
            if not thumbnail_url:
                thumbnail_url = f"https://img.youtube.com/vi/{youtube_id}/maxresdefault.jpg"
            
            preview = (
                f"\n> [!video] YouTube Video{length_str}\n"
                f"> [![Thumbnail]({thumbnail_url})]({source_url})\n\n"
            )
        elif thumbnail_url:
            if source_url:
                preview = f"\n[![Thumbnail]({thumbnail_url})]({source_url})\n\n"
            else:
                preview = f"\n![Thumbnail]({thumbnail_url})\n\n"
        
        # Insert Review, Quotes and Preview at the top (after title)
        inserts = review_callout + quotes_callout + preview
        
        if inserts:
            # Insert after the title if title exists, otherwise at the top of body
            title_match = re.search(r'^#\s+.*$', body, re.MULTILINE)
            if title_match:
                end_of_title = title_match.end()
                body = body[:end_of_title] + "\n" + inserts + body[end_of_title:]
            else:
                body = inserts + body

        # YouTube specific: Add links to timestamps in the body
        if youtube_id:
            def replace_timestamp(match):
                ts = match.group(1)
                seconds = timestamp_to_seconds(ts)
                return f"[{ts}](https://www.youtube.com/watch?v={youtube_id}&t={seconds}s)"
            
            ts_pattern = r'\[((\d+:)?\d+:\d+)\]'
            body = re.sub(ts_pattern, replace_timestamp, body)


        # Linking logic
        # First, protect URLs and inline code from being transformed by temporarily replacing them with placeholders
        url_pattern = r'(https?://[^\s\)]+)'
        urls = re.findall(url_pattern, body)
        url_placeholders = {}
        for i, url in enumerate(urls):
            placeholder = f"__URL_PLACEHOLDER_{i}__"
            url_placeholders[placeholder] = url
            body = body.replace(url, placeholder, 1)
        
        # Protect inline code (backticks)
        code_pattern = r'(`[^`]+`)'
        codes = re.findall(code_pattern, body)
        code_placeholders = {}
        for i, code in enumerate(codes):
            placeholder = f"__CODE_PLACEHOLDER_{i}__"
            code_placeholders[placeholder] = code
            body = body.replace(code, placeholder, 1)
        
        for topic in to_link:
            # Don't link a title to itself
            if topic == note['title']:
                continue
            
            # Escape for regex
            topic_esc = re.escape(topic)
            
            # Regex: match whole word, not already inside [[ ]]
            # Use a negative lookbehind and lookahead to avoid re-linking or nested links
            pattern = rf'(?<!\[\[)\b({topic_esc})\b(?!\]\])'
            
            # Simple substitution. We use a placeholder to avoid overlapping matches 
            # if we wanted to be very robust, but for this scale it's okay.
            body = re.sub(pattern, rf'[[\g<1>]]', body)
        
        # Restore URLs from placeholders
        for placeholder, url in url_placeholders.items():
            body = body.replace(placeholder, url)
        
        # Restore inline code from placeholders
        for placeholder, code in code_placeholders.items():
            body = body.replace(placeholder, code)

        # Create destination path
        dest_path = os.path.join(DEST_DIR, note['rel_path'])
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        
        # If file exists, make it writable first so we can overwrite it
        if os.path.exists(dest_path):
            os.chmod(dest_path, 0o666)
            
        with open(dest_path, 'w', encoding='utf-8') as f:
            f.write(frontmatter + body)
        
        # Make read-only
        os.chmod(dest_path, 0o444)
        
        print(f"Transformed: {note['rel_path']}")

    # Generate Featured note
    featured_notes = [n for n in notes if 'featured' in n['tags']]
    if featured_notes:
        featured_content = "# Featured Notes\n\n"
        featured_notes.sort(key=lambda x: x['title'])
        for n in featured_notes:
            featured_content += f"- [[{n['filename_stem']}|{n['title']}]]\n"
            
        featured_path = os.path.join(DEST_DIR, "featured.md")
        
        if os.path.exists(featured_path):
            os.chmod(featured_path, 0o666)
            
        with open(featured_path, 'w', encoding='utf-8') as f:
            f.write(featured_content)
            
        os.chmod(featured_path, 0o444)
        print("Generated: featured.md")

if __name__ == "__main__":
    transform()
