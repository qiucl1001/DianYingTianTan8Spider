# coding: utf-8
# author: QCL
# software: PyCharm Professional Edition 2018.2.8

import requests


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


class SetProxy(object):
    """构建一个代理设置类"""

    @staticmethod
    def set_proxy_meta():
        """构建代理"""
        # 代理服务器
        proxyHost = "http-dyn.abuyun.com"
        proxyPort = "9020"

        # 代理隧道验证信息购买代理后需手动设置
        # (HTTP隧道代理列表--->动态版--->{通行证书：proxyUser, 通行秘钥：proxyPass})
        proxyUser = "H281536S5025633D"
        proxyPass = "A137BB48995E7B55"

        proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
            "host": proxyHost,
            "port": proxyPort,
            "user": proxyUser,
            "pass": proxyPass
        }

        proxies = {
            "http": proxyMeta,
            "https": proxyMeta
        }

        print(proxies)
        return proxies

    def get_page(self, url):
        """
        获取网页源代码
        :param url: 请求网页资源url
        :return: response<网页源代码> None<抓取页面失败，返回空>
        """
        proxies = self.set_proxy_meta()
        try:
            resp = requests.get(
                url=url,
                proxies=proxies,
                verify=False
            )
            current_url = resp.url
            status_code = resp.status_code
            if resp.status_code == 200:
                print({"info": "抓取成功...", "current_url": current_url, "status_code": status_code})
                return resp
            else:
                print({"info": "抓取失败...", "url": url, "status_code": status_code})
                print("重新发送请求！")
                self.get_page(url)
        except ConnectionError:
            print("连接失败...重新发送请求！")
            self.get_page(url)


if __name__ == '__main__':
    page_source = SetProxy()
    response = page_source.get_page("https://www.dytt8.net/html/gndy/dyzz/list_23_1.html")
    print(response.text)
