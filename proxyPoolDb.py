#!/usr/bin/env python3
# coding=utf-8
# Version:python3.6.1
# Data:2021/7/2 15:55
# Author:LGSP_Harold
from random import choice

import redis

# 测试代理通过分值
MAX_SCORE = 100
# 失效移除代理分值
MIN_SCORE = 0
# 爬取代理初始化分值
INITIAL_SCORE = 10
# Redis地址
REDIS_HOST = 'localhost'
# Redis端口
REDIS_PORT = 6379
# Redis密码
REDIS_PASSWORD = None
# Redis键名
REDIS_KEY = 'proxies'
# Redis数据库
DB = 9


class RedisClient:
    def __init__(self, host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, db=DB):
        """
        初始化Redis连接
        :param host: Redis地址
        :param port: Redis端口
        :param password: Redis密码
        """
        self.db = redis.StrictRedis(host=host, port=port, password=password, db=db, decode_responses=True)

    def add(self, proxy, score=INITIAL_SCORE):
        """
        添加代理，设置初始化分值
        :param proxy: 代理
        :param score: 分值
        :return: 添加结果
        """
        if not self.db.zscore(REDIS_KEY, proxy):
            mapping = {
                proxy: score
            }
            self.db.zadd(REDIS_KEY, mapping)

    def random(self):
        """
        随机获取有效代理，首先尝试获取最高分值代理，如果最高分值不存在，则按照排名获取，否则异常
        :return: 随机代理
        """
        result = self.db.zrangebyscore(REDIS_KEY, MAX_SCORE, MAX_SCORE)
        if len(result):
            return choice(result)
        else:
            print('没有代理')

    def decrease(self, proxy):
        """
        检测代理，并对失效代理分值进行减分操作，小于最小值则删除
        :param proxy: 代理
        :return: 修改后的代理分值
        """
        score = self.db.zscore(REDIS_KEY, proxy)
        if score and score > MIN_SCORE:
            print('代理', proxy, '当前分数', score, '减1')
            return self.db.zincrby(REDIS_KEY, -1, proxy)
        else:
            print('代理', proxy, '当前分数', score, '移除')
            return self.db.zrem(REDIS_KEY, proxy)

    def exists(self, proxy):
        """
        判断爬取代理是否存在集合中
        :param proxy: 代理
        :return: 是否存在
        """
        return not self.db.zscore(REDIS_KEY, proxy) is None

    def max(self, proxy):
        """
        将代理的分值设置为MAX_SCORE
        :param proxy: 代理
        :return: 设置结果
        """
        print('代理', proxy, '可用，设置为', MAX_SCORE)
        return self.db.zadd(REDIS_KEY, {proxy: MAX_SCORE})

    def count(self):
        """
        获取当前集合的元素个数
        :return: 数量
        """
        return self.db.zcard(REDIS_KEY)

    def all(self):
        """
        获取所有的代理列表，供检测使用
        :return: 全部代理列表
        """
        return self.db.zrangebyscore(REDIS_KEY, MIN_SCORE, MAX_SCORE)
