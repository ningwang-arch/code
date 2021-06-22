from spiders.base_spider import BaseSpider


class Ip3366Spider(BaseSpider):
    urls = ['http://www.ip3366.net/free/?stype={}&page={}'.format(
        i, j) for j in range(1, 10) for i in range(1, 4, 2)]
    group_xpath = '//*[@id="list"]/table/tbody/tr'
    detail_xpath = {
        'ip': './td[1]/text()', 'port': './td[2]/text()', 'area': './td[5]/text()'}


class ProxylistplusSpider(BaseSpider):
    urls = [
        'https://list.proxylistplus.com/Fresh-HTTP-Proxy-List-{}'.format(i) for i in range(1, 7)]
    group_xpath = '//*[@id="page"]/table[2]/tr[position()>2]'
    detail_xpath = {
        'ip': './td[2]/text()', 'port': './td[3]/text()', 'area': './td[5]/text()'}


class KuaidailiSpider(BaseSpider):
    urls = [
        'https://www.kuaidaili.com/free/inha/{}/'.format(i) for i in range(1, 10)]
    group_xpath = '//*[@id="list"]/table/tbody/tr'
    detail_xpath = {
        'ip': './td[1]/text()', 'port': './td[2]/text()', 'area': './td[5]/text()'}


if __name__ == '__main__':
    spider = KuaidailiSpider()
    for proxy in spider.get_proxies():
        print(proxy)
