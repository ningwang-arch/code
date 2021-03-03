# -*- coding: utf-8 -*-
import re
import os

import hmac
import time
import json
import uuid
import urllib3
import hashlib
import requests
from urllib import parse


urllib3.disable_warnings()
global_url = "https://picaapi.picacomic.com/"
api_key = "C69BAF41DA5ABD1FFEDC6D2FEA56B"
secret_key = "~d}$Q7$eIni=V)9\\RK/P.RM4;9[7|@/CA}b~OW!3?EV`:<>M7pddUBL5n|0/*Cn"
uuid_s = str(uuid.uuid4()).replace("-", "")
header = {
    "api-key": "C69BAF41DA5ABD1FFEDC6D2FEA56B",
    "accept": "application/vnd.picacomic.com.v1+json",
    "app-channel": "2",
    "time": 0,
    "nonce": "",
    "signature": "encrypt",
    "app-version": "2.2.1.3.3.4",
    "app-uuid": "418e56fb-60fb-352b-8fca-c6e8f0737ce6",
    "app-platform": "android",
    "app-build-version": "45",
    "Content-Type": "application/json; charset=UTF-8",
    "User-Agent": "okhttp/3.8.1",
}
proxies = {
    "http": "http://127.0.0.1:8889",
    "https": "http://127.0.0.1:8889"
}


class Pica:

    def __init__(self, account, password):
        self.path = "/home/eclipse/Pictures/picacg/"
        self.account = account
        self.password = password
        self.header = header.copy()
        self.uuid_s = str(uuid.uuid4()).replace("-", "")
        self.header["nonce"] = self.uuid_s

    def post(self, url, data=None):
        ts = str(int(time.time()))
        self.header["time"] = ts
        self.header["signature"] = self.encrypt(url, ts, "POST", self.uuid_s)
        return requests.post(url=url, data=data, headers=self.header, verify=False, proxies=proxies)

    def get(self, url):
        ts = str(int(time.time()))
        self.header["time"] = ts
        self.header["signature"] = self.encrypt(url, ts, "GET", self.uuid_s)
        header_tmp = self.header.copy()
        header_tmp.pop("Content-Type")
        # print(url)
        # print(self.header)
        while True:
            try:
                return requests.get(url=url, headers=header_tmp, verify=False, proxies=proxies)
            except Exception:
                time.sleep(10)

    @staticmethod
    def encrypt(url, ts, method, uuid_ss):
        """
        :param url: 完整链接：https://picaapi.picacomic.com/auth/sign-in
        :param ts: 要和head里面的time一致, int(time.time())
        :param method: http请求方式: "GET" or "POST"
        :param uuid_ss: str, len(uuid)==32
        :return: header["signature"]
        """
        raw = url.replace("https://picaapi.picacomic.com/", "") + \
            str(ts) + uuid_ss + method + api_key
        raw = raw.lower()
        hc = hmac.new(secret_key.encode(), digestmod=hashlib.sha256)
        hc.update(raw.encode())
        return hc.hexdigest()

    def login(self):
        api = "auth/sign-in"
        url = global_url + api
        send = {"email": self.account, "password": self.password}
        __a = self.post(url=url, data=json.dumps(send)).text
        self.header["authorization"] = json.loads(__a)["data"]["token"]
        return self.header["authorization"]

    def categories(self):
        api = "categories"
        url = global_url + api
        return self.get(url)

    def block(self, __page, __word):
        """
        bl:妹妹系,性轉換,
        """
        api = "comics?page={0}&c={1}&s=ua".format(__page, parse.quote(__word))
        url = global_url + api
        return self.get(url)

    def searchs(self, __page, __word):
        url = global_url + \
            "comics/search?page={0}&q={1}".format(__page, parse.quote(__word))
        return self.get(url)

    def tags(self, __page, __word):
        url = global_url + \
            "comics?page={}&t={}".format(__page, parse.quote(__word))
        return self.get(url)

    def comics(self, __id, __name):
        # print(__name, time.ctime())
        api = global_url + "comics/{0}/eps?".format(__id) + "page={0}"
        _return = []
        for _ in range(1, 2):  # __pages + 1
            url = api.format(_)
            __res = self.get(url).json()["data"]["eps"]["docs"]
            for __ in __res:
                _name = re.sub("[|:/*\\s!?]*", "", __name + __["title"])
                # print(_name)
                _return.append({"name": _name, "fid": __id,
                                "order": __["order"], "id": __["_id"]})
        return _return

    def comic(self, __order, __id, _name):
        api = global_url + \
            'comics/{0}/order/{1}/pages'.format(__id, __order) + '?page={0}'
        url = api.format(1)
        __pages = self.get(url).json()["data"]["pages"]["pages"]
        try:
            os.makedirs("/home/eclipse/Pictures/picacg/{}".format(_name))
        except FileExistsError:
            pass
        for _ in range(1, __pages + 1):  # __pages + 1
            url = api.format(_)
            __res = self.get(url).json()["data"]["pages"]["docs"]

            for __ in __res:
                _tmp = __["media"]
                file_name = "/home/eclipse/Pictures/picacg/{}/{}".format(
                    _name, _tmp["originalName"])
                if os.path.exists(file_name) and os.path.getsize(file_name) != 0:
                    continue
                with open(file_name, "wb") as out:
                    _pic = self.get_picture(
                        "https://storage1.picacomic.com/static/" + _tmp["path"])
                    out.write(_pic)
        print(_name, time.ctime(), "done")
        return _name, time.ctime(), "done"

    def get_picture(self, url):
        while True:
            try:
                __a = self.get(url)
                if __a.status_code != 200:
                    continue
                break
            except requests.exceptions.ConnectionError:
                time.sleep(8)
        return __a.content

    def search(self, __word):
        api = global_url + \
            "comics/search?page={0}" + "&q={0}".format(parse.quote(__word))
        _return = []
        for _ in range(1, 3):  # __pages + 1
            url = api.format(_)
            __res = self.get(url).json()["data"]["comics"]["docs"]
            for __ in __res:
                if __["likesCount"] < 200:
                    continue
                if __["pagesCount"] / __["epsCount"] > 60 or __["epsCount"] > 10:
                    continue
                _return.append({"name": __["title"], "id": __["_id"]})
        return _return


if __name__ == "__main__":
    spider = Pica("ubuntulinux", "qwerty123")
    spider.login()
    ret = spider.block(1, 'Cosplay').content.decode()
    content = json.loads(ret)['data']['comics']['docs']
    for item in content:
        _id = item['_id']
        name = item['title']
        order = "1"
        spider.comic(order, _id, name)
