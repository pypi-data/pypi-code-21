from kazoo.security import make_digest_acl
from kazoo.client import KazooClient
import json

class ZookeeperPlus(KazooClient):
    def __init__(self,zk_conn_info,username,passwd):
        self.username = username
        self.passwd = passwd
        self.zk_conn_info = zk_conn_info
        self.act = self.get_acl()
        super(ZookeeperPlus, self).__init__(hosts=self.zk_conn_info,auth_data=[('digest', self.get_digest_auth())])
        self.start()


    def get_digest_auth(self):
        result =  "%s:%s" % (self.username,self.passwd)
        return result

    def get_acl(self):
        return make_digest_acl(self.username,self.passwd, all=True)

    def delete_app_path(self,app_name,app_port,recursive=True):
        self.delete("/realms/" + app_name + '/' + str(app_port), recursive)
        self.delete("/applications/" + app_name + '/instances/' + str(app_port), recursive)

    def delete_app(self,app_name,app_port,recursive=True):
        self.delete("/realms/" + app_name, recursive)
        self.delete("/applications/" + app_name, recursive)

    def set_metadata(self,app_name,app_port,app_metadata={}):
        self.ensure_path('/applications/' + app_name + '/instances/' + str(app_port) + '/metadata',
                                (self.act,))
        self.set('/applications/' + app_name + '/instances/' + str(app_port) + '/metadata',
                        json.dumps(app_metadata).encode('utf-8'))

    def set_configuration(self,app_name,app_port,app_configuration={}):
        self.ensure_path('/applications/' + app_name + '/instances/' + str(app_port) + '/configuration',
                                (self.act,))
        self.set('/applications/' + app_name + '/instances/' + str(app_port) + '/configuration',
                        json.dumps(app_configuration).encode('utf-8'))

    def set_information(self,app_name,app_port,app_infomation={}):
        self.ensure_path('/applications/' + app_name + '/instances/' + str(app_port) + '/information',
                                (self.act,))
        self.set('/applications/' + app_name + '/instances/' + str(app_port) + '/information',
                        json.dumps(app_infomation).encode('utf-8'))

    def set_dependencies(self,app_name,app_port,app_dependencies={}):
        self.ensure_path('/applications/' + app_name + '/instances/' + str(app_port) + '/dependencies',
                                (self.act,))
        self.set('/applications/' + app_name + '/instances/' + str(app_port) + '/dependencies',
                        json.dumps(app_dependencies).encode('utf-8'))

    def set_runtime_data(self, app_name, app_port, app_runtime_data={}):
        self.ensure_path('/applications/' + app_name + '/instances/' + str(app_port) + '/runtime-data',
                                (self.act,))
        self.set('/applications/' + app_name + '/instances/' + str(app_port) + '/runtime-data',
                        json.dumps(app_runtime_data).encode('utf-8'))

    def set_realms(self,app_name,app_port,app_infomation={}):
        self.ensure_path('/realms/' + app_name + '/' + str(app_port),(self.act,))
        self.set('/realms/' + app_name + '/' + str(app_port),
                        json.dumps(app_infomation).encode('utf-8'))

    def create_app_infomation(self,app_name,app_version,app_host,app_port,sweetpy_version='1.0',layer='Business',state='Starting'):
        #applications:
        # {
        #     "appId": "8000",
        #     "appName": "python-sweet",
        #     "appVersion": "1.0",
        #     "appHost": "10.200.144.127",
        #     "appPort": 8000,
        #     "appContextPath": "/",
        #     "sweetpyFrameworkVersion": "2.2.3-SNAPSHOT",
        #     "layer": "Business",
        #     "state": "Starting"
        # }
        #realms:
        # {
        #     "appId": "8000",
        #     "appName": "python-sweet",
        #     "appVersion": "1.0",
        #     "appHost": "10.200.144.127",
        #     "appPort": 8000,
        #     "appContextPath": "/",
        #     "sweetpyFrameworkVersion": "2.2.3-SNAPSHOT",
        #     "layer": "Business",
        #     "state": "Running"
        # }
        result = {
                  "appId": str(app_port),
                  "appName": app_name,
                  "appVersion": app_version,
                  "appHost": app_host,
                  "appPort": app_port,
                  "appContextPath": "/",
                  "SweetpyFrameworkVersion": sweetpy_version,
                  "layer": layer,
                  "state": state
                }
        return result

    def create_runtime_data(self,load_balance_weight=50,multi_version_force_match=False):
        # {
        #     "loadBalanceWeight": 50,
        #     "multiVersionForceMatch": false
        # }
        result = {
            "loadBalanceWeight": 50,
            "multiVersionForceMatch": False
        }
        return result

    def get_realms_app_port_list(self,app_name):
        result = self.get_children('/realms/' + app_name)
        return result

    def get_realms_params_by_port(self,app_name,port):
        result = self.get('/realms/' + app_name + '/' + str(port))
        return result

    def get_applications(self):
        result = self.get_children('/applications')
        return result

    def get_realms(self):
        result = self.get_children('/realms')
        return result

    def get_available_node(self, app_name):
        resuts = []
        try:
            ports = self.get_realms_app_port_list(app_name)
        except Exception as e:
            return resuts
        for _port in ports:
            _params = self.get_realms_params_by_port(app_name, _port)[0]
            _params = _params.decode()
            try:
                _params = json.loads(_params)
            except Exception as e:
                _params = None
            if not _params:
                continue
            try:
                if _params['state'] == 'Running':
                    resuts.append('http://' + _params['appHost'] + ':' + str(_params['appPort']) + '/')
            except Exception as e:
                pass
        return resuts

    # zk_plus = ZookeeperPlus()

