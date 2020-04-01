# coding: utf-8
# author: QCL
# software: PyCharm Professional Edition 2018.2.8

import requests
from requests.exceptions import ConnectionError


base_headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/"
              "signed-exchange;v=b3;q=0.9",
    "Accept-Language": "en,en-US;q=0.9,zh-CN;q=0.8,zh;q=0.7",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Host": "www.ygdy8.net",
    "If-Modified-Since": "Wed, 25 Mar 2020 00:50:11 GMT",
    "If-None-Match": '"80236a563f2d61:84a"',
    "Referer": "https://www.dytt8.net/",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "cross-site",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/80.0.3987.132 Safari/537.36",
}


def get_page(dst_url, options={}):
    """
    获取网页源代码
    :param dst_url: 目标网页url地址
    :param options: 键值对的可变参数 关键字参数
    :return:
    """
    headers = dict(base_headers, **options)
    try:
        response = requests.get(
            url=dst_url,
            headers=headers
        )
        if response.status_code == 200:
            print({"info": "抓取成功...", "url": dst_url, "status_code": response.status_code})
            return response
    except ConnectionError:
        print("抓取失败！".format(dst_url))
        raise ConnectionError

