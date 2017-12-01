
import time
import socket
import struct
import sys
import multiprocessing
import datetime
import json
import glob
import random

class NodeManager:

    def __init__(self,password):
        self.nodelist_current=nodelist_current
        self.rf=rf


    def localParams():
        with open ('localcfg.json','r') as lc:
            params=json.load(lc)

        params['node_num']=random.randint(1,999999)
        params['localnode']=socket.gethostname()

        with open ('localcfg.json','w') as lc:
            json.dump(params,lc)

        with open('network_cfg.json','r') as nwc:
            nw=json.load(nwc)
        return params, nw

    def infHBeat(params, nw , beat_time=2):
        ''' Generates an infinite heartbeat based on  localcfg.json
        parameters. Frequency is determined by beat_time.
        '''



        HB_GRP = nw['HB_GRP']
        HB_PORT = nw['HB_PORT']

        hostname=(socket.gethostname())

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)

        while True:
            nodeadv=("%(node_num)s:%(role)s:%(cluster_id)s:%(localnode)s") % params
            nodeadv=bytes(nodeadv, "ascii")
            sock.sendto(nodeadv, (HB_GRP, HB_PORT))
            time.sleep(beat_time)



    def nodeTable(nw, wait_factor=3, nodelist=[]):
        '''Builds a list on active nodes based upon the reciept of hearbeat.
        The time that it waits to build the list is based on 'wait_factor' and
        beat_time in infHBeat function.
        '''

        HB_GRP = nw['HB_GRP']
        HB_PORT = nw['HB_PORT']
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('', HB_PORT))  # use HB_GRP instead of '' to listen only
                                     # to HB_GRP, not all groups on HB_PORT
        mreq = struct.pack("4sl", socket.inet_aton(HB_GRP), socket.INADDR_ANY)

        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        i=0
        nodelist=[]
        while i < (len(nodelist)+1)*wait_factor:
            list_node=sock.recv(10240)
            dcdnode=list_node.decode("utf-8")
            nodelist.append(dcdnode)
            nodelist=set(nodelist)
            #nodelist=["1:RxTx:1:system-1","2:RxTx:1:system-2","3:Tx:1:system-3","4:RxTx:1:system-4"] #keep for testing
            nodelist=[i for i in nodelist if 'RxTx' in i]
            nodelist.sort()
            i=i+1

        return nodelist

    def droplistGen(nodelist,rf=1):
        '''This creates a list of nodes that will be appended to each message sent.

        If an Rx node recieves a message packet where it's node number appears,
        it will log the packet but the packet will later be deleted during policing.
        Tx only nodes need to append tags, but cannot themselves be tagged to
        drop messages(Because they never receive them).
        '''

        if 'nodelist_previous.json' not in glob.glob('*'):
            with open('nodelist_previous.json','w') as npj:
                json.dump(nodelist,npj)
        if 'round_robin.json' not in glob.glob('*'):
            with open('round_robin.json','w') as rrj:
                json.dump(nodelist,rrj)
        with open ('nodelist_previous.json','r') as np:
            nodelist_previous=json.load(np)
        if nodelist == nodelist_previous:
            with open ('round_robin.json','r') as rr:
                drop_order=json.load(rr)

            rxnodes=rf+1
            if len(drop_order)>rxnodes:
                topop=drop_order[0]
                drop_order.pop(0)
                drop_order.append(topop)
            droplist=drop_order[rxnodes-1:-1]
            with open ('round_robin.json','w') as rr:
                json.dump(drop_order,rr)
            with open('droplist.json','w') as dl:
                json.dump(droplist,dl)
        if nodelist != nodelist_previous:
            with open('nodelist_previous.json','w') as np:
                json.dump(nodelist,np)
            with open ('round_robin.json','w') as rr:
                json.dump(nodelist,rr)
            droplist=[]
        return droplist

    def messageTagGen(nw):
        while True:
            nodelist=NodeManager.nodeTable(nw)
            droplist=NodeManager.droplistGen(nodelist)

    def messageTagGen_ret(nw):
            nodelist=NodeManager.nodeTable(nw)
            droplist=NodeManager.droplistGen(nodelist)
            return nodelist, droplist



if __name__=='__main__':
    '''Start infinite hearbeat '''
    jobs=[]
    params, nw=NodeManager.localParams()
    z = multiprocessing.Process(target=NodeManager.infHBeat, args=(params,nw,))
    jobs.append(z)
    z.daemon = True
    z.start()

    '''report current Rx nodes and drop list '''
    while True:
        nodelist, droplist = NodeManager.messageTagGen_ret(nw)
        print("The Current Message Drop List:\n")
        print(droplist)
        print("The Current Node List:\n")
        print(nodelist)
