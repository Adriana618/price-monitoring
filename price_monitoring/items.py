# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class PriceMonitoringItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class FastenalItem(scrapy.Item):
    sku = scrapy.Field()
    product_name = scrapy.Field()
    description = scrapy.Field()
    manufacturer = scrapy.Field()
    metal_type = scrapy.Field()
    price = scrapy.Field()
