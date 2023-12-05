from typing import List

from bs4 import BeautifulSoup
import requests

class URLReader:
    def parse_url(url: str):
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')
        for tag in soup(['style', 'script']):
            tag.decompose()
        x = " ".join(soup.stripped_strings)
        return x

    def parse_urls(urls: List[str]):
        for url in urls:
            x = URLReader.parse_url(url)
            x += "\n\n"