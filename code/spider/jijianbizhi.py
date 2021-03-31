import requests
import json
import time
import hashlib


url = 'https://api.zzzmh.cn/bz/getJson'


contentType = 'application/json'
location = 'bz.zzzmh.cn'
sign = 'error'
timestamp = str(int(time.time()*1000))
data = contentType+location+sign+timestamp

access = hashlib.sha256(data.encode('utf-8')).hexdigest()

headers = {
    'access': access,
    'content-type': contentType,
    'location': location,
    'sign': sign,
    'timestamp': timestamp,
    'user-agent': 'Mozilla/5.0 (X11 Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36'
} 

img_headers = {
    'cookie':
    '__cfduid=dadbd925e21bd1950f7c0a0da7ba21b791592988781',
    'user-agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36'
}
payload = {
    'pageNum': 1,
    'target': "index"
}  # 该json中的pageNum代表第几页,可通过循环赋值来获取更多图片链接
response = requests.post(url, data=json.dumps(payload), headers=headers)
temp = json.loads(response.text)
contents = temp['result']['records']
img_urls = []
for content in contents:
    ret = content['i']
    img_url = 'https://w.wallhaven.cc/full/' + ret[
        0:
        2] + '/wallhaven-' + ret + '.jpg'  # https://w.wallhaven.cc/full/nk/wallhaven-nk1314.jpg
    img_urls.append(img_url)

# 本爬虫核心在于图片链接的构造,图片下载方式不变

# print(img_urls)
r = requests.get(img_urls[0], headers=headers, stream=True)
chunk_size = 128
content_size = int(r.headers['content-length'])
size = 0
print("文件大小：" + str(round(float(content_size / 1024 / 1024), 4)) + "[MB]")
path = "pic.jpg"
with open(path, 'wb') as image:
    # r = r.content
    for chunk in r.iter_content(chunk_size=chunk_size):
        image.write(chunk)
        size = len(chunk) + size
        print('\r' + "已经下载：[" + int(size / content_size * 100) * ">" + "] 【" +
              str(round(size / 1024 / 1024, 2)) + "MB】" + "【" +
              str(round(float(size / content_size) * 100, 2)) + "%" + "】",
              end="")
