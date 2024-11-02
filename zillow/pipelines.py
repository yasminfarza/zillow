# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.pipelines.images import ImagesPipeline
from scrapy import Request
from scrapy.http.request import NO_CALLBACK


class ZillowPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        urls = ItemAdapter(item).get(self.images_urls_field, [])
        return [Request(u, meta={'houseId': item.get('id')}, callback=NO_CALLBACK) for u in urls]
 
    def file_path(self, request, response=None, info=None, *, item=None):
        image_name = request.meta['houseId']
        return f"media/images/{image_name}.jpg"

