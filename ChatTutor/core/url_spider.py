import random
import re
import string
import uuid
from threading import Lock, Thread
from typing import List
import json
from bs4 import BeautifulSoup
import bs4
import requests
import io
from urllib.parse import urlparse, ParseResult, urljoin
import uuid

from flask import jsonify
from werkzeug.datastructures import FileStorage
from core.definitions import Text
from core.definitions import Doc
from core.messagedb import MessageDB
from core.reader import parse_plaintext_file, parse_plaintext_file_read
from core.extensions import get_random_string
from core.url_reader import URLReader

 
class URLSpider:
    """
        The `URLSpider` class is a web scraping tool that parses URLs, extracts text content from web pages,
        and stores the parsed information in a database.
    """
    depth = 1
    node_degree = {}
    max_number_of_urls: int
    TH_COUNT: int
    BFS_TH_COUNT: int
    MAX_LEVEL_PARQ: int

    def __init__(self, depth, max_number_of_urls):
        self.depth = depth
        self.node_degree = {}
        self.max_number_of_urls = max_number_of_urls

    def parse_url(url: str):
        """
        The function `parse_url` takes a URL as input, retrieves the content of the web page at that
        URL, removes any style and script tags from the HTML, and returns the stripped text content of
        the page.
        
        :param url: The `url` parameter is a string that represents the URL of a webpage that you want
        to parse
        :type url: str
        :return: The function `parse_url` returns the parsed and cleaned text content of the web page
        specified by the given URL. If there is an error in accessing the page or if the page status
        code is not 200 (indicating a successful response), an empty string is returned.
        """
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
        return x

    def parse_urls(urls: List[str]):
        """
        The function `parse_urls` takes a list of URLs, calls the `parse_url` function on each URL using
        the `URLSpider` class, and appends the result to a string with two newlines.
        
        :param urls: A list of strings representing URLs
        :type urls: List[str]
        """
        for url in urls:
            x = URLSpider.parse_url(url)
            x += "\n\n"

    spider_urls: [str] = []
    degree: int = 0
    visited: {str: bool} = {}

    global_url_reading_queue: [str]

    all_urls: [str] = []

    def neighbouring_urls(self, lock: Lock, url2app):
        """
        The `neighbouring_urls` function is responsible for extracting and processing the URLs found on
        a given webpage, while respecting certain conditions and restrictions.
        
        :param lock: The `lock` parameter is an instance of the `Lock` class from the `threading`
        module. It is used to synchronize access to shared resources between multiple threads. In this
        code, the lock is acquired before accessing and modifying the `self.spider_urls`,
        `self.visited`, and
        :type lock: Lock
        :param url2app: The `url2app` parameter is original url domain
        :return: The function does not explicitly return anything.
        """
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
          
            if ("http://" in shr or "https://" in shr) and dom not in shr:  # if url be havin' http://
                g = "NO"
            else:
                print(adom)
                g = urljoin(adom.geturl(), shr)
                print(g)
                
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

    def set_bfs_thread_count(self, tc):
        self.BFS_TH_COUNT = tc

    def produce_bfs_array(self, urltoapp, lock):
        """
        The function produces a breadth-first search array of URLs by iterating through a list of spider
        URLs and creating threads to find neighboring URLs.
        
        :param urltoapp: The `urltoapp` parameter is the starting URL for the BFS (Breadth-First Search)
        algorithm. It is the URL from which the spider will begin crawling and exploring its neighboring
        URLs
        :param lock: The `lock` parameter is used to synchronize access to shared resources in a
        multi-threaded environment. It ensures that only one thread can access the shared resources at a
        time, preventing race conditions and data corruption
        """
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
    
    
    def add_to_andudb(self, section_dict, from_doc_joined, message_db: MessageDB):
        """
        The function adds a section to a message database and establishes a relationship between the
        section and a course.
        
        :param section_dict: A dictionary containing information about a section, including the section
        ID and course ID
        :param from_doc_joined: The parameter "from_doc_joined" is a string that represents the document
        from which the section is being pulled
        :param message_db: The parameter `message_db` is an instance of the `MessageDB` class
        :type message_db: MessageDB
        :return: a tuple containing the section_dict and from_doc_joined.
        """
        message_db.insert_section(section_id=section_dict['section_id'], pulling_from=from_doc_joined)
        message_db.establish_course_section_relationship(section_id=section_dict['section_id'], course_id=section_dict['course_id'])
        return section_dict, from_doc_joined
    
    def add_from_doc_to_section(self, section_id, to_add, message_db: MessageDB):
        """
        The function `add_from_doc_to_section` updates a section in a message database by adding a value
        from a document, and returns the section ID and the value added.
        
        :param section_id: The section_id parameter is the identifier of the section where the content
        will be added from the document
        :param to_add: The `to_add` parameter is the content that you want to add to a specific section
        in the `message_db`
        :param message_db: The `message_db` parameter is an instance of the `MessageDB` class. It is used
        to interact with a database that stores messages
        :type message_db: MessageDB
        :return: a tuple containing the section_id and to_add.
        """
        message_db.update_section_add_fromdoc(section_id, from_doc=to_add)
        return section_id, to_add

    def parse_url_array(self, lock: Lock, message_db: MessageDB, chroma_db, collection_name, course_id, addToMessageDB=True):
        """
        The function `parse_url_array` parses a URL array, extracts text from the URLs, adds the text to
        a database, and updates various data structures and databases with the parsed information.
        
        :param lock: The `lock` parameter is an instance of the `Lock` class from the `threading`
        module. It is used to synchronize access to shared resources in a multi-threaded environment. By
        acquiring and releasing the lock, the code ensures that only one thread can execute the critical
        section at a time
        :type lock: Lock
        :param message_db: The `message_db` parameter is an instance of the `MessageDB` class. It is
        used to interact with a message database and perform operations such as inserting sections,
        establishing relationships between sections and courses, and retrieving information from the
        database
        :type message_db: MessageDB
        :param chroma_db: The parameter `chroma_db` is a database object that is used to interact with a
        database for storing and retrieving text data. It is used in the `add_texts_chroma_lock` method
        to add the parsed texts to the database
        :param collection_name: The `collection_name` parameter is a string that represents the name of
        the collection in the `chroma_db` where the texts will be added
        :param course_id: The `course_id` parameter is used to identify the course to which the parsed
        URL belongs. It is a unique identifier for the course
        :param addToMessageDB: The `addToMessageDB` parameter is a boolean flag that determines whether
        or not to add the parsed section to the `message_db`. If `addToMessageDB` is set to `True`, the
        section will be added to the `message_db`. If it is set to `False`, the section, defaults to
        True (optional)
        :return: The function does not explicitly return anything.
        """
        print("...parsing url arr")
        lock.acquire()
        strv = self.all_urls.pop(0)

        lock.release()

        print("parse " + strv)
        ss = URLSpider.parse_url(strv)
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
            print("\t\t\t\terror")
        print("added texts...", strv)

        message_db.insert_section(section_id=section_id, pulling_from=section_id, sectionurl=strv)
        message_db.establish_course_section_relationship(section_id=section_id, course_id=course_id)
        lock.acquire()
        self.global_results[navn] = {
                                     'section_id': section_id,
                                     'course_id': course_id,
                                     'section_url': strv,
                                     'course_chroma_collection': collection_name
                                     }
        lock.release()

    def dfsjdlf(self):
        print("Yeyyy")

    def unique(self, list1):
        """
        The function takes a list as input and returns a new list with only the unique elements from the
        input list.
        
        :param list1: The parameter `list1` is a list of elements
        :return: a list of unique elements from the input list.
        """
        unique_list = []

        for x in list1:
            if x not in unique_list:
                unique_list.append(x)

        return unique_list

    def set_thread_count(self, tc):
        self.TH_COUNT = tc

    def get_bfs_array(self, urltoapp):
        """
        The function `get_bfs_array` returns the `all_urls` list after performing some operations.
        
        :param urltoapp: The `urltoapp` parameter is a string that represents the URL to the application
        :return: the value of the variable "self.all_urls".
        """
        lock = Lock()
        self.lock = lock
        self.dfsjdlf()
        self.produce_bfs_array(urltoapp=urltoapp, lock=lock)
        return self.all_urls
    
    def new_spider_function(self, urltoapp, save_to_database, collection_name, message_db: MessageDB, course_name,
                                    proffessor, course_id, produce_bfs=True, current_user=None):
        """
        The function `new_spider_function` is used to crawl and scrape data from a website, save it to a
        database, and return the results.
        
        :param urltoapp: The `urltoapp` parameter is the URL of the application or website that you want
        to crawl with the spider
        :param save_to_database: The `save_to_database` parameter is an object that is responsible for
        saving data to a database. It has a method called `load_datasource` which is used to load data
        from a specific collection in the database
        :param collection_name: The `collection_name` parameter is a string that represents the name of
        the collection in the database where the spider data will be saved
        :param message_db: The `message_db` parameter is an instance of the `MessageDB` class, which is
        used to interact with a database to store and retrieve messages related to the spider function.
        It is used to insert course information, insert user to course, and insert data into the
        database
        :type message_db: MessageDB
        :param course_name: The name of the course
        :param proffessor: The "proffessor" parameter in the function represents the name of the
        professor teaching the course
        :param course_id: The `course_id` parameter is the unique identifier for a course. It is used to
        associate the spider function with a specific course in the database
        :param produce_bfs: produce_bfs is a boolean parameter that determines whether the spider should
        produce a breadth-first search array of URLs or not. If set to True, the spider will generate a
        BFS array of URLs starting from the given urltoapp. If set to False, the spider will not
        generate the BFS array, defaults to True (optional)
        :param current_user: The `current_user` parameter is used to specify the current user who is
        executing the spider function. It is an object that represents the user and contains information
        such as the username
        """

        print("New spider func")
        message_db.insert_course(course_id=course_id, name=course_name, proffessor=proffessor, mainpage=urltoapp,
                              collectionname=collection_name)
        message_db.insert_user_to_course(current_user.username, course_id=course_id)
        save_to_database.load_datasource(collection_name)
        print("inserted date")

        lock = Lock()
        if produce_bfs:
            self.dfsjdlf()
            self.all_urls = []
            print("All urls:", self.all_urls)
            self.produce_bfs_array(urltoapp=urltoapp, lock=lock)
            print("All urls", self.all_urls)
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
                                args=(lock, message_db, save_to_database, collection_name, course_id))
                thread.start()
                threads.append(thread)

            for thread in threads:
                thread.join()

            print("finish in while.")

            # for value in self.global_results.values():
            vals = self.global_results.values()
            yield f"""data: {json.dumps(list(vals))}"""

        print("finished succesfully.")
        self.global_results = []
        self.all_urls = []
        self.spider_urls = []
        self.node_degree = []
    