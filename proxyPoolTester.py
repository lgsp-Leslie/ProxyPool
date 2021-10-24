#!/usr/bin/env python3
# coding=utf-8
# Version:python3.6.1
# Data:2021/7/3 23:32
# Author:LGSP_Harold
import asyncio
import time

import aiohttp
from aiohttp import ClientError, ClientConnectorError
from asyncio import TimeoutError

from proxyPoolDb import RedisClient

# 正常状态码
VALID_STATUS_CODES = [200]
# 检测地址
TEST_URL = 'https://www.baidu.com'
# 并发数，windows509，Linux1024，超过报错ValueError: too many file descriptors in select()
BATCH_TEST_SIZE = 500


class Tester(object):
    def __init__(self):
        self.redis = RedisClient()

    async def test_single_proxy(self, proxy):
        """
        异步请求库 aiohttp 来进行检测，测试单个代理
        :param proxy: 待检测的单个代理
        :return: None
        """
        # 创建链接池
        conn = aiohttp.TCPConnector(verify_ssl=False)
        # 方法内部首先创建了 Aiohttp 的 ClientSession 对象，可直接调用该对象的 get () 方法来访问页面
        async with aiohttp.ClientSession(connector=conn) as session:
            try:
                if isinstance(proxy, bytes):
                    proxy = proxy.decode('utf-8')
                real_proxy = 'http://' + proxy
                print('正在测试', proxy)
                async with session.get(TEST_URL, proxy=real_proxy, timeout=15) as response:
                    if response.status in VALID_STATUS_CODES:
                        self.redis.max(proxy)
                        print('代理可用', proxy)
                    else:
                        self.redis.decrease(proxy)
                        print('请求响应码不合法', proxy)
            except (ClientError, ClientConnectorError, TimeoutError, AttributeError):
                self.redis.decrease(proxy)
                print('代理请求失败', proxy)

    def run(self):
        """
        测试主函数
        :return: None
        """
        print('测试器开始运行')
        try:
            proxies = self.redis.all()
            loop = asyncio.get_event_loop()
            # 批量测试
            for i in range(0, len(proxies), BATCH_TEST_SIZE):
                test_proxies = proxies[i:i + BATCH_TEST_SIZE]
                tasks = [self.test_single_proxy(proxy) for proxy in test_proxies]
                loop.run_until_complete(asyncio.wait(tasks))
                time.sleep(5)
        except Exception as e:
            print('测试器发生错误', e.args)


if __name__ == '__main__':
    tester = Tester()
    tester.run()
