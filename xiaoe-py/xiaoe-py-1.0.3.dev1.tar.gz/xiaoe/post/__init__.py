import requests
import json
import time
import hashlib


class Poster(object):
    base_url = 'https://api.xiaoe-tech.com/open'

    def __init__(self, appid, secret, version='1.0'):
        """
        :param appid: your appid
        :param secret: your secret
        :return:
        """
        self.appid = appid
        self.secret = secret
        self.version = version

    def format(self, data):
        """
        :param data: 请求体字典
        {
            "app_id": "xxxxxxx",
            "timestamp": "1511247678",
            "use_type": "0",
            "data": {
                "phone": "xxxxxxx",
                ...
            }
        }
        :return: key1=value1&key2=value2...&app_secret=self.secret
        """
        r = []
        for k, v in sorted(data.items(), key=lambda item: item[0]):
            if k == 'data':
                r.append(k + '=' + json.dumps(v, separators=(',', ':'), ensure_ascii=False))
            else:
                r.append(k + '=' + str(v))
        r.append('app_secret=' + self.secret)
        return '&'.join(r)

    @staticmethod
    def sign(s):
        """
        :param s: key1=value1&key2=value2...&app_secret=self.secret
        :return: 小写 md5
        """
        m = hashlib.md5()
        m.update(s.encode('utf-8'))
        sign = m.hexdigest().lower()
        return sign

    def post(self, path, data):
        url = '{}{}{}'.format(self.base_url, path, self.version)
        ct = str(int(time.time()))
        body = {
            "app_id": self.appid,
            "timestamp": ct,
            "use_type": "0",
            "data": data,
        }

        # create 签名
        format_s = self.format(body)
        sign = self.sign(format_s)

        # sign 更新到 body
        body.update({
            'sign': sign,
        })
        r = requests.post(url=url, json=body)
        # print(r, json.dumps(r.json(), ensure_ascii=False, indent=4))
        return r.json()
