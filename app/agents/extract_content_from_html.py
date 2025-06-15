import requests
from bs4 import BeautifulSoup

def extract_content_from_url(
    url: str,
    include_links: bool = False,
    min_text_length: int = 20,
    exclude_selectors: list = ["script", "style", "nav", "footer", "head"]
) -> str:
    """
    Extracts clean, readable text from a URL while excluding junk.
    
    Args:
        url (str): The webpage URL.
        include_links (bool): Whether to keep hyperlinks (default: False).
        min_text_length (int): Min length for text blocks (default: 20 chars).
        exclude_selectors (list): Tags/classes to exclude (e.g., ads, menus).
    
    Returns:
        str: Extracted content, cleaned and concatenated.
    """
    try:
        # Fetch HTML
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        print(soup)
        # Remove unwanted elements (scripts, ads, menus)
        for selector in exclude_selectors:
            for element in soup.select(selector):
                element.decompose()

        # Extract text from meaningful tags (p, h1-h6, article, section)
        valid_tags = ["time","p", "h1", "h2", "h3", "h4", "h5", "h6", "article", "section", "main"]
        elements = soup.find_all(valid_tags)

        # Filter and clean text
        texts = []
        for element in elements:
            text = element.get_text(separator=" ", strip=True)
            if len(text) >= min_text_length:
                if include_links:
                    # Preserve links if needed
                    for a in element.find_all("a"):
                        text += f" [{a.get('href')}]"
                texts.append(text)

        return "\n\n".join(texts) if texts else "No readable content found."

    except Exception as e:
        return f"Error: {str(e)}"

# res= extract_content_from_url('https://www.calendardate.com/todays.htm')
# print(res)