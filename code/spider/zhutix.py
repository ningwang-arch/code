import os
import requests
import time
import json
from lxml import etree

VIDEO_DIR = './video'

PAGE_NUM = 1

# CCODE, UTID, CKEY, BASE and HEADERS are fixed values, don't change them!!!
CCODE = '0512'
CLIENT_IP = '192.168.0.1'
UTID = 'VUNIGRhqvyYCAXE57Q%2Bj%2FKjI'
CKEY = 'DIl58SLFxFNndSV1GFNnMQVYkx1PP5tKe1siZu%2F86PR1u%2FWh1Ptd%2BWOZsHHWxysSfAOhNJpdVWsdVJNsfJ8Sxd8WKVvNfAS8aS8fAOzYARzPyPc3JvtnPHjTdKfESTdnuTW6ZPvk2pNDh4uFzotgdMEFkzQ5wZVXl2Pf1%2FY6hLK0OnCNxBj3%2Bnb0v72gZ6b0td%2BWOZsHHWxysSo%2F0y9D2K42SaB8Y%2F%2BaD2K42SaB8Y%2F%2BahU%2BWOZsHcrxysooUeND'
BASE = 'https://ups.youku.com/ups/get.json?vid={}&ccode={}&client_ip={}&utid={}&client_ts={}&ckey={}'
HEADERS = {
    'referer': 'https://player.youku.com/',
}

error_list = []

if not os.path.exists(VIDEO_DIR):
    os.makedirs(VIDEO_DIR)

for num in range(1, PAGE_NUM+1):
    url = 'https://zhutix.com/animated/page/{}'.format(num)
    response = requests.get(url)
    html = response.content.decode('utf-8')
    element = etree.HTML(html)
    content_list = element.xpath(
        '//*[@id="post-list"]/ul/li/div/div/a[1]//@href')
    for i in range(len(content_list)):
        res = requests.get(content_list[i])
        html = res.content.decode('utf-8')
        ele = etree.HTML(html)
        title = ele.xpath(
            '//*[@id="primary-home"]/div[1]/section[2]/div[1]/div[1]/h3//text()')[0]
        vid_url = ele.xpath(
            '//*[@id="primary-home"]/div[1]/section[1]/div/iframe//@src')[0]
        vid = vid_url[vid_url.rfind('/')+1:]
        client_ts = int(time.time())

        url = BASE.format(vid, CCODE,
                          CLIENT_IP, UTID, client_ts, CKEY)
        res = requests.get(url, headers=HEADERS)
        video_url = (json.loads(res.text)['data']['stream'])[
            2]['segs'][0]['cdn_url']
        try:
            video = requests.get(video_url).content

            filename = VIDEO_DIR+('/{}.mp4'.format(title))

            with open(filename, 'wb') as f:
                f.write(video)
            print('Page'+str(num)+', '+title+' is finished! ')
        except Exception:
            error_list.append(content_list[i])
if not error_list:
    print('\nAll tasks are finished!')
else:
    print(error_list)
