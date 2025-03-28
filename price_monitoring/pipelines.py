# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from price_monitoring.utils import calculate_price_differences, update_google_sheet
import pymongo
from scrapy import signals
import datetime
import logging

logger = logging.getLogger(__name__)

class MongoPipeline:

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls(
            mongo_uri=crawler.settings.get("MONGO_URI"),
            mongo_db=crawler.settings.get("MONGO_DATABASE"),
        )

        crawler.signals.connect(pipeline.close_spider, signal=signals.spider_closed)

        return pipeline

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def process_item(self, item, spider):
        products_coll = self.db["products"]
        price_coll = self.db["priceHistory"]

        products_coll.update_one(
            {"sku": item["sku"]},
            {
                "$set": {
                    "sku": item["sku"],
                    "productName": item["product_name"],
                    "description": item["description"],
                    "manufacturer": item["manufacturer"],
                    "metalType": item["metal_type"],
                }
            },
            upsert=True,
        )

        today = datetime.datetime.utcnow()

        price_value = float(item["price"]) if item["price"] else None

        price_doc = {"sku": item["sku"], "date": today, "price": price_value}
        price_coll.insert_one(price_doc)

        return item


    def close_spider(self, spider, reason):
        if reason == "finished":
            logger.info("🐍 Spider finished successfully. Calculating price variations...")
            calculate_price_differences(self.db)
            logger.info("✅ Price variation calculation completed.")

            logger.info("📊 Updating Google Sheets...")
            update_google_sheet(self.db)
            logger.info("✅ Google Sheets updated.")
        else:
            logger.warning(f"⚠ Spider closed with status '{reason}', data will not be updated.")
