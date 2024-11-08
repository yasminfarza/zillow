import random

BOT_NAME = "zillow"

SPIDER_MODULES = ["zillow.spiders"]
NEWSPIDER_MODULE = "zillow.spiders"

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

DEFAULT_REQUEST_HEADERS = {
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Sec-Fetch-Dest": "empty",
    "Sec-Ch-Ua": '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
    "Sec-Ch-Ua-Mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "accept-language": "en-US,en;q=0.9",
    "Content-Type": "application/json",
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Origin": "https://www.zillow.com",
    "Referer": "https://www.zillow.com/homes/for_rent/"
}

# Enable proxy usage
PROXY_USER = 'spl8584hxy'
PROXY_PASSWORD = 'eI0whJ1ihFsm1yRw_6'
PROXY_SERVER = 'gate.smartproxy.com:10001'

# Smartproxy configuration in Scrapy
HTTP_PROXY = f'http://{PROXY_USER}:{PROXY_PASSWORD}@{PROXY_SERVER}'
HTTPS_PROXY = HTTP_PROXY

# Enable the middleware to set the proxy for each request
DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'scrapy_user_agents.middlewares.RandomUserAgentMiddleware': 400,
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': 90,
}

# Use the proxy for HTTP and HTTPS requests
CUSTOM_PROXY = f"http://{PROXY_USER}:{PROXY_PASSWORD}@{PROXY_SERVER}"

# Retry settings for handling blocked requests
RETRY_HTTP_CODES = [500, 502, 503, 504, 522, 524, 408, 429]
# Set a download delay and concurrent requests
DOWNLOAD_DELAY = random.uniform(3, 8)  # Random delay between requests
CONCURRENT_REQUESTS = 5
RETRY_ENABLED = True
RETRY_TIMES = 3


