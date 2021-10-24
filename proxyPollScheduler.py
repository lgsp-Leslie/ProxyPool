#!/usr/bin/env python3
# coding=utf-8
# Version:python3.6.1
# Data:2021/7/3 23:41
# Author:LGSP_Harold
import time

from proxyPoolGetter import Getter
from proxyPoolTester import Tester
from multiprocessing import Process
from proxyPoolAPI import app

# 每隔3600秒进行一次代理检测
TESTER_CYCLE = 20
# 每隔7200秒进行一次代理获取
GETTER_CYCLE = 7200
# 测试模块、获取模块、接口模块的开关
TESTER_ENABLED = True
GETTER_ENABLED = False
API_ENABLED = True

# 接口模块的地址和端口
API_HOST = 'localhost'
API_PORT = 5000


class Scheduler:
    def schedule_tester(self, cycle=TESTER_CYCLE):
        """
        定时测试代理
        """
        tester = Tester()
        while True:
            print('测试器开始运行')
            tester.run()
            time.sleep(cycle)

    def schedule_getter(self, cycle=GETTER_CYCLE):
        """
        定时获取代理
        """
        getter = Getter()
        while True:
            print('开始抓取代理')
            getter.run()
            time.sleep(cycle)

    def schedule_api(self):
        """
        开启API
        """
        app.run(API_HOST, API_PORT)

    def run(self):
        # 分别判断了三个模块的开关，如果开启的话，就新建一个 Process 进程，设置好启动目标，然后调用 start () 方法运行，这样三个进程就可以并行执行，互不干扰
        print('代理池开始运行')
        if GETTER_ENABLED:
            getter_process = Process(target=self.schedule_getter)
            getter_process.start()

        if TESTER_ENABLED:
            tester_process = Process(target=self.schedule_tester)
            tester_process.start()

        if API_ENABLED:
            api_process = Process(target=self.schedule_api)
            api_process.start()


if __name__ == '__main__':
    scheduler = Scheduler()
    scheduler.run()
