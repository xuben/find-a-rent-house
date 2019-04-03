import re

class RentChecker:

    # 可接受的最大价格
    max_price = 2600
    # 提取价格的关键字
    price_keywords = [r'(\d{3,5})(元|/?月|每月|一个月|一月)', r'租金(\d{3,5})']

    def checkPrice(self, content):
        for keyword in self.price_keywords:
            priceStr = re.search(keyword, content)
            if priceStr:
                price = int(priceStr[1])
                if price > self.max_price:
                    return False
        return True

checker = RentChecker()