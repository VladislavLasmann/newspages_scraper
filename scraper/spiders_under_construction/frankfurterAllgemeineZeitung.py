# -*- coding: utf-8 -*-
import scrapy
import re
from scraper.items import Article


class FrankfurterallgemeinezeitungSpider(scrapy.Spider):
    name = 'frankfurterAllgemeineZeitung'
    allowed_domains = ['https://www.faz.net/aktuell/politik/ausland/eu-ratschef-tusk-attackiert-radikale-brexit-befuerworter-16027407.html?printPagedArticle=true#pageIndex_0']
    start_urls = ['http://https://www.faz.net/aktuell/politik/ausland/eu-ratschef-tusk-attackiert-radikale-brexit-befuerworter-16027407.html?printPagedArticle=true#pageIndex_0']

    def parse(self, response):
        full_article_button_text_list = response.xpath('//div[@class="atc-ContainerFunctions_Navigation"]//span[@class="btn-Base_Text"]/text()').extract()
        if "Artikel auf einer Seite lesen" in full_article_button_text_list:
            full_article_url = response.xpath('//div[@class="atc-ContainerFunctions_Navigation"]//a[@class="btn-Base_Link"]/@href').get()
            yield scrapy.Request(
                    response.urljoin(full_article_url),
                    callback=self.parse
                )
        elif not self._contains_payment_wall(response):
            self.scrape(response)

    def scrape(self, response):
        article = Article()
        article["newspaper_name"] = "FrankfurterAllgemeineZeitung"
        article["url"] = response.url
        article["main_category"] = self._clean_text(response.xpath(
            '//ul[@class="nvg-Breadcrumb_List"]/li/a/span[@itemprop="name"]/text()').get())
        article["categories"] = response.xpath(
            '//ul[@class="nvg-Breadcrumb_List"]/li/a/span[@itemprop="name"]/text()').extract()
        article["authors"] = self._get_author(response)
        article["date"] = response.xpath('//time[@class="atc-MetaTime"]/@datetime').get()
        article["title"] = self._clean_text(response.xpath('//span[@class="atc-HeadlineText"]/text()').get())
        article["text_header"] = self._clean_text(response.xpath('//p[@class="atc-IntroText"]/text()').get())
        article["text_body"] = self._clean_text(self._get_text_body(response))
        print(article)
        yield article

    def _get_author(self, response):
        author_list = response.xpath('//span[@class="atc-MetaAuthor"]/text()').extract()
        return [author_string.replace("\n", "").replace("\t", "") for author_string in author_list]

    def _get_text_body(self, response):
        text_list = response.xpath('//div[@class="atc-Text "]/*[self::p or self::h3]/text()').extract()
        first_letter = response.xpath('//span[@class="atc-TextFirstLetter"]/text()').get()
        text_list[0] = first_letter + text_list[0]
        return "".join( text_list)

    def _contains_payment_wall(self, response):
        return len(response.xpath('//div[@class="js-ctn-PaywallInfo ctn-PaywallInfo "]')) > 0


    def _clean_text(self, text:str):
        regex = "\xa0|\t|\n|\s\s"
        clean_text = re.sub(regex, " ", text)
        clean_text = re.sub("\s\s+", " ", clean_text)
        return clean_text