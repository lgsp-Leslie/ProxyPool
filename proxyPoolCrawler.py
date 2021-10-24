#!/usr/bin/env python3
# coding=utf-8
# Version:python3.6.1
# Data:2021/7/3 12:00
# Author:LGSP_Harold
import json
import re
import time

import requests
from lxml import etree


# 设置全局爬取页数
PAGE_COUNT = 2

# 设置爬取代理的URL
GITHUBUSERCONTENT_URL = 'https://raw.githubusercontent.com/fate0/proxylist/master/proxy.list'
FATEZERO_URL = 'http://proxylist.fatezero.org/proxy.list'

_66IP_URL = 'http://www.66ip.cn/{}.html'
_66IP_PAGE_COUNT = PAGE_COUNT

XILADAILI_URL = 'http://www.xiladaili.com/gaoni/{}/'
XILADAILI_PAGE_COUNT = PAGE_COUNT

IHUAN_TODAY_URL = 'https://ip.ihuan.me/today/{path}.html'
IHUAN_URL = 'https://ip.ihuan.me/{}'
IHUAN_PAGE_COUNT = PAGE_COUNT

_89IP_URL = 'https://www.89ip.cn/index_{}.html'
_89IP_PAGE_COUNT = PAGE_COUNT

IP3366_URL = 'http://www.ip3366.net/?stype=1&page={}'
IP3366_PAGE_COUNT = PAGE_COUNT

JIANGXIANLI_URL = 'https://ip.jiangxianli.com/?page={}'
JIANGXIANLI_PAGE_COUNT = PAGE_COUNT

KUAIDAILI_URL = 'https://www.kuaidaili.com/free/inha/{}/'
KUAIDAILI_PAGE_COUNT = PAGE_COUNT

TAIYANGHTTP_URL = 'http://www.taiyanghttp.com/free/page{}/'
TAIYANGHTTP_PAGE_COUNT = PAGE_COUNT


# 请求要爬取代理的URL
class GetPage:
    def get_page(self, url):
        try:
            html = requests.get(url)
            # 获取请求到的URL的编码，并设置；如果没有，默认设置为UTF-8
            if requests.utils.get_encodings_from_content(html.text):
                html.encoding = requests.utils.get_encodings_from_content(html.text)[0]
            else:
                html.encoding = 'utf-8'
            if html:
                time.sleep(1)
                # 解析字符串格式的HTML文档对象，转变成_Element对象
                doc = etree.HTML(html.text)
                return doc
        except Exception as e:
            print(e)
        return None


class ProxyMetaclass(type):
    """
    在 __new__() 方法中遍历了 attrs 属性，像遍历一个字典一样，键名对应的就是方法的名称，接下来判断其开头是否是 crawl，
    如果是，则将其加入到 CrawlFunc 属性中，将所有以 crawl 开头的方法定义成了一个属性，就成功动态地获取到所有以 crawl 开头的方法列表
    """
    def __new__(cls, name, bases, attrs):
        count = 0
        attrs['__CrawlFunc__'] = []
        for k, v in attrs.items():
            if 'crawl_' in k:
                attrs['__CrawlFunc__'].append(k)
                count += 1
        attrs['__CrawlFuncCount__'] = count
        return type.__new__(cls, name, bases, attrs)


