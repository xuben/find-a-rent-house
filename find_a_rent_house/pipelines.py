# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from find_a_rent_house.items import CatalogItem, RentHouseItem

class RentHouseItemPipeline(object):
    def process_item(self, item, spider):
        if isinstance(item, CatalogItem):
            pass
        return item

class CatalogItemPipeline(object):
    def process_item(self, item, spider):
        return item