# from typing import Any
#
# import scrapy
# from scrapy.http import Response
# from scrapy.crawler import CrawlerProcess
# from scrapy.spiders import CrawlSpider, Rule
# from scrapy.utils.project import get_project_settings
# from scrapy.linkextractors import LinkExtractor
#
#
#
# class DataHolder:
#     data: [str] = []
#
# class URLSpiderParser(CrawlSpider):
#     def __init__(self, *args, **kwargs):
#         super(CrawlSpider, self).__init__(*args, **kwargs)
#
#
#     name = 'TheFriendlyNeighbourhoodSpider'
#
#     allowed_domains = ['en.wikipedia.org', 'upload.wikimedia.org']
#     start_urls = ['https://en.wikipedia.org/wiki/Lists_of_animals']
#
#     custom_settings = {
#         'LOG_LEVEL': 'INFO',
#         'DEPTH_LIMIT': 3
#     }
#
#     rules = (
#         Rule(LinkExtractor(), callback='parse_item', follow=True),
#     )
#
#     parsed_urls: DataHolder
#
#     def parse_item(self, response):
#         filename = f'storage/{response.url.split("/")[-1]}.html'
#         print(filename)
#
