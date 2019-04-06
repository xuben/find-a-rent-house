import scrapy
import datetime
import re
import os
import time
import random
import sys
import find_a_rent_house.spiders.checker as checker
import find_a_rent_house.items as items

class DoubanRentSpider(scrapy.Spider):
    name = 'douban-rent'
    start_urls = [
        'https://www.douban.com/group/shanghaizufang/discussion',
    ]
    custom_settings = {
        'ROBOTSTXT_OBEY': False,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'DOWNLOAD_DELAY': 4
    }
    itemsPerPage = 25
    page = 0
    # 黑名单阈值
    blacklistThreshold = 4
    # 搜索的关键字
    keywords = r'((4|四).{0,5}号线?)|海伦路|宝山路|上海火车站|中潭路\
        |镇坪路|曹杨路|金沙江路|中山公园|延安西路|虹桥路|宜山路|临平路|大连路\
            |杨树浦路|浦东大道|世纪大道|浦电路|蓝村路|四川北路|天潼路|南京东路\
                |豫园|老西门|新天地|陕西南路|上海图书馆|交通大学|虹桥路|宋园路|伊犁路'
    ex_keywords = r'限女|百套房源|已租'
    
    # 最近3天的发帖
    period_seconds = 60 * 60 * 24 * 3
    # 最近2天的回复
    response_period_seconds = 60 * 60 * 24 * 2
    # 中介名单
    blacklist = []
    # 已经浏览过的历史页面
    history = []
    # 作者名单
    authorMap = {}
    # 本次启动浏览的页面数量
    page_viewed = 0
    # 每次启动浏览的最大页面数量
    max_page_viewed = 250

    def __init__(self):
        with open('data/blacklist', mode='r+', encoding='utf-8') as f:
            self.blacklist = f.readlines()
            self.logger.info("loading blacklist, length:%d", len(self.blacklist))
        with open('data/history', mode='r+', encoding='utf-8') as f:
            self.history = f.readlines()

    def parseEntry(self, response):
        item_loader = items.RentHouseItemLoader(items.RentHouseItem(), response)
        item = item_loader.load_item()
        if 'full_title' in item:
            content = item['full_title'] + '\n' + item['content']
        else:
            content = item['title'] + '\n' + item['content']
        self.logger.info('visiting page:%s', response.url)
        # 加入已浏览过的历史页面中
        self.history.append(response.url)
        with open('data/history', mode='a+', encoding='utf-8') as f:
            f.writelines(response.url + '\n')
        # 发帖时间太久远
        now = datetime.datetime.now()
        delta = now - item['date']
        if (delta.total_seconds() > self.period_seconds):
            return
        # 图片数量
        if (item['image_num'] == 0):
            return
        # 价格判断
        if not checker.checker.checkPrice(content):
            return
        if (re.search(self.ex_keywords, content)):
            return
        if (not re.search(self.keywords, content)):
            return
        with open('data/result', mode='a+', encoding='utf-8') as f:
            if 'full_title' in item:
                f.writelines(item['full_title'])
            else:
                f.writelines(item['title'])
            f.writelines(response.url)
            return

    def parse(self, response):
        # yield scrapy.Request(url="https://www.douban.com/group/topic/137594429/", callback=self.parseEntry)
        # return
        # 防止每次请求数量过多被禁止访问
        if (self.page_viewed >= self.max_page_viewed):
            self.page_viewed = 0
            return
        for entry in response.css('#content tr'):
            item_loader = items.CatalogItemLoader(items.CatalogItem(), entry)
            item = item_loader.load_item()
            if ('title' not in item or 'author' not in item or 'url' not in item):
                continue
            # 作者在黑名单中
            if (item['author'] in self.blacklist):
                continue
            # 已经浏览过
            if (item['url'] in self.history):
                continue
            # 最后回复时间是否最近
            now = datetime.datetime.now()
            lastRespDate = None
            if (item['lastRespStr'].index(':')):
                lastRespDate = datetime.datetime.strptime('2019-' + item['lastRespStr'], '%Y-%m-%d %H:%M')
            else:
                lastRespDate = datetime.datetime.strptime(item['lastRespStr'], '%Y-%m-%d')
            if ((now - lastRespDate).total_seconds() > self.response_period_seconds):
                return
            # 作者最近发帖次数
            count = 1
            if (item['author'] not in self.authorMap):
                count = self.authorMap[item['author']] = 1
            else:
                count = self.authorMap[item['author']] = self.authorMap[item['author']] + 1
            if (count >= self.blacklistThreshold):
                # 加入黑名单
                self.blacklist.append(item['author'])
                with open('data/blacklist', mode='a+', encoding='utf-8') as f:
                    f.writelines(item['author'] + '\n')
                continue
            # 价格判断
            if not checker.checker.checkPrice(item['title']):
                continue
            # 标题关键字过滤
            if (re.search(self.ex_keywords, item['title'])):
                continue
            yield response.follow(url=item['url'], callback=self.parseEntry)
        self.page = self.page + 1
        yield scrapy.Request(self.start_urls[0] + '?start=' + str(self.page * self.itemsPerPage), callback = self.parse)