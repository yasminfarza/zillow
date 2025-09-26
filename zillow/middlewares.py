# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals

import random
from zillow import settings

import socket
from scrapy.mail import MailSender
from scrapy.exceptions import CloseSpider

class Forbidden403Middleware:
    def __init__(self, mailer, to_email):
        self.mailer = mailer
        self.to_email = to_email
        self.alert_sent = False  # avoid duplicate emails

    @classmethod
    def from_crawler(cls, crawler):
        mailer = MailSender.from_settings(crawler.settings)
        to_email = crawler.settings.get("ALERT_EMAIL")
        return cls(mailer, to_email)

    def process_response(self, request, response, spider):
        if response.status == 403 and not self.alert_sent:
            device_name = socket.gethostname()
            subject = f"[Scrapy Alert] 403 Forbidden on {device_name}"
            body = (f"A 403 Forbidden error occurred.\n\n🕸️ Spider: {spider.name}\n🔗 URL: {request.url}\n💻 Device: {device_name}")
            self.mailer.send(to=[self.to_email], subject=subject, body=body)
            self.alert_sent = True
            raise CloseSpider(reason="403 Forbidden detected")
        return response

class ZillowSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class ZillowDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)

import random
from scrapy import signals

class RandomHeaderMiddleware:
    def __init__(self):
        # Lists of headers to randomize
        self.accept_language_options = [
            'en-US,en;q=0.9', 'en-GB,en;q=0.8', 'en;q=0.7'
        ]
        self.user_agent_options = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36'
        ]
        self.referer_options = [
            settings.REFERER
        ]

    def process_request(self, request, spider):
        # Randomize each header field for every request
        request.headers['User-Agent'] = random.choice(self.user_agent_options)
        request.headers['Accept-Language'] = random.choice(self.accept_language_options)
        request.headers['Referer'] = random.choice(self.referer_options)
        request.headers['Content-Type'] = "application/json"
