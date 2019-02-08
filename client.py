from typing import List
import pymongo
from datetime import datetime
from scrapy.crawler import CrawlerProcess

from models.newspage import Newspage
from database_config import MONGODB_SERVER, MONGODB_PORT, MONGODB_PW, MONGODB_USER


class Client:
    def __init__(self, use_docker = True):
        connection_details = [MONGODB_USER, MONGODB_PW, MONGODB_SERVER, MONGODB_PORT]
        connection_uri = 'mongodb://{0}:{1}@{2}:{3}/'.format(*connection_details)
        self.mongo_connection = pymongo.MongoClient(connection_uri)

    def crawl_all_newspages(self):
        return self.crawl_newspages([page for page in Newspage])

    def crawl_newspages(self, listof_newspages: List[Newspage]):
        crawler_process = CrawlerProcess()
        for newspage in listof_newspages:
            crawler_process.crawl(newspage.get_spider())
        crawler_process.start(stop_after_crawl=True)

    def get_all_articles_in_interval_pages_section(self, listof_newspages: List[Newspage], listof_section: List[str],
                                                   min_date: datetime, max_date: datetime):
        result_list = []
        query_dict = {"publish_time": {"gte": min_date, "lte": max_date}}

        for newspage in listof_newspages:
            for section in listof_section:
                collection = self.mongo_connection[newspage.name][section]

                for element in collection.find(query_dict):
                    result_list.append(element)

        return result_list

    def get_all_articles_in_interval(self, listof_newspages: List[Newspage], min_date: datetime, max_date: datetime):
        result_list = []
        query_dict = {"publish_time": {"gte": min_date, "lte": max_date}}

        for newspage in listof_newspages:
            database = self.mongo_connection[newspage.name]
            listof_collection_names = database.collection_names()

            for col_name in listof_collection_names:
                collection = database[col_name]

                for element in collection.find( query_dict ):
                    result_list.append(element)

        return result_list
