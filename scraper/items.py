# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class Article(scrapy.Item):
    newspaper_name = scrapy.Field()
    url = scrapy.Field()
    main_category = scrapy.Field()
    categories = scrapy.Field()
    authors = scrapy.Field()
    publish_time = scrapy.Field()
    title = scrapy.Field()
    text_header = scrapy.Field()
    text_body = scrapy.Field()


