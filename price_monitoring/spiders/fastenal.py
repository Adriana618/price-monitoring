import scrapy
import json

from price_monitoring.items import FastenalItem


class FastenalSpider(scrapy.Spider):
    name = "fastenal"
    allowed_domains = ["www.fastenal.com"]
    start_urls = ["https://www.fastenal.com"]

    search_url = "https://www.fastenal.com/catalog/api/product-search"

    token = "a97a8daa-de51-42b1-92d0-2b3eea30f5b2"

    def start_requests(self):
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
            "Origin": "https://www.fastenal.com",
            "Referer": "https://www.fastenal.com/product/Material%20Handling%2C%20Lifting%20and%20Rigging/Magnets/General%20Purpose%20Magnets?categoryId=600448&page=2&pageSize=12",
            "X-XSRF-TOKEN": "a97a8daa-de51-42b1-92d0-2b3eea30f5b2",
        }

        cookies = {"XSRF-TOKEN": "a97a8daa-de51-42b1-92d0-2b3eea30f5b2"}

        payload = {
            "categoryLevelOne": "Material Handling, Lifting and Rigging",
            "categoryLevelTwo": "Magnets",
            "categoryLevelThree": "General Purpose Magnets",
            "categoryId": "600448",
            "attributeFilters": {},
            "pageUrl": "/product/Material%20Handling%2C%20Lifting%20and%20Rigging/Magnets/General%20Purpose%20Magnets",
        }

        yield scrapy.FormRequest(
            url=self.search_url,
            method="POST",
            headers=headers,
            cookies=cookies,
            body=json.dumps(payload),
            callback=self.parse_initial,
            meta={
                "handle_httpstatus_list": [405, 403, 500],
            },
        )

    def get_price(self, prices):
        for price in prices:
            if price["dataName"] == "Online Price:":
                return price["pr"]
        return 0

    def parse_initial(self, response):
        products = response.json()["productList"]
        paging = response.json()["paging"]

        for product in products:
            item = FastenalItem()
            item["sku"] = product["sku"]
            item["product_name"] = ""  # product["test"]
            item["description"] = product["mp_des"]
            item["manufacturer"] = product["mfr"]
            item["metal_type"] = ""  # product[""]
            item["price"] = self.get_price(product["pdd"])
            yield item

        if paging["currentPage"] == paging["totalPages"]:
            return

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
            "Origin": "https://www.fastenal.com",
            "Referer": "https://www.fastenal.com/product/Material%20Handling%2C%20Lifting%20and%20Rigging/Magnets/General%20Purpose%20Magnets?categoryId=600448&page=2&pageSize=12",
            "X-XSRF-TOKEN": "a97a8daa-de51-42b1-92d0-2b3eea30f5b2",
        }
        payload = {
            "categoryLevelOne": "Material Handling, Lifting and Rigging",
            "categoryLevelTwo": "Magnets",
            "categoryLevelThree": "General Purpose Magnets",
            "categoryId": "600448",
            "attributeFilters": {},
            "page": str(int(paging["currentPage"]) + 1),
            "pageSize": "12",
            "pageUrl": "/product/Material%20Handling%2C%20Lifting%20and%20Rigging/Magnets/General%20Purpose%20Magnets",
        }
        cookies = {"XSRF-TOKEN": "a97a8daa-de51-42b1-92d0-2b3eea30f5b2"}
        yield scrapy.FormRequest(
            url=self.search_url,
            method="POST",
            headers=headers,
            cookies=cookies,
            body=json.dumps(payload),
            callback=self.parse_initial,
            meta={
                "handle_httpstatus_list": [405, 403, 500],
            },
        )
