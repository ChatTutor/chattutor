from typing import List

from bs4 import BeautifulSoup
import requests

# The URLReader class provides methods to parse the content of a webpage given a URL or a list of
# URLs.
class URLReader:
    def parse_url(url: str):
        """
        The function `parse_url` takes a URL as input, retrieves the content of the webpage, removes the
        style and script tags from the HTML, and returns the stripped text content of the webpage.
        
        :param url: The `url` parameter is a string that represents the URL of a webpage that you want
        to parse
        :type url: str
        :return: the parsed and cleaned text content of the webpage specified by the given URL.
        """
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')
        for tag in soup(['style', 'script']):
            tag.decompose()
        x = " ".join(soup.stripped_strings)
        return x

    def parse_urls(urls: List[str]):
        """
        The function `parse_urls` takes a list of URLs, parses each URL using the `URLReader.parse_url`
        method, and appends the result to a string with two newlines.
        
        :param urls: The `urls` parameter is a list of strings that represent URLs
        :type urls: List[str]
        """
        for url in urls:
            x = URLReader.parse_url(url)
            x += "\n\n"