import random
import os
import dotenv

dotenv.load_dotenv()

BOT_NAME = "zillow"

SPIDER_MODULES = ["zillow.spiders"]
NEWSPIDER_MODULE = "zillow.spiders"

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

# DEFAULT_REQUEST_HEADERS = {
#     "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
#     "Sec-Fetch-Dest": "empty",
#     "Sec-Ch-Ua": '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
#     "Sec-Ch-Ua-Mobile": "?0",
#     "sec-ch-ua-platform": '"macOS"',
#     "Sec-Fetch-Mode": "cors",
#     "Sec-Fetch-Site": "same-origin",
#     "accept-language": "en-US,en;q=0.9",
#     "Content-Type": "application/json",
#     "Accept": "*/*",
#     "Accept-Encoding": "gzip, deflate, br, zstd",
#     "Origin": "https://www.zillow.com",
#     "Referer": "https://www.zillow.com/homes/for_rent/"
# }


# Enable the middleware to set the proxy for each request
DOWNLOADER_MIDDLEWARES = {
    'zillow.middlewares.RandomHeaderMiddleware': 543,
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': 90,
}

# Retry settings for handling blocked requests
RETRY_HTTP_CODES = [500, 502, 503, 504, 522, 524, 408, 429]
# Set a download delay and concurrent requests
# DOWNLOAD_DELAY = random.uniform(3, 8)  # Random delay between requests
CONCURRENT_REQUESTS = 5
RETRY_ENABLED = True
RETRY_TIMES = 3
DOWNLOAD_DELAY = 2
RANDOMIZE_DOWNLOAD_DELAY = True

# Variables
COOKIES = os.environ["COOKIES"]
PAYLOAD = os.environ["PAYLOAD"]
FILENAME = os.environ["FILENAME"]
REFERER = os.environ["REFERER"]

PROXY_LIST = [
    "http://scrapyfarzana:m~3E2glX3WywCz4qqj@us.decodo.com:10001",
    "http://scrapyfarzana:m~3E2glX3WywCz4qqj@us.decodo.com:10002",
    "http://scrapyfarzana:m~3E2glX3WywCz4qqj@us.decodo.com:10003",
    "http://scrapyfarzana:m~3E2glX3WywCz4qqj@us.decodo.com:10004",
    "http://scrapyfarzana:m~3E2glX3WywCz4qqj@us.decodo.com:10005",
    "http://scrapyfarzana:m~3E2glX3WywCz4qqj@us.decodo.com:10006",
    "http://scrapyfarzana:m~3E2glX3WywCz4qqj@us.decodo.com:10007",
    "http://scrapyfarzana:m~3E2glX3WywCz4qqj@us.decodo.com:10008",
    "http://scrapyfarzana:m~3E2glX3WywCz4qqj@us.decodo.com:10009",
    "http://scrapyfarzana:m~3E2glX3WywCz4qqj@us.decodo.com:10010",
    "http://scrapyfarzana:m~3E2glX3WywCz4qqj@us.decodo.com:10011",
    "http://scrapyfarzana:m~3E2glX3WywCz4qqj@us.decodo.com:10012",
    "http://scrapyfarzana:m~3E2glX3WywCz4qqj@us.decodo.com:10013",
    "http://scrapyfarzana:m~3E2glX3WywCz4qqj@us.decodo.com:10014",
    "http://scrapyfarzana:m~3E2glX3WywCz4qqj@us.decodo.com:10015",
    "http://scrapyfarzana:m~3E2glX3WywCz4qqj@us.decodo.com:10016",
    "http://scrapyfarzana:m~3E2glX3WywCz4qqj@us.decodo.com:10017",
    "http://scrapyfarzana:m~3E2glX3WywCz4qqj@us.decodo.com:10018",
    "http://scrapyfarzana:m~3E2glX3WywCz4qqj@us.decodo.com:10019",
    "http://scrapyfarzana:m~3E2glX3WywCz4qqj@us.decodo.com:10020",
    "http://scrapyfarzana:m~3E2glX3WywCz4qqj@us.decodo.com:10021",
    "http://scrapyfarzana:m~3E2glX3WywCz4qqj@us.decodo.com:10022",
    "http://scrapyfarzana:m~3E2glX3WywCz4qqj@us.decodo.com:10023",
    "http://scrapyfarzana:m~3E2glX3WywCz4qqj@us.decodo.com:10024",
    "http://scrapyfarzana:m~3E2glX3WywCz4qqj@us.decodo.com:10025",
    "http://scrapyfarzana:m~3E2glX3WywCz4qqj@us.decodo.com:10026",
    "http://scrapyfarzana:m~3E2glX3WywCz4qqj@us.decodo.com:10027",
    "http://scrapyfarzana:m~3E2glX3WywCz4qqj@us.decodo.com:10028",
    "http://scrapyfarzana:m~3E2glX3WywCz4qqj@us.decodo.com:10029",
    "http://scrapyfarzana:m~3E2glX3WywCz4qqj@us.decodo.com:10030",
    "http://scrapyfarzana:m~3E2glX3WywCz4qqj@us.decodo.com:10031",
    "http://scrapyfarzana:m~3E2glX3WywCz4qqj@us.decodo.com:10032",
    "http://scrapyfarzana:m~3E2glX3WywCz4qqj@us.decodo.com:10033",
    "http://scrapyfarzana:m~3E2glX3WywCz4qqj@us.decodo.com:10034",
    "http://scrapyfarzana:m~3E2glX3WywCz4qqj@us.decodo.com:10035",
    "http://scrapyfarzana:m~3E2glX3WywCz4qqj@us.decodo.com:10036",
    "http://scrapyfarzana:m~3E2glX3WywCz4qqj@us.decodo.com:10037",
    "http://scrapyfarzana:m~3E2glX3WywCz4qqj@us.decodo.com:10038",
    "http://scrapyfarzana:m~3E2glX3WywCz4qqj@us.decodo.com:10039",
    "http://scrapyfarzana:m~3E2glX3WywCz4qqj@us.decodo.com:10040",
]

DOWNLOADER_MIDDLEWARES.update({
    'zillow.middlewares.Forbidden403Middleware': 560,
})

# Email settings (example for Gmail SMTP)
MAIL_FROM = 'farzana09bd@gmail.com'
MAIL_HOST = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USER = 'farzana09bd@gmail.com'
MAIL_PASS = 'jsfz sgwn auxi zucw'  # Use Gmail App Password
MAIL_TLS = True
MAIL_SSL = False

ALERT_EMAIL = 'farzana09bd@gmail.com'
