# from typing import Any
#
# import scrapy
# from scrapy.http import Response
# from scrapy.crawler import CrawlerProcess
# from scrapy.spiders import CrawlSpider, Rule
# from scrapy.utils.project import get_project_settings
# from scrapy.linkextractors import LinkExtractor
# from urlspider import URLSpiderParser
#
#
# class URLSpiderParser_Main:
#     main_process: CrawlerProcess
#     parsed_items: [str] = []
#
#     def run_url_parser(self, dataholder):
#         process = CrawlerProcess()
#         process.crawl(URLSpiderParser)
#         process.start(stop_after_crawl=True, install_signal_handlers=False)
#
#     def stop_process(self):
#         self.main_process.stop()
