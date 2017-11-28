import zoo_handler

class keyholder:
    host = ""
    port = 0
    type = ""
    namespace = ""
    conn = None
    state = ""
    def __init__(self,namespace, type="zookeeper",host="127.0.0.1",port=2181):
        self.host = host
        self.port = port
        self.type = type
        self.namespace = namespace
        if (self.type == "zookeeper"):
            self.conn = zoo_handler.zoo_handler(self.host,self.port)

    def ensure_path(self,path):
        self.conn.ensure_path(path)

    def create(self,path):
        self.conn.create(path)

    def ensure_path(self,path):
        self.conn.ensure_path(path)

    def create(self,path):
        self.conn.create(path)

    def exists(self,node):
        return self.conn.exists(node)

    def get_node_data(self,node):
        return self.conn.get_node_data(node)

    def get_children(self,path):
        return self.conn.get_children(path)

    def set_node_data(self,node,data):
        self.conn.set_node_data(node,data)

    def delete_node(self,node,isrecursive):
        self.conn.delete(node,recursive=isrecursive)

