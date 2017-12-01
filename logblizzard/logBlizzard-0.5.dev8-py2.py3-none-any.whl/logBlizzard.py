"""
Author: Kris Swanson, kriswans@cisco.com

Tested with Python 3.6.1 on WIN10
"""


import socket
import struct
import time
import sys
import multiprocessing
import datetime
import glob
import json
from crypto import Crypto as cryp
from syslog import syslog
from nodemanager import NodeManager as nm
from localsearch import SearchLocal as sl



def logMonitor_Rx(password,params):
    """
    fn listens for messages and updates message log.
    """
    print("Starting Rx Process...\n")

    with open('network_cfg.json','r') as nwc:
        nw=json.load(nwc)

    LOGMSG_GRP = nw['LOGMSG_GRP']
    LOGMSG_PORT = nw['LOGMSG_PORT']
    SCH_GRP = nw['SCH_GRP']
    SCH_PORT = nw['SCH_PORT']


    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', LOGMSG_PORT))  # use LOGMSG_GRP instead of '' to listen only
                                 # to LOGMSG_GRP, not all groups on LOGMSG_PORT
    mreq = struct.pack("4sl", socket.inet_aton(LOGMSG_GRP), socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    filter_tag='%(node_num)s:%(role)s:%(cluster_id)s:%(localnode)s' % params
    print(filter_tag)

    ts = 0
    i=0
    dcdmsg=''
    search_list=[]
    quick_search_tag='LogQSearch:::'
    write_mem_tag='!WRITECACHE!'
    zero_disk_tag='!DELETEDISKCACHE!'
    zero_mem_tag='!DELETEMEMCACHE!'

    ts_start=time.time()
    log_name='msglog_'+str(ts_start)+'.json'
    schjob=[]
    while True:

        try:
            search=False
            rx_msg=sock.recv(2048)
            dcdmsg=rx_msg.decode("utf-8")
            dcdmsg=bytes(dcdmsg,'ascii')
            dcdmsg=cryp.DecryptMsg(dcdmsg,password)

            if quick_search_tag in dcdmsg:
                search=True
                print('quick search!')
                sl.searchMem(search_list,dcdmsg,password,'off')


            if filter_tag not in dcdmsg and search==False:

              jlm=json.loads(dcdmsg)
              search_list.append({"source_time":jlm["source_time"],'sending_node':jlm['sending_node'],'sending_hostname':jlm['sending_hostname'],"cluster":params["cluster_id"],'orig_message':jlm['orig_message'],'orig_addr':jlm['orig_addr']})
              i+=1
              if i % 10 == 0:
                  with open ('msglog_temp.json','w') as log:
                      json.dump(search_list,log)
                      continue
              if i % 105 == 0:
                  ts_start=time.time()
                  log_name='msglog_'+str(ts_start)+'.json'
                  with open (log_name,'w') as log:
                      json.dump(search_list,log)
                  search_list=[]
                  continue

            else:
              continue

        except:
            print('Rx Process Exception')
            pass





def logMonitor_Tx(msg, params,password, nw):


    LOGMSG_GRP = nw['LOGMSG_GRP']
    LOGMSG_PORT = nw['LOGMSG_PORT']

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)
    print("Starting Tx process...\n")

    localnode=params['localnode']
    role=params['role']
    node=params['localnode']
    cluster=params['cluster_id']

    hostname=(socket.gethostname())

    jobs=[]

    z = multiprocessing.Process(target=nm.infHBeat,args=(params,nw))
    jobs.append(z)
    z.daemon = True
    z.start()

    n = multiprocessing.Process(target=nm.messageTagGen,args=(nw,))
    jobs.append(n)
    n.daemon = True
    n.start()

    if role == 'RxTx':

        p = multiprocessing.Process(target=logMonitor_Rx,args=(password,params,))
        jobs.append(p)
        p.daemon = True
        p.start()

        ds =multiprocessing.Process(target=sl.deepSearch)
        jobs.append(ds)
        ds.daemon = True
        ds.start()

    q = multiprocessing.Process(target=syslog)
    jobs.append(q)
    q.daemon = True
    q.start()

    lenfr=0
    send_throttle=2
    lfr=[0,0]
    while True:
        lfr[0]=lfr[1]
        if max(lfr) > 100:
            with open ('syslog.log','w') as f:
                f.close()
            lfr=[0,0]
        time.sleep(send_throttle)

        try:
            with open ('droplist.json','r') as dlj:
                drop_tag=json.load(dlj)
                drop_tag=str(drop_tag)
        except :
            print('possible JSONDecodeError')
            drop_tag='[]'
            pass


        while True:

            with open('syslog.log','r') as f:
                fr=f.readlines()
            lfr[1]=len(fr)
            if lfr[1] > lfr[0]:
                msg=''
                for i in fr[lfr[0]:lfr[1]]:
                    msg=i.rstrip()
                    parse_msg=json.loads(msg)
                    ts = time.time()
                    msg={'source_time':ts,'sending_node':localnode,'sending_hostname':hostname,'orig_message':parse_msg['log_message'],'orig_addr':parse_msg['orig_addr'],'drop_tag':drop_tag}
                    msg=json.dumps(msg)
                    msg=bytes(msg, "ascii")
                    msg=cryp.EncryptMsg(msg,password)
                try:
                    sock.sendto(msg, (LOGMSG_GRP, LOGMSG_PORT))
                except OSError:
                    msg = ("Attempting to send %s log messages from overran Tx buffer" % str(len(fr)))
                    msg=localnode+'@'+hostname+"# "+'"'+msg+'"'+drop_tag
                    msg=bytes(msg, "ascii")
                    msg=cryp.EncryptMsg(msg,password)
                    sock.sendto(msg, (LOGMSG_GRP, LOGMSG_PORT))
                    pass

            if lfr[0] == lfr[1]:
                pass

            else:
                pass
            break


    sys.exit()
"""
main fn to pull user info and kick off logMonitor_Tx fn. logMonitor_Tx kicks off heartbeat and Rx functions.
"""

def main():

    params, nw =nm.localParams()

    with open('pwf','r') as p:
        password=p.read()
    password=password.rstrip()

    jobs = []
    msg=None

    r = multiprocessing.Process(target=logMonitor_Tx(msg,params,password,nw))
    jobs.append(r)
    r.start()


if __name__ == '__main__':
    main()
