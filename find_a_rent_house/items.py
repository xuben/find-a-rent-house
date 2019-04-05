# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import datetime
import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import Join, MapCompose, TakeFirst

class RentHouseItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    image_num = scrapy.Field()
    date = scrapy.Field()

def count_processor(self, values):
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
        self.add_css('content', '.topic-richtext>p::text')
        self.add_css('image_num', '.topic-richtext img')
        self.add_css('date', '.topic-doc>h3>span:nth-last-of-type(1)::text')
