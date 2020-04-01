# coding: utf-8
# author: QCL
# software: PyCharm Professional Edition 2018.2.8

from lxml import etree
from queue import Queue
from threading import Thread
from dianyingtiantan8spider.use_proxy import SetProxy


class DyTT8Spider(object):
    """抓取电影天堂8最新全部电影"""
    def __init__(self):
        """初始化"""
        self.base_domain = "https://www.dytt8.net"
        self.base_url = "https://www.dytt8.net/html/gndy/dyzz/list_23_{}.html"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/80.0.3987.132 Safari/537.36",
        }

        self.page_url_queue = Queue()  # 初始化一个用来维护列表页url地址的队列
        self.thread_li = []  # 初始化一个用来存储子线程的列表

    def url_in(self):
        """
        url入队列
        :return:
        """
        for i in range(1, 3):
            url = self.base_url.format(i)
            self.page_url_queue.put(url)

    def start(self):
        """
        获取列表页的详情url地址
        :return:
        """
        while True:
            if self.page_url_queue.empty():
                break
            current_page_url = self.page_url_queue.get()
            # 使用阿布云代理隧道获取列表页源码
            response = SetProxy().get_page(current_page_url)
            if response.status_code == 200:
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
            self.get_detail_page(detail_url)
            print(detail_urls)

    def get_detail_page(self, detail_url):
        """
        获取详情页源代码
        :param detail_url: 详情页连接
        :return:
        """
        # 使用阿布云代理隧道获取详情页源码
        response = SetProxy().get_page(detail_url)
        if response.status_code == 200:
            self.parse_detail_page(response)

    @staticmethod
    def parse_detail_page(response):
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
        cover = html.xpath("//div[@id='Zoom']//img/@src")[0]  # 海报
        movie["cover"] = cover
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
                movie["actors"] = actors
            # 简介
            elif info.startswith("◎简　　介"):
                info = info.replace("◎简　　介", "").strip()
                profiles = []
                for x in range(index + 1, len(infos)):
                    profile = infos[x].strip()
                    if profile.startswith("◎获奖情况"):
                        break
                    profiles.append(profile)
                movie["profile"] = profiles
            # 获奖情况
            elif info.startswith("◎获奖情况"):
                info = info.replace("◎获奖情况", "").strip()
                prizes = []
                for x in range(index + 1, len(infos)):
                    prize = infos[x].strip()
                    if prize.startswith("【下载地址】"):
                        break
                    prizes.append(prize)
                movie["prize"] = prizes
            # 下载链接
            download_url = html.xpath("//td[@bgcolor='#fdfddf']/a/text()")[0]
            movie["download_url"] = download_url

        print(movie)
        print("=="*100)

    def run(self):
        """程序入口"""
        # 列表页url地址入队列
        self.url_in()

        # 创建5个子线程
        for i in range(3):
            t = Thread(target=self.start)
            self.thread_li.append(t)
            t.start()

        for thread in self.thread_li:
            thread.join()


if __name__ == '__main__':
    d = DyTT8Spider()
    d.run()
