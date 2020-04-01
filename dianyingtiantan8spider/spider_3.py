# coding: utf-8
# author: QCL
# software: PyCharm Professional Edition 2018.2.8

import threading
import requests
from lxml import etree
from queue import Queue
from dianyingtiantan8spider.useragents import GetRandomUserAgent
from dianyingtiantan8spider.utils import get_page

from models import db, Movie


class Producer(threading.Thread):
    """生产者模型类"""

    def __init__(self, page_url_queue, detail_url_queue, *args, **kwargs):
        """初始化"""
        super(Producer, self).__init__(*args, **kwargs)
        self.page_url_queue = page_url_queue
        self.detail_url_queue = detail_url_queue
        self.base_domain = "https://www.dytt8.net"
        self.proxy_url = "http://127.0.0.1:5000/random"

    def run(self):
        """
        处理列表页子线程启动
        :return:
        """
        while True:
            if self.page_url_queue.empty():
                break
            current_page_url = self.page_url_queue.get()
            try:
                response = get_page(current_page_url)
            except Exception as e:
                print(e.args)
                # 获取代理ip
                proxy = requests.get(self.proxy_url).text
                print("使用代理：{}".format(proxy))
                try:
                    response = requests.get(
                        url=current_page_url,
                        headers={
                            "User-Agent": GetRandomUserAgent().random
                        },
                        proxies={
                            "http": "http://" + proxy,
                            "https": "https://" + proxy
                        }
                    )
                    if response.status_code == 200:
                        self.get_detail_urls(response)
                except Exception as e:
                    print(e.args)
                    print("{} 代理无效！".format(proxy))
                    self.page_url_queue.put(current_page_url)
                    continue
            self.get_detail_urls(response)

    def get_detail_urls(self, response):
        """
        提取详情连接
        :param response: 列表页源码
        :return:
        """
        text = response.text
        html = etree.HTML(text)
        detail_urls = html.xpath('//div[@class="co_content8"]//a[@class="ulink"]/@href')
        detail_urls = list(map(lambda x: self.base_domain + x, detail_urls))
        for detail_url in detail_urls:
            self.detail_url_queue.put(detail_url)
            print(detail_urls)


