import re
import uuid
from typing import List

from bs4 import BeautifulSoup
import requests
import io
import uuid

from flask import jsonify
from werkzeug.datastructures import FileStorage
from core.definitions import Text
from core.definitions import Doc
from core.messagedb import MessageDB
from core.reader import parse_plaintext_file, parse_plaintext_file_read


class URLReader:
    def parse_url(url: str):
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')
        for tag in soup(['style', 'script']):
            tag.decompose()
        x = " ".join(soup.stripped_strings)
        print(x)
        return x

    def parse_urls(urls: List[str]):
        for url in urls:
            x = URLReader.parse_url(url)
            x += "\n\n"

    spider_urls: [str] = []
    degree: int = 0
    visited: {str: bool} = {}

    def please_spider(self, max_nr, urltoapp, save_to_database, collection_name, andu_db: MessageDB, course_name, proffessor):
        self.spider_urls = []
        self.visited = {}
        self.spider_urls.append(urltoapp)
        while len(self.spider_urls) > 0:
            url = self.spider_urls.pop(0)
            self.visited[url] = 1
            self.degree += 1
            if (self.degree > max_nr):
                self.spider_urls = []
                self.visited = {}
                break
            page = requests.get(url)
            soup = BeautifulSoup(page.content, 'html.parser')
            hrefs = soup.find_all('a', href=True)
            course_id = f'{uuid.uuid4()}'
            yield course_id
            for href in hrefs:
                g = ''
                shr = href['href']
                if shr[0:7] == "http://" or shr[0:8] == "https://":  # if url be havin' http://
                    g = shr
                else:
                    g = url + shr

                if not (self.visited.get(g) and self.visited[g] == 1):
                    self.spider_urls.append(g)
                    # add to chromadb
                    ss = URLReader.parse_url(g)
                    site_text = f"{ss.encode('utf-8', errors='replace')}"
                    navn = re.sub(r'[^A-Za-z0-9\-_]', '_', g)
                    print('Saved to ', navn)
                    file = FileStorage(stream=io.BytesIO(bytes(site_text, 'utf-8')), name=navn)

                    f_f = (file, navn)
                    doc = Doc(docname=f_f[1], citation="", dockey=f_f[1])
                    texts = parse_plaintext_file_read(f_f[0], doc=doc, chunk_chars=2000, overlap=100)

                    save_to_database.load_datasource(collection_name)
                    save_to_database.add_texts(texts)
                    # add to andu_db

                    andu_db.insert_course(course_id=course_id, name=course_name, proffessor=proffessor, mainpage=urltoapp, collectionname=collection_name)
                    yield g


