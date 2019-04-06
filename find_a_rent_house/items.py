# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import datetime
from scrapy import Item, Field
from scrapy.loader import ItemLoader
from scrapy.loader.processors import Join, MapCompose, TakeFirst

class RentHouseItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = Field()
    full_title = Field()
    content = Field()
    image_num = Field()
    date = Field()

def count_processor(self, values):
    if values is None:
        return 0
    return len(values)
    
def date_processor(self, values):
    return datetime.datetime.strptime(values[0], '%Y-%m-%d %H:%M:%S')

class RentHouseItemLoader(ItemLoader):

    default_output_processor = TakeFirst()
    content_in = Join('\n')
    image_num_in = count_processor
    date_in = date_processor

    def __init__(self, item, response):
        ItemLoader.__init__(self, item = item, response = response)
        self.add_css('title', '#content>h1::text')
        self.add_css('full_title', '.topic-doc td.tablecc::text')
        self.add_css('content', '.topic-richtext>p')
        self.add_css('image_num', '.topic-richtext img')
        self.add_css('date', '.topic-doc>h3>span:nth-last-of-type(1)::text')

class CatalogItem(Item):
    title = Field()
    author = Field()
    url = Field()
    lastRespStr = Field()

class CatalogItemLoader(ItemLoader):

    default_output_processor = TakeFirst()

    def __init__(self, item, selector):
        ItemLoader.__init__(self, item = item, selector = selector)
        self.add_css('title', '.title>a::text')
        self.add_css('author', 'td:nth-of-type(2)>a::text')
        self.add_css('url', '.title>a::attr(href)')
        self.add_css('lastRespStr', 'td:nth-of-type(4)::text')