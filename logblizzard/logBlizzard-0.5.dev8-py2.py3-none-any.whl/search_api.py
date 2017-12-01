

from clustersearch import ClusterSearch as CS
import time
import json
from crypto import Crypto as cryp
import socket
import struct

def apiReq(search_list_cl=['PIM','DR'], search_oper_cl='AND',search_type_cl='D',search_list_ca=[''],search_oper_ca='OR'):


    with open('network_cfg.json','r') as nwc:
        nw=json.load(nwc)
    API_GRP = nw['API_GRP']
    API_PORT = nw['API_PORT']

    with open('pwf','r') as p:
        password=p.read()
    password=password.rstrip()


    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', API_PORT))
    mreq = struct.pack("4sl", socket.inet_aton(API_GRP), socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    ts=time.time()
    api_file="APIREQ"+str(ts)+".json"

    CS.searchSend('api',None,None,'ZD',None)
    time.sleep(.2)
    CS.searchSend('api',None,None,'ZM',None)
    time.sleep(.2)
    CS.searchSend('api',search_list_cl,search_oper_cl,search_type_cl,None)
    time.sleep(.2)

    dcdmsg=''
    responses=1
    i=0
    search_len_list=[]

    if search_type_cl == "D":
        while i < responses:

            rx_msg=sock.recv(2048)
            dcdmsg=rx_msg.decode("utf-8")
            dcdmsg=bytes(dcdmsg,'ascii')
            dcdmsg=cryp.DecryptMsg(dcdmsg,password)
            js_dcdmsg=json.loads(dcdmsg)
            responses=js_dcdmsg['node_len']
            search_len=js_dcdmsg['search_len']
            search_len_list.append(search_len)
            search_max=max(search_len_list)
            i+=1
            print(str(responses)+" TxRx nodes to respond.")
            print(str(i) + " TxRx nodes have responded.")

        print(str(search_max)+" is the largest response from a single node.")
        if search_max > 3000:
            return {'Error':'Search Results exceed 3000 from a single logging node, please narrow search criteria.'}
        response_size_timer=(.01+.001*responses)*search_max
        print("\nWait time for responses is: "+ str(response_size_timer)+"\n")
        time.sleep(response_size_timer)
    else:
        time.sleep(.5)

    CS.searchSend('api',None,None,'W',None)
    time.sleep(.2)
    CS.searchSend('api',search_list_ca,search_oper_ca,'C',api_file)
    time.sleep(1.5)

    with open (api_file,'r') as f:
        jsr=json.load(f)

    return jsr


if __name__=='__main__':
    jsr=apiReq()
    print(len(jsr))
    print(type(jsr))
