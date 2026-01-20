import sys
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

def clean_url(url):
    parsed = urlparse(url)
    query_params = parse_qs(parsed.query, keep_blank_values=True)
    
    # Parameters to remove
    params_to_remove = [
        't', 'pp', 
        'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
        'fbclid', 'gclid', 'si'
    ]
    
    # Remove parameters
    for param in params_to_remove:
        query_params.pop(param, None)
        
    # Reconstruct query string
    new_query = urlencode(query_params, doseq=True)
    
    # Reconstruct URL
    new_parsed = parsed._replace(query=new_query)
    cleaned_url = urlunparse(new_parsed)
    
    # Remove trailing '?' if query is empty
    if cleaned_url.endswith('?'):
        cleaned_url = cleaned_url[:-1]
        
    return cleaned_url

if __name__ == "__main__":
    if len(sys.argv) > 1:
        url = sys.argv[1]
        print(clean_url(url))
    else:
        # Read from stdin if no argument provided (handling piped input)
        for line in sys.stdin:
            if line.strip():
                print(clean_url(line.strip()))
