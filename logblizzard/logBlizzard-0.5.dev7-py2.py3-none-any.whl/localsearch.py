import multiprocessing
import json
import socket
from crypto import Crypto as cryp
import os
import glob
import struct
import time
import datetime

class SearchLocal:
    '''Class of functions to search in log fields for both logs kept in memory and
    nvdisk andd then return results to SCH_GRP'''


    def __init__(self,dcdmsg,password):
        self.dcdmsg=dcdmsg
        self.password=password

    def deepSearch():
        print("Starting Deep Search Daemon")
        with open('network_cfg.json','r') as nwc:
            nw=json.load(nwc)

        DEEP_SCH_GRP = nw['DEEP_SCH_GRP']
        DEEP_SCH_PORT = nw['DEEP_SCH_PORT']
        with open('pwf','r') as p:
            password=p.read()
        password=password.rstrip()
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('', DEEP_SCH_PORT))  # use MCAST_GRP instead of '' to listen only
                                     # to MCAST_GRP, not all groups on MCAST_PORT
        mreq = struct.pack("4sl", socket.inet_aton(DEEP_SCH_GRP), socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        deep_search_tag='LogDSearch:::'
        while True:

            search=False
            rx_msg=sock.recv(2048)
            dcdmsg=rx_msg.decode("utf-8")
            dcdmsg=bytes(dcdmsg,'ascii')
            dcdmsg=cryp.DecryptMsg(dcdmsg,password)
            if deep_search_tag in dcdmsg:
                search=True
                print('deep search!')
                SearchLocal.searchDisk(dcdmsg,password,'off')
            else:
                continue


    def searchMem(search_list,dcdmsg,password,search_term_debug='off'):
        with open('network_cfg.json','r') as nwc:
            nw=json.load(nwc)

        SCH_GRP = nw['SCH_GRP']
        SCH_PORT = nw['SCH_PORT']

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)
        js_dcdmsg=json.loads(dcdmsg)
        so=js_dcdmsg['search_oper']
        sv=js_dcdmsg['search_var']
        sf=js_dcdmsg['search_field']
        search_result=[]


        if so == 'OR':
            search_result=[j for j in search_list if any(x in j[sf] for x in sv)]


        if so == 'AND':
            search_result=[j for j in search_list if all(x in j[sf] for x in sv)]

        else:
            print("Using 'OR' operator")
            search_result=[j for j in search_list if any(x in j[sf] for x in sv)]


        if search_term_debug == 'on':
            print(so)
            print('is the search operator')
            print(sv)
            print('is search var\n')
            print(sf)
            print('is search field\n')
            print(search_result)
            print('is search result\n\n')
            print(len(search_result))
            print('is the number of search results###\n\n')
        '''need to throttle responses using loop to limit msg size'''

        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        print(st+' is START time for sending memory search responses')
        i=0
        send_chunk=[]
        try:
            if search_result is not []:
              for k in search_result:
                  send_chunk.append(k)
                  i+=1
                  if i % 40 == 0:
                      js_search_result=json.dumps(send_chunk)
                      js_search_result=bytes(js_search_result, "ascii")
                      msg=cryp.EncryptMsg(js_search_result,password)
                      sock.sendto(msg, (SCH_GRP, SCH_PORT))
                      send_chunk=[]
                      time.sleep(.2)
              if send_chunk != []:
                  js_search_result=json.dumps(send_chunk)
                  js_search_result=bytes(js_search_result, "ascii")
                  msg=cryp.EncryptMsg(js_search_result,password)
                  sock.sendto(msg, (SCH_GRP, SCH_PORT))

            else:
                pass

            ts = time.time()
            st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
            print(st+' is END time for sending memory search responses')

        except OSError:
          msg = ("Attempting to send %s log messages from overran Tx buffer" % str(len(js_search_result)))
          msg=localnode+'@'+hostname+"# "+'"'+msg+'"'+drop_tag
          msg=bytes(msg, "ascii")
          msg=cryp.EncryptMsg(msg,password)
          sock.sendto(msg, (SCH_GRP, SCH_PORT))
          pass
        return search_result

    def searchDisk(dcdmsg,password,search_term_debug='off',response_limit=3000):
        with open('network_cfg.json','r') as nwc:
            nw=json.load(nwc)

        SCH_GRP = nw['SCH_GRP']
        SCH_PORT = nw['SCH_PORT']
        API_GRP = nw['API_GRP']
        API_PORT = nw['API_PORT']

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)
        js_dcdmsg=json.loads(dcdmsg)
        so=js_dcdmsg['search_oper']
        sv=js_dcdmsg['search_var']
        sf=js_dcdmsg['search_field']
        with open ('localcfg.json','r') as lcf:
            lcfg=json.load(lcf)

        loglist=glob.glob('msglog*.json')
        fldlist=[]
        search_result=[]

        for i in loglist:
            with open(i,'r') as f:
                sch=json.load(f)
                for j in sch:
                    fldlist.append(j)

        if so == 'OR':
            search_result=[j for j in fldlist if any(x in j[sf] for x in sv)]


        if so == 'AND':
            search_result=[j for j in fldlist if all(x in j[sf] for x in sv)]

        else:
            print("Using 'OR' operator")
            search_result=[j for j in fldlist if any(x in j[sf] for x in sv)]

        if search_term_debug == 'on':
            print(so)
            print('is the search operator')
            print(sv)
            print('is search var\n')
            print(sf)
            print('is search field\n')
            print(search_result)
            print('is search result\n\n')
            print(len(search_result))
            print('is the number of search results###\n\n')
        '''need to throttle responses using loop to limit msg size'''
        with open('nodelist_previous.json','r') as np:
            npl=json.load(np)

        lnp=len(npl)
        lsr=len(search_result)
        response_size={'node_len':lnp,'search_len':lsr}
        js_response_size=json.dumps(response_size)
        js_response_size=bytes(js_response_size, "ascii")
        msg=cryp.EncryptMsg(js_response_size,password)
        time.sleep(1)
        sock.sendto(msg, (API_GRP, API_PORT))
        if lsr > response_limit:
            search_result=[{lcfg["localnode"]:lsr}]

        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        print(st+' is START time for sending deep search responses')
        i=0
        send_chunk=[]
        try:
            if search_result is not []:
              for k in search_result:
                  send_chunk.append(k)
                  i+=1
                  if i % 40 == 0:
                      js_search_result=json.dumps(send_chunk)
                      js_search_result=bytes(js_search_result, "ascii")
                      msg=cryp.EncryptMsg(js_search_result,password)
                      sock.sendto(msg, (SCH_GRP, SCH_PORT))
                      send_chunk=[]
                      time.sleep(.2)
              if send_chunk != []:
                  js_search_result=json.dumps(send_chunk)
                  js_search_result=bytes(js_search_result, "ascii")
                  msg=cryp.EncryptMsg(js_search_result,password)
                  sock.sendto(msg, (SCH_GRP, SCH_PORT))

            else:
                pass

            ts = time.time()
            st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
            print(st+' is END time for sending deep search responses')

        except OSError:
          msg = ("Attempting to send %s log messages from overran Tx buffer" % str(len(js_search_result)))
          pass
        return search_result
