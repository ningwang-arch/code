import requests
from lxml import etree

url = 'https://www.kuaidaili.com/free/inha/1/'
html = requests.get(url).content.decode()
element = etree.HTML(html)
groups = element.xpath('//*[@id="list"]/table/tbody/tr')
for item in groups:
    ip = item.xpath('./td[1]//text()')
    print(ip)
