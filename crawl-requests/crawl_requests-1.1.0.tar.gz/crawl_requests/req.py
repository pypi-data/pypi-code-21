#coding:utf-8

import random
import requests


def req_get(url :str,headers :dict,UA_pool :list,proxy_pool :list,**kwargs):
    session = requests.Session()
    try:
        res = session.get(url,headers=headers,**kwargs)
        return res
    except:
        try:
            if headers:
                headers.update({'User-Agent': random.choice(UA_pool)})
            else:
                headers = {'User-Agent': random.choice(UA_pool)}
            #print('--Add UA visit web:--')
            res = session.get(url,headers=headers,**kwargs)
            return res
        except:
            if headers:
                headers.update({'User-Agent': random.choice(UA_pool)})
            else:
                headers = {'User-Agent': random.choice(UA_pool)}
            #print('--Add UA and proxy visit web:--')
            res = session.get(url,headers=headers,proxies=random.choice(proxy_pool),**kwargs)
            return res
    finally:
        session.close()



def req_post(url :str,headers :dict,UA_pool :list,proxy_pool :list,**kwargs):
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
            # print('--Add UA visit web:--')
            res = session.post(url,headers=headers,**kwargs)
            return res
        except:
            if headers:
                headers.update({'User-Agent': random.choice(UA_pool)})
            else:
                headers = {'User-Agent': random.choice(UA_pool)}
            # print('--Add UA and proxy visit web:--')
            res = session.post(url,headers=headers,proxies=random.choice(proxy_pool),**kwargs)
            return res
    finally:
        session.close()

