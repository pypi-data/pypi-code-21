#coding:utf-8

import random
import requests


def fake_get(url :str,headers :dict,UA_pool :list,proxy_pool :list,**kwargs):
    session = requests.Session()
    try:
        #print(111)
        res = session.get(url,headers=headers,**kwargs)
        return res
    except:
        try:
            if headers:
                headers.update({'User-Agent': random.choice(UA_pool)})
            else:
                headers = {'User-Agent': random.choice(UA_pool)}
            #print(222)
            res = session.get(url,headers=headers,**kwargs)
            return res
        except:
            if headers:
                headers.update({'User-Agent': random.choice(UA_pool)})
            else:
                headers = {'User-Agent': random.choice(UA_pool)}
            #print(333)
            res = session.get(url,headers=headers,proxies=random.choice(proxy_pool),**kwargs)
            return res
    finally:
        session.close()



def fake_post(url :str,headers :dict,UA_pool :list,proxy_pool :list,**kwargs):
    session = requests.Session()
    try:
        res = session.post(url,headers=headers,**kwargs)
        return res
    except:
        try:
            if headers:
                headers.update({'User-Agent': random.choice(UA_pool)})
            else:
                headers = {'User-Agent': random.choice(UA_pool)}
            res = session.post(url,headers=headers,**kwargs)
            return res
        except:
            if headers:
                headers.update({'User-Agent': random.choice(UA_pool)})
            else:
                headers = {'User-Agent': random.choice(UA_pool)}
            res = session.post(url,headers=headers,proxies=random.choice(proxy_pool),**kwargs)
            return res
    finally:
        session.close()

