#!/usr/bin/env python3
# coding=utf-8
# Version:python3.6.1
# Data:2021/7/3 23:18
# Author:LGSP_Harold
from proxyPoolDb import RedisClient
from proxyPoolCrawler import Crawler

# 代理池的最大数量
POOL_UPPER_THRESHOLD = 1000000


class Getter:
    def __init__(self):
        self.redis = RedisClient()
        self.crawler = Crawler()

    def is_over_threshold(self):
        """
        判断是否达到了代理池限制
        """
        if self.redis.count() >= POOL_UPPER_THRESHOLD:
            return True
        else:
            return False

    def run(self):
        print('获取器开始执行')
        if not self.is_over_threshold():
            """
            调用了 Crawler 类的 CrawlFunc 属性，获取到所有以 crawl 开头的方法列表，依次通过 get_proxies () 方法调用，得到各个方法抓取到的代理
            """
            for callback_label in range(self.crawler.__CrawlFuncCount__):
                callback = self.crawler.__CrawlFunc__[callback_label]
                proxies = self.crawler.get_proxies(callback)
                for proxy in proxies:
                    self.redis.add(proxy)


if __name__ == '__main__':
    getter = Getter()
    getter.run()
