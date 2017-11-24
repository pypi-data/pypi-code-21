
import requests
import json

class CookieManager:
    def __init__(self, cookies=None,path=None, domain=None, ):
        self.path = path
        if not cookies or isinstance(cookies, list):
            self.cookies=cookies
        elif isinstance(cookies, requests.cookies.RequestsCookieJar):
            self.cookies=self._requests_to_lis(cookies)
        elif isinstance(cookies, str):
            self.cookies=self._str_to_list(cookies, domain=domain)
        if self.cookies and self.path:
            self.dump_cookies()
        elif self.path:
            self.load_cookies()

    def to_requests(self):
        if not self.cookies:
            return None
        return self.selenium_to_requests(self.cookies)

    def to_selenium(self):
        if not self.cookies:
            return None
        return self.cookies

    def dump_cookies(self, path=None):
        path = self.path if self.path else path
        if not path:
            print('no path')
        with open(path,'w')as f:
            json.dump(self.cookies,f)

    def load_cookies(self, path=None):
        path = self.path if self.path else path
        if not path:
            print('no path')
        try:
            with open(path,'r')as f:
                self.cookies = json.load(f)
        except FileNotFoundError:
            pass

    def _str_to_list(self, cookie_str : str, domain: str):
        cookie_lis = []
        for one_ck in cookie_str.split(';'):
            co_dic = {'domain':domain} if domain else {}
            cook = one_ck.split('=')
            co_dic['name'] = cook[0].strip()
            co_dic['value'] = cook[1].strip()
            cookie_lis.append(co_dic)
        self.cookies=cookie_lis
        return cookie_lis

    def _requests_to_lis(self, cookies : object):
        cookie_lis = []
        for each in cookies:
            cookie_lis.append(each.__dict__)
        self.cookies=cookie_lis
        return cookie_lis

    def str_to_selenium(self, cookie_str : str, domain=None ):
        ''' browser.add_cookie(each) '''
        return self._str_to_list(cookie_str, domain=domain)

    def str_to_requests(self, cookie_str : str, domain=None ):
        ''' s.cookie.update(jar) '''
        jar = requests.cookies.RequestsCookieJar()
        for cookie in self._str_to_list(cookie_str, domain=domain):
            jar.set(cookie['name'], cookie['value'], domain=cookie.get('domain'))
        return jar

    def selenium_to_requests(self, cookies : list):
        '''s.cookie.update(jar)'''
        self.cookies=cookies
        jar = requests.cookies.RequestsCookieJar()
        for cookie in cookies:
            jar.set(cookie['name'], cookie['value'], domain=cookie.get('domain'),path=cookie.get('path'))
        return jar

    def requests_to_selenium(self, cookies : object):
        ''' browser.add_cookie(each) '''
        return self._requests_to_lis(cookies)

if __name__ == '__main__':
    rck = "acw_tc=AQAAAMl0jwWXVgwAkVEQcNYwfiOHTU7Z; gr_user_id=789093c2-6f47-44c7-96f0-1000976b1617; Hm_lvt_9d483e9e48ba1faa0dfceaf6333de846=1506502469; Hm_lpvt_9d483e9e48ba1faa0dfceaf6333de846=1508590237; _uab_collina=150889608020375247468069; _umdata=70CF403AFFD707DF927BBBE5EAC67F5E32B0AAD93C1C382A68E9BA25AA2B8D45EE08BD8218C4A89DCD43AD3E795C914CA803ADC524B3172BB746CA7ACFF8D4B2; acw_sc=59f17e409215724b5f7f37a5860c8b6747701b2a; identity_id=4160030387732514; identity=326737833%40qq.com; remember_code=1uiHRC55ou; unique_token=292300; _ga=GA1.2.176552989.1505963948; _gid=GA1.2.171718625.1511441720; Hm_lvt_1c587ad486cdb6b962e94fc2002edf89=1511441720; Hm_lpvt_1c587ad486cdb6b962e94fc2002edf89=1511444216; session=00a767387291af90227da7aec74a97bbe4c1f90f; gr_session_id_eee5a46c52000d401f969f4535bdaa78=d386b5cf-100b-443d-9d5d-f473f9c96e5f"
    ch = CookieManager(rck,'test')
    # ret = ch.str_to_selenium(rck,'.itjuzi.com')
    print(ch.cookies)
