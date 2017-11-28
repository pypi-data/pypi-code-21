from kazoo.client import KazooClient
from kazoo.client import KazooState
import logging

class zoo_handler:
    zk = None
    host = ""
    port = 0
    logging = None
    state = ""

    def __init__(self,host,port):
        def conn_listener(state):
            if (state == KazooState.LOST):
                self.state = "LOST"
            elif state == KazooState.SUSPENDED:
                self.state = "SUSPENDED"
            else:
                self.state = "SUSPENDED"
        self.host = host
        self.port = port
        self.zk = KazooClient(host+":"+str(port))
        self.zk.start()
        self.logging = logging.basicConfig()
        self.zk.add_listener(conn_listener)

    def ensure_path(self,path):
        self.zk.ensure_path(path)

    def create(self,path):
        self.zk.create(path)

    def exists(self,node):
        return self.zk.exists(node)

    def get_node_data(self,node):
        return self.zk.get(node)

    def get_children(self,path):
        return self.zk.get_children(path)

    def set_node_data(self,node,data):
        self.zk.set(node,data)

    def delete_node(self,node,isrecursive):
        self.zk.delete(node,recursive=isrecursive)