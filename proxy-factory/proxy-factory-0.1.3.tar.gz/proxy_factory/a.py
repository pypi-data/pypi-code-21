def check(self, proxy):
    import requests
    print(requests.get("http://2017.ip138.com/ic.asp", proxies={"http": "http://%s"%proxy}).text)
    return True

