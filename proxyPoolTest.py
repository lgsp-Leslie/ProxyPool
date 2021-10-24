#!/usr/bin/env python3
# coding=utf-8
# Version:python3.6.1
# Data:2021/7/4 13:49
# Author:LGSP_Harold
import requests

PROXY_POOL_URL = 'http://127.0.0.1:5000/get_proxy'


def get_proxy():
    try:
        response = requests.get(PROXY_POOL_URL)
        if response.status_code == 200:
            return response.text
    except ConnectionError:
        return None


for _ in range(9):
    proxy = get_proxy()
    proxies = {
        'http': 'http://' + proxy,
        'https': 'https://' + proxy
    }
    try:
        response = requests.get('http://httpbin.org/ip', proxies=proxies, timeout=(5, 9))
        print(response.text)
    except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout) as e:
        print('Error：', e.args)
