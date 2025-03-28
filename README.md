# 🕷️ Price Monitoring Scrapy Project

This project uses [Scrapy](https://scrapy.org/) to monitor product prices and syncs the data with a Google Spreadsheet and MongoDB. It also tracks discontinued products automatically.

---

## 🔧 Environment Setup

Before running the spider, you must define the following environment variables. You can export them in your shell or store them in a `.env` file.

### ✅ Required Environment Variables

| Variable               | Description                                                                                   |
|------------------------|-----------------------------------------------------------------------------------------------|
| `MONGO_URI`            | MongoDB connection URI. Example: a hosted MongoDB Atlas cluster.                             |
| `MONGO_DATABASE`       | Name of the MongoDB database used to store product and price data.                           |
| `SPREADSHEET_ID`       | Google Spreadsheet ID where the latest prices will be uploaded.                              |
| `GOOGLE_CREDENTIALS_JSON` | Full JSON string for a Google service account (used for Google Sheets API). Make sure the private key uses real `\n` line breaks (not `\\n`). |
| `SCRAPY_PROXY`         | *(Optional)* Proxy service URL for Scrapy (e.g., PacketStream).                  |

---

### 🧪 Example `.env` file

You can place this in your project root:

```env
MONGO_URI="mongodb+srv://user:password@price-monitoring.testing.mongodb.net/?retryWrites=true&w=majority&appName=price-monitoring"
MONGO_DATABASE="price-monitoring-db"
SPREADSHEET_ID="1zfw-eCOdvMLEXAMPLEkb-DUJsf6dMDrd8vA4QUGrSZ4oE"
SCRAPY_PROXY="http://user:password@proxy_host:port"
GOOGLE_CREDENTIALS_JSON='{
  "type": "service_account",
  "project_id": "genial-cycling-123456-u3",
  "private_key_id": "YOUR_KEY_ID",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEuwIBADANBg...\n-----END PRIVATE KEY-----\n",
  "client_email": "price-monitoring-spider@genial-cycling-123456-u3.iam.gserviceaccount.com",
  ...
}'
```

## 🚀 Running the spider

Once your environment is configured, run your Scrapy spider with:

```bash
scrapy crawl fastenal
```

## 📊 Output

- Data is saved into the following MongoDB collections:
  - `products`: static product details like name, description, metal type, etc.
  - `priceHistory`: timestamped records of scraped prices for each product.

- Updates are also pushed to the configured **Google Spreadsheet**, including:
  - Product description
  - Latest price
  - Daily and weekly price variation
  - Alerts for significant changes