class Crawler(object, metaclass=ProxyMetaclass):
    # 借助于元类（ProxyMetaclass）来实现将所有以 crawl 开头的方法调用一遍，获取每个方法返回的代理并组合成列表形式返回
    def get_proxies(self, callback):
        proxies = []
        for proxy in eval("self.{}()".format(callback)):
            print('成功获取到代理', proxy)
            proxies.append(proxy)
        return proxies

    # githubusercontent需要翻墙，等同于fatezero
    def crawl_githubusercontent(self):
        """
        获取GitHub开源代理
        :return: 代理
        """
        response = requests.get(FATEZERO_URL)
        proxies_list = response.text.split('\n')
        for proxy_str in proxies_list:
            if proxy_str == '':
                continue
            proxy_json = json.loads(proxy_str)
            host = proxy_json['host']
            port = proxy_json['port']
            yield ':'.join([host, str(port)])

    def crawl_66ip(self):
        """
        获取66ip代理
        :return: 代理
        """
        urls = [_66IP_URL.format(page) for page in range(1, _66IP_PAGE_COUNT + 1)]
        for url in urls:
            print('Crawling', url)
            doc = GetPage().get_page(url)
            trs = doc.xpath('//div[@class="layui-row layui-col-space15"]//table//tr')
            for tr in trs:
                try:
                    host = tr.xpath('./td[1]/text()')[0]
                    if host == 'ip' or host == '127.0.0.1':
                        continue
                    port = tr.xpath('./td[2]/text()')[0]
                    yield ':'.join([host, port])
                except Exception as e:
                    print(e)
                    continue

    def crawl_xiladaili(self):
        """
        获取西拉代理
        :return: 代理
        """
        urls = [XILADAILI_URL.format(page) for page in range(1, XILADAILI_PAGE_COUNT + 1)]
        for url in urls:
            print('Crawling', url)
            doc = GetPage().get_page(url)
            if doc is not None:
                trs = doc.xpath('//div[@class="mt-0 mb-2 table-responsive"]/table//tr')
                for tr in trs:
                    try:
                        if not tr.xpath('./td[1]/text()'):
                            continue
                        str_url = tr.xpath('./td[1]/text()')[0]
                        yield str_url
                    except:
                        continue

    def crawl_ihuan_today(self):
        """
        获取IHUAN当日代理
        :return: 代理
        """
        path = time.strftime('%Y/%m/%d/%H', time.localtime())
        url = IHUAN_TODAY_URL.format(path=path)
        doc = requests.get(url)
        if doc is not None:
            ip_address = re.compile('([\d:\.]*).*?<br>')
            hosts_ports = ip_address.findall(doc.text)
            for addr in hosts_ports:
                try:
                    if addr == '':
                        continue
                    addr_split = addr.split(':')
                    if len(addr_split) == 2:
                        host = addr_split[0]
                        port = addr_split[1]
                        yield ':'.join([host, port])
                except:
                    continue

    def crawl_ihuan(self):
        """
        获取IHUAN实时代理
        :return: 代理
        """
        url = IHUAN_URL
        doc = GetPage().get_page(url)
        page = ''
        for item in range(1, IHUAN_PAGE_COUNT + 1):
            if doc is not None:
                trs = doc.xpath('//table[@class="table table-hover table-bordered"]/tbody/tr')
                for tr in trs:
                    try:
                        host = tr.xpath('./td[1]/a/text()')[0]
                        port = tr.xpath('./td[2]/text()')[0]
                        yield ':'.join([host, port])
                    except:
                        continue

                page = doc.xpath('//ul[@class="pagination"]/li[8]/a/@href')[0]
                url = IHUAN_URL.format(page)
                print(url)
                doc = GetPage().get_page(url)

    def crawl_89ip(self):
        """
        获取89ip代理
        :return: 代理
        """
        urls = [_89IP_URL.format(page) for page in range(1, _66IP_PAGE_COUNT + 1)]
        for url in urls:
            print('Crawling', url)
            doc = GetPage().get_page(url)
            if doc is not None:
                trs = doc.xpath('//table[@class="layui-table"]/tbody/tr')
                for tr in trs:
                    try:
                        host = tr.xpath('./td[1]/text()')[0].strip()
                        port = tr.xpath('./td[2]/text()')[0].strip()
                        yield ':'.join([host, port])
                    except:
                        continue

    def crawl_ip3366(self):
        """
        获取ip3366代理
        :return: 代理
        """
        urls = [IP3366_URL.format(page) for page in range(1, IP3366_PAGE_COUNT + 1)]
        for url in urls:
            print('Crawling', url)
            doc = GetPage().get_page(url)
            if doc is not None:
                trs = doc.xpath('//table[@class="table table-bordered table-striped"]/tbody/tr')
                for tr in trs:
                    try:
                        host = tr.xpath('./td[1]/text()')[0]
                        port = tr.xpath('./td[2]/text()')[0]
                        yield ':'.join([host, port])
                    except:
                        continue

    def crawl_jiangxianli(self):
        """
        获取ip3366代理
        :return: 代理
        """
        urls = [JIANGXIANLI_URL.format(page) for page in range(1, JIANGXIANLI_PAGE_COUNT + 1)]
        for url in urls:
            print('Crawling', url)
            doc = GetPage().get_page(url)
            if doc is not None:
                trs = doc.xpath('//table[@class="layui-table"]/tbody/tr')
                for tr in trs:
                    try:
                        host = tr.xpath('./td[1]/text()')[0]
                        port = tr.xpath('./td[2]/text()')[0]
                        yield ':'.join([host, port])
                    except:
                        continue

    def crawl_kuaidaili(self):
        """
        获取kuaidaili代理
        :return: 代理
        """
        urls = [KUAIDAILI_URL.format(page) for page in range(1, KUAIDAILI_PAGE_COUNT + 1)]
        for url in urls:
            print('Crawling', url)
            doc = GetPage().get_page(url)
            time.sleep(3)
            if doc is not None:
                trs = doc.xpath('//table[@class="table table-bordered table-striped"]/tbody/tr')
                for tr in trs:
                    try:
                        host = tr.xpath('./td[1]/text()')[0]
                        port = tr.xpath('./td[2]/text()')[0]
                        yield ':'.join([host, port])
                    except:
                        continue

    #
    def crawl_taiyanghttp(self):
        """
        获取taiyanghttp代理
        :return: 代理
        """
        urls = [TAIYANGHTTP_URL.format(page) for page in range(1, TAIYANGHTTP_PAGE_COUNT + 1)]
        for url in urls:
            print('Crawling', url)
            doc = GetPage().get_page(url)
            if doc is not None:
                trs = doc.xpath('//div[@id="ip_list"]/div[@class="tr ip_tr"]')
                for tr in trs:
                    try:
                        host = tr.xpath('.//div[1]/text()')[0]
                        port = tr.xpath('.//div[2]/text()')[0]
                        yield ':'.join([host, port])
                    except:
                        continue
