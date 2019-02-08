# -*- coding: utf-8 -*-
import scrapy
import re
import arrow

from datetime import date, timedelta
from scraper.items import Article


class SpiegeldeSpider(scrapy.Spider):
    name = 'spiegelDE'
    base_url = 'http://www.spiegel.de'
    archive_start_date = date(2000, 1, 1)
    start_urls = []
    custom_settings = {
        "ITEM_PIPELINES": {"scraper.pipelines.MongoDBPipeline": 300},
    }

    def __init__(self):
        self.start_urls = self._get_start_urls()
        super(SpiegeldeSpider, self).__init__()

    def parse(self, response):
        article_url_suffix_list = response.xpath('//div[@id="content-main"]//div[@class="column-wide"]'
                                                 '//ul//li/a/@href').extract()
        for url_suffix in article_url_suffix_list:
            complete_url = self.base_url + url_suffix

            yield scrapy.Request(
                complete_url,
                callback=self.scrape_article
            )

    def scrape_article(self, response):
        if not self._contains_payment_wall(response):
            article = Article()
            article["newspaper_name"] = self.name
            article["url"] = response.url
            article["main_category"] = response.xpath('//a[@class="current-channel-name"]/text()').get()
            article["categories"] = response.xpath('//div[@id="breadcrumb"]/ul/li/a/text()').extract()
            article["authors"] = response.xpath('//p[@class="author"]/a/text()').extract()
            article["publish_time"] = self._get_datetime(response)
            article["title"] = response.xpath('//span[@class="headline-intro"]/text()').get()
            article["text_header"] = self._clean_text( " ".join(response.css('p.article-intro *::text').extract()))
            article["text_body"] = self._clean_text(" ".join(response.css("div#js-article-column > div > p *::text").extract()))

            yield article

    def _contains_payment_wall(self, response):
        return "/plus/" in response.url

    def _get_start_urls(self):
        days_delta = (date.today() - self.archive_start_date).days
        dates_inbetween = [self.archive_start_date + timedelta(add_dates) for add_dates in range(days_delta + 1)]
        return ['http://www.spiegel.de/nachrichtenarchiv/artikel-'
                + day.strftime("%d.%m.%Y") + '.html'
                for day in dates_inbetween]

    def _get_datetime(self, response):
        date_string = response.xpath('//time[@class="timeformat"]/@datetime').get()
        return arrow.get( date_string ).datetime

    def _clean_text(self, text:str):
        regex = "\xa0|\t|\n|\s\s"
        clean_text = re.sub(regex, " ", text)
        clean_text = re.sub("\s\s+", " ", clean_text)
        return clean_text

