# -*- coding: utf-8 -*-
from scraper.items import Article
import pymongo
from database_config import MONGODB_SERVER, MONGODB_PORT, MONGODB_PW, MONGODB_USER


class MongoDBPipeline(object):
    def __init__(self):
        connection_details = [MONGODB_USER, MONGODB_PW, MONGODB_SERVER, MONGODB_PORT]
        connection_uri = 'mongodb://{0}:{1}@{2}:{3}/'.format(*connection_details)
        self.connection = pymongo.MongoClient(connection_uri)

    def process_item(self, item:Article, spider):
        db = self.connection[item["newspaper_name"]]
        db_collection = db[item["main_category"]]
        item_dict = dict( item )
        item_dict["_id"] = item_dict["url"]
        db_collection.save(item_dict)

