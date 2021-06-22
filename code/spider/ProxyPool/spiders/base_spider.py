import requests
from lxml import etree
from domain import Proxy
from utils.http import get_request_header


class BaseSpider(object):
    urls = []  # 代理IP网址的URL的列表
    group_xpath = ''  # 分组XPATH, 获取包含代理IP信息标签列表的XPATH
    detail_xpath = {}  # 组内XPATH, 获取代理IP详情的信息XPATH

    def __init__(self, urls=[], group_xpath=None, detail_xpath={}):

        if urls:  # 如果urls中有数据
            self.urls = urls
        if group_xpath:  # 如果group_xpath中有数据
            self.group_xpath = group_xpath
        if detail_xpath:  # 如果detail_xpath中有数据
            self.detail_xpath = detail_xpath

    def get_page_from_url(self, url):
        response = requests.get(url, headers=get_request_header())
        return response.content

    def get_first(self, lis):
        return lis[0].strip() if len(lis) != 0 else ''

    def get_proxies_from_page(self, page):
        """解析页面数据"""
        element = etree.HTML(page)
        trs = element.xpath(self.group_xpath)
        # print(len(trs))
        for tr in trs:
            ip = self.get_first(tr.xpath(self.detail_xpath['ip']))
            port = self.get_first(tr.xpath(self.detail_xpath['port']))
            area = self.get_first(tr.xpath(self.detail_xpath['area']))
            proxy = Proxy(ip, port, area=area)
            # 返回代理IP
            yield proxy

    def get_proxies(self):
        """获取代理IP信息"""
        # - 遍历URL列表, 获取URL
        for url in self.urls:
            # - 根据发送请求, 获取页面数据
            page = self.get_page_from_url(url)
            # - 解析页面, 提取数据
            proxies = self.get_proxies_from_page(page)
            # - 把数据返回
            yield from proxies


if __name__ == '__main__':
    config = {
        'urls': ['http://www.ip3366.net/free/?stype={}&page={}'.format(
            i, j) for j in range(1, 10) for i in range(1, 4, 2)],
        'group_xpath': '//*[@id="list"]/table/tbody/tr',
        'detail_xpath': {
            'ip': './td[1]/text()', 'port': './td[2]/text()', 'area': './td[5]/text()'}
    }
    # 创建通用代理对象
    base_spider = BaseSpider(**config)
    for proxy in base_spider.get_proxies():
        print(proxy)