#用于获取动态参数改变 暂时不启用
# @zk_plus.client.DataWatch('/realms/')
# def zookeeper_nodify(data, stat, event):
#     pass
    # print("Data is %s" % data)
    # print("Version is %s" % stat.version)
    # print("Event is %s" % event)

class ZookeeperPlusWatch(object):
    watch_list = []

    def __init__(self,zookeeper_plus):
        self.zk = zookeeper_plus

    def process_data_watch(self,*args):
        pass

    def process_node_change(self,*args):
        pass

    def add_node_watch(self,node_path, func):
        if self.zk == None:
            print('add_node_watch error: zk is None')
            return False
        self.process_node_change = func

        @self.zk.ChildrenWatch(node_path)  # '/realms/python-sweet/8888'
        def children_watch(*args):
            self.process_node_change(args)
        return True

    def add_data_watch(self,node_path, func):
        if self.zk == None:
            print('add_data_watch error: zk is None')
            return False
        self.process_data_watch = func

        @zk_plus.DataWatch(node_path)  # '/realms/python-sweet/8888'
        def data_watch(*args):
            self.process_data_watch(args)
        return True


if __name__ == '__main__':
    zk_plus = ZookeeperPlus('10.86.87.180:2181', 'sweetCloud', 'sweetCloud123')

    app_name = 'python-sweet'
    app_host = "10.200.144.127"
    app_port = 8000

    app_info_appliacations = zk_plus.create_app_infomation(app_name, '1.0', app_host, app_port, '1.0')
    app_info_realms = zk_plus.create_app_infomation(app_name, '1.0', app_host, app_port, '1.0',
                                                    state='Stoped')  # Running  Stoped
    app_runtime_data = zk_plus.create_runtime_data()

    zk_plus.set_realms(app_name, app_port, app_info_realms)
    quit(0)

    zk_plus.delete_app_path(app_name)

    zk_plus.set_configuration(app_name, app_port)
    zk_plus.set_dependencies(app_name, app_port)
    zk_plus.set_information(app_name, app_port, app_info_appliacations)
    zk_plus.set_metadata(app_name, app_port)
    zk_plus.set_runtime_data(app_name, app_port, app_runtime_data)
    zk_plus.set_realms(app_name, app_port, app_info_realms)

    # # 增加zookeeper监视节点变化
    # from SweetPy.setting import add_node_watch
    #
    # add_node_watch('path', func)
    #
    # # 增加zookeeper监视节点数据变化
    # from SweetPy.setting import add_data_watch
    #
    # add_data_watch('path', func)
    #
    # # 获取realms的所有目录
    # from SweetPy.setting import zk_plus
    #
    # zk_plus.get_realms
    #
    # # 获取get_applications的所有目录
    # from SweetPy.setting import zk_plus
    #
    # zk_plus.get_applications
    #
    # # 获取某app的可用节点路径
    # from SweetPy.setting import zk_plus
    #
    # zk_plus.get_available_node(app_name)
    #
    # # 获取某app的已打开端口列表
    # from SweetPy.setting import zk_plus
    #
    # zk_plus.get_realms_app_port_list(app_name)
    #
    # # 获取某app的某端口参数
    # from SweetPy.setting import zk_plus
    #
    # zk_plus.get_realms_params_by_port(app_name, app_port)
    #
    # # 自定义查询 参数
    # from SweetPy.setting import zk_plus
    #
    # zk_plus.get(path)
    #
    # # 自定义查询 节点
    # from SweetPy.setting import zk_plus
    #
    # zk_plus.get_children(path)