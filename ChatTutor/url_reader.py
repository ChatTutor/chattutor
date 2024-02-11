import random
import re
import string
import uuid
from threading import Lock, Thread
from typing import List, Generator
import json
from bs4 import BeautifulSoup
import bs4
import requests
import io
from urllib.parse import urlparse, ParseResult
from core.extensions import VectorDatabase
import uuid

from flask import jsonify
from werkzeug.datastructures import FileStorage
from core.definitions import Text
from core.definitions import Doc
from core.messagedb import MessageDB
from core.reader import parse_plaintext_file, parse_plaintext_file_read
from core.extensions import get_random_string
from core.url_reader import URLReader
from typing import Tuple, Dict
from main import User

class URLReaderCls:
    depth = 1
    node_degree = {}
    max_number_of_urls: int
    TH_COUNT: int
    BFS_TH_COUNT: int
    MAX_LEVEL_PARQ: int

    spider_urls: [str] = []
    degree: int = 0
    visited: {str: bool} = {}

    global_url_reading_queue: [str]

    all_urls: [str] = []

    global_results: {str: dict} = {}

    def __init__(self, depth: int, max_number_of_urls: int) -> None:
        self.depth = depth
        self.node_degree = {}
        self.max_number_of_urls = max_number_of_urls

    def parse_url(url: str) -> str:
        try:
            page = requests.get(url)
        except:
            return ""
        if page.status_code != 200:
            return ""

        content_page_no = page.content.decode('utf-8', 'ignore')
        content_page = ''.join(i for i in content_page_no if i in string.printable)

        soup = BeautifulSoup(content_page, 'html.parser')
        for tag in soup(['style', 'script']):
            tag.decompose()
        x = " ".join(soup.stripped_strings)
        # print(x)
        return x

    def parse_urls(urls: List[str]) -> None:
        for url in urls:
            x = URLReaderCls.parse_url(url)
            x += "\n\n"

    def neighbouring_urls(self, lock: Lock, url2app: str) -> None:
        lock.acquire()
        print("starting thread!")
        if len(self.spider_urls) == 0 or len(self.spider_urls) > self.max_number_of_urls:
            return

        urltoapp = self.spider_urls.pop(0)
        self.visited[urltoapp] = True
        self.all_urls.append(urltoapp)

        lock.release()
        s_urls = []

        page = requests.get(urltoapp)
        if page.status_code != 200:
            return

        soup = BeautifulSoup(page.content, 'html.parser')
        hrefs = soup.find_all('a', href=True)

        adom: ParseResult = urlparse(url2app)
        dom = adom.netloc
        httpdom = adom.scheme + "://" + adom.netloc

        print("dom: ", httpdom)
        print("MAX_PARURL: ", self.MAX_LEVEL_PARQ)
        
        forbidden_extensions = [
            "exe", "py", "a", "b", "c",
            "void", "pdf", "doc", "docx",
            "txt", "java", "c", "zip",
            "tar", "tar.gz", "bin"
        ]
        for href in hrefs:
            lock.acquire()
            shr = href['href']
            print("\t\t -> " + shr)

            g = "OK"
          
            if ("http://" in shr or "https://" in shr) and httpdom not in shr:  # if url be havin' http://
                g = "NO"
            elif httpdom not in shr and g != 'NO':
                if shr[0] == "/":
                    g = httpdom + shr
                else:
                    g = httpdom + "/" + shr
            elif g != 'NO':
                g = shr
                
            if ("void(0);" in g):
                g = "NO"
           
            
            
            no_query = shr.split("?")[0]
            
            for forbidden in forbidden_extensions:
                if no_query.endswith(f".{forbidden}"):
                    g = "NO"
                    


            if g != "NO" and '/#' not in g:
                if 'license' not in g and "login" not in g:
                    if not self.visited.get(g):
                        self.node_degree[g] = self.node_degree[urltoapp] + 1
                        if self.node_degree[g] < self.MAX_LEVEL_PARQ and g not in self.spider_urls and g not in s_urls:
                            print("g: " + g)
                            print(s_urls)
                            s_urls.append(g)
            lock.release()

        lock.acquire()
        for u in s_urls:
            self.all_urls.append(u)
            self.spider_urls.append(u)
        lock.release()

        print("done threading")

    def set_bfs_thread_count(self, tc: int) -> None:
        self.BFS_TH_COUNT = tc

    def produce_bfs_array(self, urltoapp: str, lock: Lock) -> None:
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
    
    # {
    # 'section_id': section_id,
    # 'course_id': course_id,
    # 'section_url': strv,
    # 'course_chroma_collection': collection_name
    # }
    
    def add_to_andudb(
            self, 
            section_dict: Dict, 
            from_doc_joined: str, 
            andu_db: MessageDB
    ) -> Tuple[Dict, str]:
        andu_db.insert_section(section_id=section_dict['section_id'], pulling_from=from_doc_joined)
        andu_db.establish_course_section_relationship(section_id=section_dict['section_id'], course_id=section_dict['course_id'])
        return section_dict, from_doc_joined
    
    def add_from_doc_to_section(self, section_id, to_add: str, andu_db: MessageDB) -> Tuple[str, str]:
        andu_db.update_section_add_fromdoc(section_id, from_doc=to_add)
        return section_id, to_add

    def parse_url_array(
            self, 
            lock: Lock, 
            andu_db: MessageDB, 
            chroma_db: VectorDatabase, 
            collection_name: str, 
            course_id: str, 
            addToMessageDB: bool=True
    ) -> None:
        
        print("...parsing url arr")
        lock.acquire()
        strv = self.all_urls.pop(0)

        lock.release()

        print("parse " + strv)
        ss = URLReaderCls.parse_url(strv)
        if ss == "":
            return

        site_text = f"{ss.encode('utf-8', errors='ignore')}"
        navn = re.sub(r'[^A-Za-z0-9\-_]', '_', strv)
        file = FileStorage(stream=io.BytesIO(bytes(site_text, 'utf-8')), name=navn)
        f_f = (file, navn)
        doc = Doc(docname=f_f[1], citation="", dockey=f_f[1])
        texts = parse_plaintext_file_read(f_f[0], doc=doc, chunk_chars=2000, overlap=100)

        section_id = navn
        print("finish ..")
        print("adding texts... ", strv)
        try:
            chroma_db.add_texts_chroma_lock(texts, lock=lock)
        except:
            print("error")
        print("added texts...")

        # add to andu_db
        print(f"adding to andudb {section_id}")
        andu_db.insert_section(section_id=section_id, pulling_from=section_id, sectionurl=strv)
        andu_db.establish_course_section_relationship(section_id=section_id, course_id=course_id)
        print("added to andubd")
        lock.acquire()
        # print("yeyrye")
        self.global_results[navn] = {
                                     'section_id': section_id,
                                     'course_id': course_id,
                                     'section_url': strv,
                                     'course_chroma_collection': collection_name
                                     }
        lock.release()

    def dfsjdlf(self) -> None:
        print("Yeyyy")

    def unique(self, list1: List) -> List:
        unique_list = []

        for x in list1:
            if x not in unique_list:
                unique_list.append(x)

        return unique_list

    def set_thread_count(self, tc: int) -> None:
        self.TH_COUNT = tc

    def get_bfs_array(self, urltoapp: str) -> List[str]: 
        lock = Lock()
        self.lock = lock
        self.dfsjdlf()
        self.produce_bfs_array(urltoapp=urltoapp, lock=lock)
        return self.all_urls
    
    def new_spider_function(
            self, 
            urltoapp: str, 
            save_to_database: VectorDatabase, 
            collection_name:str, 
            andu_db: MessageDB, 
            course_name: str, 
            proffessor: str, 
            course_id: str, 
            produce_bfs: bool=True, 
            current_user: User=None
    ) -> Generator[str]:

        print("New spider func")
        andu_db.insert_course(course_id=course_id, name=course_name, proffessor=proffessor, mainpage=urltoapp,
                              collectionname=collection_name)
        andu_db.insert_user_to_course(current_user.username, course_id=course_id)
        save_to_database.load_datasource(collection_name)
        print("inserted date")

        lock = Lock()
        if produce_bfs:
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
    