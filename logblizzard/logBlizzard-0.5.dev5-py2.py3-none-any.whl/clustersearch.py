import socket
import json
from crypto import Crypto as cryp
import multiprocessing
import struct
import pprint
import time

class ClusterSearch:
    def __init__(self,msg,password):
        self.msg=msg
        self.password=password


    def searchSend(input_type='user', search_input=[], search_oper='AND', search_type='Q',api_file=None):
        with open('pwf','r') as p:
            password=p.read()
        password=password.rstrip()
        with open('network_cfg.json','r') as nwc:
            nw=json.load(nwc)

        LOGMSG_GRP = nw['LOGMSG_GRP']
        LOGMSG_PORT = nw['LOGMSG_PORT']
        SCH_GRP = nw['SCH_GRP']
        SCH_PORT = nw['SCH_PORT']
        DEEP_SCH_GRP = nw['DEEP_SCH_GRP']
        DEEP_SCH_PORT = nw['DEEP_SCH_PORT']
        '''
        may want to break out cache search to help with scaling
        SEARCH_CACHE_GRP='232.1.1.12'
        SEARCH_CACHE_PORT = 5012
        '''
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)
        if input_type == 'user':
            in_field=''
            search_input=[]
            while '!!!' not in in_field:
                in_field=str(input("Please enter search string, enter !!! to end: "))
                search_input.append(in_field)
            search_input.pop()
            print(search_input)
            search_oper=str(input("Enter your search operator as AND , OR ->  "))
            search_type=str(input("Enter search type Q:Quick, D:Deep:, C:Cached or ZM/ZD:Zero-Mem/Disk-Cache,W:Write-Cache ->  "))

        if search_type == 'Q':
            search_tag='LogQSearch:::'
            msg={'search_tag':search_tag,'search_var':search_input,'search_field':'orig_message','search_oper':search_oper}
            msg=json.dumps(msg)
            msg=bytes(msg, "ascii")
            msg=cryp.EncryptMsg(msg,password)
            sock.sendto(msg, (LOGMSG_GRP, LOGMSG_PORT))

        if search_type == 'D':
            search_tag='LogDSearch:::'
            msg={'search_tag':search_tag,'search_var':search_input,'search_field':'orig_message','search_oper':search_oper}
            msg=json.dumps(msg)
            msg=bytes(msg, "ascii")
            msg=cryp.EncryptMsg(msg,password)
            sock.sendto(msg, (DEEP_SCH_GRP, DEEP_SCH_PORT))

        if search_type == 'W':
            search_tag='!WRITECACHE!'
            msg={'search_tag':search_tag}
            msg=json.dumps(msg)
            msg=bytes(msg, "ascii")
            msg=cryp.EncryptMsg(msg,password)
            sock.sendto(msg, (SCH_GRP, SCH_PORT))

        if search_type =='C':
            search_tag='!SEARCHCACHE!'
            msg={'search_tag':search_tag,'search_var':search_input,'search_field':'orig_message','search_oper':search_oper,'api_file':api_file}
            msg=json.dumps(msg)
            msg=bytes(msg, "ascii")
            msg=cryp.EncryptMsg(msg,password)
            sock.sendto(msg, (SCH_GRP, SCH_PORT))

        if search_type == 'ZD':
            search_tag='!DELETEDISKCACHE!'
            msg={'search_tag':search_tag}
            msg=json.dumps(msg)
            msg=bytes(msg, "ascii")
            msg=cryp.EncryptMsg(msg,password)
            sock.sendto(msg, (SCH_GRP, SCH_PORT))

        if search_type == 'ZM':
            search_tag='!DELETEMEMCACHE!'
            msg={'search_tag':search_tag}
            msg=json.dumps(msg)
            msg=bytes(msg, "ascii")
            msg=cryp.EncryptMsg(msg,password)
            sock.sendto(msg, (SCH_GRP, SCH_PORT))


    def searchRx(output_type='console'):

            print("starting searchRx")
            with open('pwf','r') as p:
                password=p.read()
            password=password.rstrip()

            with open('network_cfg.json','r') as nwc:
                nw=json.load(nwc)

            SCH_GRP = nw['SCH_GRP']
            SCH_PORT = nw['SCH_PORT']
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(('', SCH_PORT))  # use LOGMSG_GRP instead of '' to listen only
                                         # to LOGMSG_GRP, not all groups on LOGMSG_PORT
            mreq = struct.pack("4sl", socket.inet_aton(SCH_GRP), socket.INADDR_ANY)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
            print("\n\nListening for search results:\n")

            dedup_list=[]
            dedup_set=set()
            output_list=[]
            cache_message_list=[]

            while True:

                search=False
                rx_msg=sock.recv(100000)
                dcdmsg=rx_msg.decode("utf-8")
                dcdmsg=bytes(dcdmsg,'ascii')
                dcdmsg=cryp.DecryptMsg(dcdmsg,password)

                if "!WRITECACHE!" in dcdmsg:
                    cache_message_list=[json.dumps(i) for i in cache_message_list]
                    cache_message_list.sort()
                    cache_message_list=[json.loads(i) for i in cache_message_list]
                    with open('search_cache.json','w') as sc:
                        json.dump(cache_message_list,sc)
                    dcdmsg=''

                if '!DELETEDISKCACHE!' in dcdmsg:
                    with open('search_cache.json','w') as f:
                        f.close()
                    dcdmsg=''

                if '!DELETEMEMCACHE!' in dcdmsg:
                    dedup_list=[]
                    dedup_set=set()
                    output_list=[]
                    cache_message_list=[]
                    dcdmsg=''

                if '!SEARCHCACHE!' in dcdmsg:

                    js_dcdmsg=json.loads(dcdmsg)
                    so=js_dcdmsg['search_oper']
                    sv=js_dcdmsg['search_var']
                    sf=js_dcdmsg['search_field']
                    af=js_dcdmsg['api_file']
                    search_result=[]

                    with open('search_cache.json','r') as f:
                        jsl=json.load(f)

                    if so == 'OR':
                        search_result=[j for j in jsl if any(x in j[sf] for x in sv)]

                    if so == 'AND':
                        search_result=[j for j in jsl if all(x in j[sf] for x in sv)]

                    if so == None:
                        pass

                    else:
                        pass


                    stamp=str(time.time())
                    result_filename=str(sv)+str(so)+stamp+".json"

                    result_filename=result_filename.replace("/","-")
                    result_filename=result_filename.replace("?","-")
                    result_filename=result_filename.replace(":","-")
                    result_filename=result_filename.replace("*","-")
                    result_filename=result_filename.replace(">","-")
                    result_filename=result_filename.replace("<","-")
                    result_filename=result_filename.replace("|","-")
                    result_filename=result_filename.replace("\\","-")
                    result_filename=result_filename.replace(" ","-")

                    if af == None:
                        with open(result_filename,'w') as rf:
                            json.dump(search_result,rf)

                    if af != None:
                        with open(af,'w') as f:
                            json.dump(search_result,f)

                    time_addr_list=[{i['source_time']:i['orig_addr']} for i in search_result]
                    len_hits=len(time_addr_list)
                    print("Result total occurences: "+str(len_hits)+"\n")

                    dcdmsg=''



                else:

                    if dcdmsg != '':
                        dcdmsg=json.loads(dcdmsg)
                        for i in dcdmsg:
                            dedup_list.append(i)
                            len_set_before=len(dedup_set)
                            jd=json.dumps(i) ## b/c a dictionary is an unhashable type inside if a set.
                            dedup_set.add(jd)
                            len_set_after=len(dedup_set)
                            if len_set_after > len_set_before:
                                dedup_msg=dedup_list[-1]
                                #dcdmsg=json.loads(dcdmsg)
                                cache_message_list.append(dedup_msg)
                                #pprint.pprint(dedup_msg,None,1,80)
                    else:
                        pass



if __name__=='__main__':
    ClusterSearch.searchRx()
