# -*- coding: utf-8 -*-
import scrapy
import re
import arrow

from datetime import date
from scraper.items import Article


class SueddeutscheSpider(scrapy.Spider):
    name = 'SUEDDEUTSCHE'
    archive_start_year = 2001
    start_urls = ['https://www.sueddeutsche.de/archiv']
    custom_settings = {
        "ITEM_PIPELINES": {"scraper.pipelines.MongoDBPipeline": 300},
    }

    archive_url_insert_section = 'https://www.sueddeutsche.de/archiv/$section$'
    archive_section_url_insert_year = '$section_url$/$year$'
    archive_section_year_url_insert_page = '$section_year_url$/page/$page$'

    def __init__(self):
        super(SueddeutscheSpider, self).__init__()

    def parse(self, response):
        section_list = response.xpath('//select[@id="dep"]/option/@value').extract()
        section_list.remove("none")
        for section in section_list:
            section_url = self.archive_url_insert_section.replace("$section$", section)
            yield scrapy.Request(
                section_url,
                callback=self.parse_section
            )

    def parse_section(self, response):
        current_year = date.today().year
        for year in range(self.archive_start_year, current_year + 1):
            section_year_url = self.archive_section_url_insert_year\
                                .replace("$section_url$", response.url)\
                                .replace("$year$", str(year))
            yield scrapy.Request(
                section_year_url,
                callback=self.parse_section_year
            )

    def parse_section_year(self, response):
        reduced_pagenumber_list = response.xpath('//li[@class="navigation"]/ol/li/a/@data-page').extract()
        last_page_number = 1 if len(reduced_pagenumber_list) == 0 else int(reduced_pagenumber_list[-1])

        for page_number in range(1, last_page_number + 1):
            page_url = self.archive_section_year_url_insert_page \
                        .replace("$section_year_url$", response.url) \
                        .replace("$page$", str(page_number))
            yield scrapy.Request(
                page_url,
                callback=self.parse_section_year_page
            )

    def parse_section_year_page(self, response):
        article_url_list = response.xpath('//div[@id="entrylist-container"]//a[@class="entrylist__link"]/@href').extract()
        for article_url in article_url_list:
            yield scrapy.Request(
                article_url,
                callback=self.scrape_article
            )

    def scrape_article(self, response):
        if not self._contains_payment_wall(response):
            article = Article()
            article["newspaper_name"] = self.name
            article["url"] = response.url
            article["categories"] = response.css('li.breadcrumbs__item > a ::text, span[itemprop=title]::text, li[itemprop] > *::text').extract()
            article["main_category"] = article["categories"][1]
            article["authors"] = response.xpath('//span[@class="moreInfo"]//span/text()').extract()
            article["publish_time"] = self._get_date(response)
            article["title"] = self._clean_text(response.css('section.header > h2::text, span.caption__title ::text').extract()[-1])
            article["text_header"] = self._clean_text("".join( response.css('p.article ::text').extract() ))
            article["text_body"] = self._clean_text("".join( response.css('section.body > p:not([class*=article]) *::text').extract() ))
            yield article

    def _contains_payment_wall(self, response):
        return (len(response.xpath('//section[@id="article-body"]/div[@class="opc-placeholder"]')) > 0) \
               or response.url.endswith("?reduced=true")

    def _get_date(self, response):
        date_string = response.xpath('//time[@class="timeformat"]/@datetime').get()
        return arrow.get(date_string).datetime

    def _clean_text(self, text:str):
        regex = "\xa0|\t|\n|\s\s"
        clean_text = re.sub(regex, " ", text)
        clean_text = re.sub("\s\s+", " ", clean_text)
        return clean_text
