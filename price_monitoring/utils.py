import pymongo
import datetime
import json
import logging
import os.path
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from scrapy.utils.project import get_project_settings

settings = get_project_settings()
logger = logging.getLogger(__name__)


def calculate_price_differences(db):
    price_coll = db["priceHistory"]

    today = datetime.datetime.utcnow().date()

    docs_today = list(
        price_coll.find(
            {
                "date": {
                    "$gte": datetime.datetime(today.year, today.month, today.day),
                    "$lt": datetime.datetime(today.year, today.month, today.day)
                    + datetime.timedelta(days=1),
                }
            }
        )
    )

    for doc in docs_today:
        sku = doc["sku"]
        price_today = doc["price"]

        prev_doc = price_coll.find_one(
            {"sku": sku, "date": {"$lt": doc["date"]}},
            sort=[("date", pymongo.DESCENDING)],
        )

        last_week = today - datetime.timedelta(days=7)
        week_doc = price_coll.find_one(
            {
                "sku": sku,
                "date": {
                    "$lt": datetime.datetime(
                        last_week.year, last_week.month, last_week.day
                    )
                },
            },
            sort=[("date", pymongo.DESCENDING)],
        )

        price_yesterday = prev_doc["price"] if prev_doc else None
        price_week = week_doc["price"] if week_doc else None

        diff = (price_today - price_yesterday) if price_yesterday else None
        weekly_diff = (price_today - price_week) if price_week else None

        update_data = {}
        if diff is not None:
            update_data["priceDiff"] = diff
        if weekly_diff is not None:
            update_data["weeklyDiff"] = weekly_diff

        if update_data:
            price_coll.update_one({"_id": doc["_id"]}, {"$set": update_data})


SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def update_google_sheet(db):
    """Obtiene datos desde Mongo y los sube a Google Sheets"""
    price_coll = db["priceHistory"]

    pipeline = [
        {"$sort": {"date": -1}},
        {"$group": {
            "_id": "$sku",
            "date": {"$first": "$date"},
            "price": {"$first": "$price"},
            "priceDiff": {"$first": "$priceDiff"},
            "weeklyDiff": {"$first": "$weeklyDiff"}
        }}
    ]
    latest_prices = list(price_coll.aggregate(pipeline))

    credentials_json = settings.get("GOOGLE_CREDENTIALS_JSON")
    creds_dict = json.loads(credentials_json)
    creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")

    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)

    service = build("sheets", "v4", credentials=creds)

    spreadsheet_id = settings.get("SPREADSHEET_ID")
    range_name = "Prices!A1"

    values = [["SKU", "Description", "Price", "Daily Diff", "Weekly Diff", "Last Update", "Alert"]]

    products_coll = db["products"]

    for p in latest_prices:
        product = products_coll.find_one({"sku": p["_id"]})
        description = product.get("description", "") if product else ""
        daily_alert = ""
        weekly_alert = ""
        if p.get("priceDiff", None):
            daily_alert = (
                "⚠ DAILY ALERT"
                if abs(p.get("priceDiff", 0) / (p["price"] - p.get("priceDiff", 1)))
                >= 0.10
                else ""
            )
        if p.get("weeklyDiff", None):
            weekly_alert = (
                "⚠ WEEKLY ALERT"
                if abs(p.get("weeklyDiff", 0) / (p["price"] - p.get("weeklyDiff", 1)))
                >= 0.10
                else ""
            )

        row = [
            p["_id"],
            description,
            p["price"],
            p.get("priceDiff", 0),
            p.get("weeklyDiff", 0),
            p["date"].strftime("%Y-%m-%d %H:%M"),
            daily_alert or weekly_alert,
        ]
        values.append(row)

    body = {"values": values}

    result = (
        service.spreadsheets()
        .values()
        .update(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption="RAW",
            body=body,
        )
        .execute()
    )

    logger.info(f"{result.get('updatedCells')} celdas actualizadas en Google Sheets.")
