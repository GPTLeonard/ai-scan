import requests
from bs4 import BeautifulSoup
import logging

def scrape_website(url: str, max_tokens: int = 2000) -> str:
    """
    Scrapes the text content from a given URL.
    Returns a truncated string to fit within a token limit (approximate).
    """
    try:
        # Auto-fix URL scheme
        if not url.startswith('http://') and not url.startswith('https://'):
            url = 'https://' + url
            
        # Add headers to mimic a browser, some sites block basic requests
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36'
        }
        
        logging.info(f"Scraping URL: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
            
        # Get text
        text = soup.get_text()
        
        # Break into lines and remove leading/trailing space on each
        lines = (line.strip() for line in text.splitlines())
        # Break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # Drop blank lines
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        # Simple truncation (character based, roughly 4 chars per token)
        max_chars = max_tokens * 4
        if len(text) > max_chars:
            text = text[:max_chars] + "... [Truncated]"
            
        logging.info(f"Scraped {len(text)} characters.")
        return text

    except Exception as e:
        logging.error(f"Error scraping {url}: {str(e)}")
        return f"Error scraping website: {str(e)}"
