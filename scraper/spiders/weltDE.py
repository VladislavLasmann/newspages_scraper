# -*- coding: utf-8 -*-
import scrapy
import re
import arrow

from datetime import date, timedelta
from scraper.items import Article


class WeltdeSpider(scrapy.Spider):
    name = 'weltDE'
    archive_start_date = date(1995, 1, 1)
    start_urls = []
    custom_settings = {
        "ITEM_PIPELINES": {"scraper.pipelines.MongoDBPipeline": 300},
    }

    def __init__(self):
        self.start_urls = self._get_start_urls()
        super(WeltdeSpider, self).__init__()

    def parse(self, response):
        online_article_urls = response.xpath('//div[@class="articles text"]//div[@class="article"]//a/@href').extract()
        print_article_urls = response.xpath('//div[@class="articles printimport"]//div[@class="article"]//a/@href').extract()
        all_article_urls = online_article_urls + print_article_urls

        for article_url in all_article_urls:
            yield scrapy.Request(
                article_url,
                callback=self.scrape_article
            )

    def scrape_article(self, response):
        if not self._contains_payment_wall(response):
            article = Article()
            article["newspaper_name"] = "Welt"
            article["url"] = response.url
            article["categories"] = response.css('li[data-qa="Breadcrumb.Item"] > *[property=name] ::text, li[data-qa="Breadcrumb.Item"] > a > *[property=name] ::text').extract()
            article["main_category"] = article["categories"][1]
            article["authors"] = response.xpath('//span[@class="c-author__by-line"]/a/text()').extract()
            article["publish_time"] = self._get_date(response)
            article["title"] = self._clean_text(response.xpath('//h2[@data-qa="Headline"]/text()').get())
            article["text_header"] = self._get_text_header(response)
            article["text_body"] = self._get_text_body(response)
            yield article

    def _contains_payment_wall(self, response):
        return "/plus" in response.url

    def _get_date(self, response):
        date_string = response.xpath('//time[@class="timeformat"]/@datetime').get()
        return arrow.get(date_string).datetime

    def _get_text_header(self, response):
        intro_list = response.xpath('//div[@data-qa="Article.Intro"]/text()').extract()
        summary_list = response.xpath('//div[@data-qa="Article.summary"]/div/div/text()').extract()
        summary_items_list = response.xpath('//div[@data-qa="Article.summary"]/div/ul/li/text()').extract()
        tmp_text_header = intro_list + summary_list + summary_items_list
        return self._clean_text("".join(tmp_text_header))

    def _get_text_body(self, response):
        text = "".join(response.css('div[itemprop="articleBody"] > p *::text').extract())
        return self._clean_text( text )

    def _get_start_urls(self):
        days_delta = (date.today() - self.archive_start_date).days
        dates_inbetween = [date.today() + timedelta(add_dates) for add_dates in range(days_delta + 1)]
        return ['https://www.welt.de/schlagzeilen/nachrichten-vom-'
                + day.strftime("%d-%m-%Y") + '.html'
                for day in dates_inbetween]

    def _clean_text(self, text:str):
        regex = "\xa0|\t|\n|\s\s"
        clean_text = re.sub(regex, " ", text)
        clean_text = re.sub("\s\s+", " ", clean_text)
        return clean_text
