import random
import re
import uuid
from threading import Lock, Thread
from typing import List
import json
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
from core.extensions import get_random_string
from core.url_reader import URLReader


class URLReaderCls:
    depth = 1
    node_degree = {}
    max_number_of_urls = 20
    TH_COUNT: int
    BFS_TH_COUNT: int

    def __init__(self, depth, max_number_of_urls):
        self.depth = depth
        self.node_degree = {}
        self.max_number_of_urls = max_number_of_urls

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

    global_url_reading_queue: [str]

    all_urls: [str] = []

    def neighbouring_urls(self, lock: Lock, url2app):
        lock.acquire()
        print("starting thread!")
        if len(self.spider_urls) == 0 or len(self.spider_urls) > self.max_number_of_urls:
            return

        urltoapp = self.spider_urls.pop(0)
        self.visited[urltoapp] = True
        self.all_urls.append(urltoapp)
        self.node_degree[urltoapp] = 0

        lock.release()
        s_urls = []

        page = requests.get(urltoapp)
        soup = BeautifulSoup(page.content, 'html.parser')
        hrefs = soup.find_all('a', href=True)
        print("hrefs: ", hrefs, "\n\n\n")
        for href in hrefs:
            print("href:", href)
            shr = href['href']
            if shr[0:7] == "http://" or shr[0:8] == "https://":  # if url be havin' http://
                g = shr
            else:
                g = url2app + shr
            if 'license' not in g:
                print("g: " + g)
                lock.acquire()
                if not self.visited.get(g):
                    s_urls.append(g)
                lock.release()

        lock.acquire()
        for g in s_urls:
            self.all_urls.append(g)
            self.spider_urls.append(g)
        lock.release()

        print("done threading")

    def set_bfs_thread_count(self, tc):
        self.BFS_TH_COUNT = tc

    def produce_bfs_array(self, urltoapp, lock):
        print("PRODUCING BFS ARRAY", self.max_number_of_urls)
        self.spider_urls = []
        self.visited = {}
        self.spider_urls.append(urltoapp)
        self.node_degree[urltoapp] = 0
        THREAD_COUNT = self.BFS_TH_COUNT

        print("PRODUCING BFS ARRAY")
        while 0 < len(self.spider_urls) < self.max_number_of_urls:
            threads = []
            print("len: ", min(len(self.spider_urls), THREAD_COUNT))

            for i in range(0, min(len(self.spider_urls), THREAD_COUNT)):
                thread = Thread(target=self.neighbouring_urls,
                                args=(lock, urltoapp))
                thread.start()
                threads.append(thread)

            print("started threads")

            for thread in threads:
                thread.join()

            print("ended threads")
            print(len(self.spider_urls))

    global_results: {str: dict} = {}

    def parse_url_array(self, lock: Lock, andu_db: MessageDB, chroma_db, collection_name, course_id):
        print("...parsing url arr")
        lock.acquire()
        strv = self.all_urls.pop(0)

        lock.release()

        print("parse " + strv)
        ss = URLReader.parse_url(strv)

        site_text = f"{ss.encode('utf-8', errors='replace')}"
        navn = re.sub(r'[^A-Za-z0-9\-_]', '_', strv)
        file = FileStorage(stream=io.BytesIO(bytes(site_text, 'utf-8')), name=navn)
        f_f = (file, navn)
        doc = Doc(docname=f_f[1], citation="", dockey=f_f[1])
        texts = parse_plaintext_file_read(f_f[0], doc=doc, chunk_chars=2000, overlap=100)

        section_id = navn




        print("finish ..")


        print("adding texts... ", strv)

        chroma_db.add_texts_chroma_lock(texts, lock=lock)
        print("added texts...")

        # add to andu_db

        andu_db.insert_section(section_id=section_id, pulling_from="")
        andu_db.establish_course_section_relationship(section_id=section_id, course_id=course_id)

        lock.acquire()
        # print("yeyrye")
        self.global_results[navn] = {'section_id': section_id,
                                     'course_id': course_id,
                                     'section_url': strv,
                                     'course_chroma_collection': collection_name
                                     }
        lock.release()


    def dfsjdlf(self):
        print("Yeyyy")

    def unique(self, list1):
        unique_list = []

        for x in list1:
            if x not in unique_list:
                unique_list.append(x)

        return unique_list

    def set_thread_count(self, tc):
        self.TH_COUNT = tc

    def new_spider_function(self, urltoapp, save_to_database, collection_name, andu_db: MessageDB, course_name,
                            proffessor, course_id):

        print("New spider func")
        andu_db.insert_course(course_id=course_id, name=course_name, proffessor=proffessor, mainpage=urltoapp,
                              collectionname=collection_name)
        save_to_database.load_datasource(collection_name)
        print("inserted date")

        lock = Lock()
        self.dfsjdlf()
        self.produce_bfs_array(urltoapp=urltoapp, lock=lock)

        print("produced bfs array!!")
        # print(self.spider_urls)
        # print(self.all_urls)

        THREAD_COUNT = self.TH_COUNT
        print("produced array successfully!")
        self.all_urls = self.unique(self.all_urls)
        print(len(self.all_urls))
        while len(self.all_urls) > 1:
            print("len::", len(self.all_urls))
            threads = []
            self.global_results = {}
            print("ao::", min(THREAD_COUNT, len(self.all_urls)))

            for i in range(0, min(THREAD_COUNT, len(self.all_urls))):
                thread = Thread(target=self.parse_url_array,
                                args=(lock, andu_db, save_to_database, collection_name, course_id))
                thread.start()
                threads.append(thread)

            for thread in threads:
                thread.join()

            print("finish in while.")

            # for value in self.global_results.values():
            vals = self.global_results.values()
            yield f"""data: {json.dumps(list(vals))}"""

        print("finished succesfully.")

