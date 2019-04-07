# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import re
from scrapy.exceptions import DropItem
from find_a_rent_house.items import CatalogItem, RentHouseItem
from find_a_rent_house.spiders.checker import checker

class RentHouseItemPipeline(object):
    def process_item(self, item, spider):
        if isinstance(item, CatalogItem):
            pass
        return item

class CatalogItemPipeline(object):
    def process_item(self, item, spider):
        return item

class CheckerPipeline(object):

    def process_item(self, item, spider):
        if isinstance(item, RentHouseItem):
            # 图片数量
            if (item.get('image_num', 0) == 0):
                raise DropItem('image number check failed')
            if 'full_title' in item:
                content = item['full_title'] + '\n' + item.get('content', '')
            else:
                content = item['title'] + '\n' + item.get('content', '')
            # 价格判断
            if not checker.checkPrice(content):
                raise DropItem('price check failed')
            if (re.search(spider.ex_keywords, content)):
                raise DropItem('exclusion check failed')
            if (not re.search(spider.keywords, content)):
                raise DropItem('inclusion check failed')
        return item

# write rent items to file
class RentItemWriterPipeline(object):
    def open_spider(self, spider):
        self.file = open('data/result', mode='a+', encoding='utf-8', buffering=512)

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        if isinstance(item, RentHouseItem):
            if 'full_title' in item:
                self.file.write(item['full_title'] + '\n')
            else:
                self.file.write(item['title'] + '\n')
            self.file.write(item.get('url') + '\n')
        return item