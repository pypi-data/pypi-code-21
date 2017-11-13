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
        self.delete("/applications/" + app_name + '/' + str(app_port), recursive)

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

# zk_plus = ZookeeperPlus()

#用于获取动态参数改变 暂时不启用
# @zk_plus.client.DataWatch('/realms/')
# def zookeeper_nodify(data, stat, event):
#     pass
    # print("Data is %s" % data)
    # print("Version is %s" % stat.version)
    # print("Event is %s" % event)