# -*- coding: utf-8 -*-
import scrapy

from scrapy.spiders import CrawlSpider, Rule
from news_crawler.items import NewsCrawlerItem
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.selector import Selector



class NewsSpider(scrapy.Spider):
    name = "news"
    allowed_domains = ["http://www.eluniversal.com.mx"]

    start_urls = (
        'http://www.eluniversal.com.mx/minuto-x-minuto',
    )

    rules = (
        Rule(LxmlLinkExtractor(
            follow=False,
            callback='parse'
        )),
    )

    def parse(self, response):
        selector = Selector(response)