class Consumer(threading.Thread):
    """消费者模型类"""

    def __init__(self, page_url_queue, detail_url_queue, *args, **kwargs):
        """初始化"""
        super(Consumer, self).__init__(*args, **kwargs)
        self.page_url_queue = page_url_queue
        self.detail_url_queue = detail_url_queue
        self.base_domain = "https://www.dytt8.net"
        self.proxy_url = "http://127.0.0.1:5000/random"

    def run(self):
        """
        处理详情页子程序启动
        :return:
        """
        while True:
            if all([
                self.page_url_queue.empty(),
                self.detail_url_queue.empty()
            ]):
                break
            current_detail_url = self.detail_url_queue.get()
            self.get_detail_page(current_detail_url)

    def get_detail_page(self, current_detail_url):
        """
        获取详情页源代码
        :param current_detail_url: 详情页连接
        :return:
        """
        response = None
        try:
            response = get_page(current_detail_url)
        except Exception as e:
            print(e.args)
            flag = True
            for i in range(5):  # 一部电影连续使用5次代理抓取都失败则丢弃此电影数据
                if flag:
                    # 获取代理ip
                    proxy = requests.get(self.proxy_url).text
                    print("使用代理：{}".format(proxy))
                    try:
                        response = requests.get(
                            url=current_detail_url,
                            headers={
                                "User-Agent": GetRandomUserAgent().random
                            },
                            proxies={
                                "http": "http://" + proxy,
                                "https": "https://" + proxy
                            }
                        )
                        if response.status_code == 200:
                            flag = False
                            self.parse_detail_page(response)
                    except Exception as e:
                        print(e.args)
                        print("{} 代理无效！".format(proxy))
                        # 连续5次使用代理全部失败，则将次电影连接放回队列，等待下一次调度
                        # self.detail_url_queue.put(current_detail_url)
                        continue
        if response:
            self.parse_detail_page(response)

    def parse_detail_page(self, response):
        """
        提取详情信息
        :param response: 详情页源代码
        :return:
        """
        text = response.content.decode("gbk")
        html = etree.HTML(text)
        movie = {}
        title = html.xpath("//div[@class='co_area2']//h1//text()")[0]  # 电影名称
        movie["title"] = title
        cover = html.xpath("//div[@id='Zoom']//img/@src")  # 海报
        if cover:
            movie["cover"] = cover[0]
        infos = html.xpath("//div[@id='Zoom']//text()")
        for index, info in enumerate(infos):
            if info.startswith("◎年　　代"):
                year = info.replace("◎年　　代", "").strip()  # 年代
                movie["year"] = year
            elif info.startswith("◎产　　地"):
                country = info.replace("◎产　　地", "").strip()  # 国家
                movie["country"] = country
            elif info.startswith("◎类　　别"):
                category = info.replace("◎类　　别", "").strip()  # 类别
                movie["category"] = category
            elif info.startswith("◎豆瓣评分"):
                douban_score = info.replace("◎豆瓣评分", "").strip()  # 豆瓣评分
                movie["douban_score"] = douban_score
            elif info.startswith("◎片　　长"):
                duration = info.replace("◎片　　长", "").strip()  # 片长
                movie["duration"] = duration
            elif info.startswith("◎导　　演"):
                director = info.replace("◎导　　演", "").strip()  # 导演
                movie["director"] = director

            # 主演人员名单
            elif info.startswith("◎主　　演"):
                info = info.replace("◎主　　演", "").strip()
                actors = [info]
                for x in range(index + 1, len(infos)):
                    actor = infos[x].strip()
                    if actor.startswith("◎标　　签"):
                        break
                    actors.append(actor)
                movie["actors"] = "".join(actors).strip()
            # 简介
            elif info.startswith("◎简　　介"):
                info = info.replace("◎简　　介", "").strip()
                profiles = []
                for x in range(index + 1, len(infos)):
                    profile = infos[x].strip()
                    if profile.startswith("◎获奖情况"):
                        break
                    profiles.append(profile)
                movie["profile"] = "".join(profiles).strip()
            # 获奖情况
            elif info.startswith("◎获奖情况"):
                info = info.replace("◎获奖情况", "").strip()
                prizes = []
                for x in range(index + 1, len(infos)):
                    prize = infos[x].strip()
                    if prize.startswith("【下载地址】"):
                        break
                    prizes.append(prize)
                movie["prize"] = "".join(prizes).strip()
            # 下载链接
            download_url = html.xpath("//td[@bgcolor='#fdfddf']/a/text()")[0]
            movie["download_url"] = download_url

        print(movie)
        print("=="*100)
        self.write_mysql(movie)

    @staticmethod
    def write_mysql(movie):
        """
        将数据写入数据库
        :param movie: 一部电影相关数据信息
        :return:
        """
        p = Movie(**movie)
        db.session.add(p)
        db.session.commit()


def main():
    page_url_queue = Queue()
    detail_url_queue = Queue()

    producer_thread_li = []

    # page_url入队列
    for i in range(1, 3):
        page_url = "https://www.dytt8.net/html/gndy/dyzz/list_23_{}.html".format(i)
        page_url_queue.put(page_url)

    # 创建2个子线程处理page_url_queue队列，用来获取详情页url地址
    for i in range(2):
        p = Producer(page_url_queue, detail_url_queue)
        producer_thread_li.append(p)
        p.start()

    for thread in producer_thread_li:
        thread.join()

    # 创建5个子线程用来处理detail_url_queue队列，获取电影相关数据信息
    for j in range(5):
        c = Consumer(page_url_queue, detail_url_queue)
        c.start()


if __name__ == '__main__':
    main()
