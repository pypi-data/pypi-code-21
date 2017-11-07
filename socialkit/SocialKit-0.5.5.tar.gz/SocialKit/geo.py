import sys
from qlib.net import to
from qlib.log import show
import json
import hashlib

def get_ip_information(ip, key):
    url='http://api.map.baidu.com'
    req = '/highacciploc/v1?qcip='+ip+'&qterm=pc&ak=' + key +'&coord=bd09ll&extensions=3'
    poiss=''
    h = hashlib.md5(req.encode('utf8')).hexdigest()
    request = to(url + req + '&sn=' + h)
    
    page = request.json()
    
    if("content" in page):
        content=page["content"]
        address_component=content["address_component"]
        formatted_address=content["formatted_address"]
        show("geo :")
        show(address_component["country"])
        show(formatted_address)
        if ("pois" in content):
            show("poi：")
            pois = content["pois"]
            for index in range(len(pois)):
                pois_name = pois[index]["name"]
                pois_address = pois[index]["address"]
                show(pois_name, pois_address)
    else:
        show('failed ')
    return page

if __name__ == '__main__':
    get_ip_information('183.55.116.95')