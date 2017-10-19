
## this is write by qingluan 
# just a inti handler 
# and a tempalte offer to coder
import json
import tornado
import tornado.web
from tornado import httpclient
from tornado.websocket import WebSocketHandler
from FlowWork.Net.flownet import FLowNet
import os, time, re
from hashlib import md5
from qlib.log import show

H = lambda x: md5(x).hexdigest()

class BaseHandler(tornado.web.RequestHandler):
    def prepare(self):
        self.db = self.settings['db']
        self.L = self.settings['L']
    def get_current_user(self):
        return (self.get_cookie('user'),self.get_cookie('passwd'))
    def get_current_secure_user(self):
        return (self.get_cookie('user'),self.get_secure_cookie('passwd'))
    def set_current_seccure_user_cookie(self,user,passwd):
        self.set_cookie('user',user)
        self.set_secure_cookie("passwd",passwd)


class SocketHandler(WebSocketHandler):
    """ Web socket """
    clients = set()
    con = dict()
         
    @staticmethod
    def send_to_all(msg):
        for con in SocketHandler.clients:
            con.write_message(json.dumps(msg))
         
    @staticmethod
    def send_to_one(msg, id):
        SocketHandler.con[id(self)].write_message(msg)

    def json_reply(self, msg):
        self.write_message(json.dumps(msg))

    def open(self):
        SocketHandler.clients.add(self)
        SocketHandler.con[id(self)] = self
         
    def on_close(self):
        SocketHandler.clients.remove(self)
         
    def on_message(self, msg):
        SocketHandler.send_to_all(msg)





class IndexHandler(BaseHandler):
    
    def prepare(self):
        super(IndexHandler, self).prepare()
        self.template = "template/index.html"

    def get(self):
        # L is log function , which include ok , info , err , fail, wrn
        self.L.ok('got')
        return self.render(self.template, post_page="/")

    @tornado.web.asynchronous
    def post(self):
        # you should get some argument from follow 
        post_args = self.get_argument("some_argument")
        # .....
        # for parse json post
        # post_args = json.loads(self.request.body.decode("utf8", "ignore"))['msg']
        
        # redirect or reply some content
        # self.redirect()  
        self.write("hello world")
        self.finish()
    


class ScanHandler(BaseHandler):
    
    def prepare(self):
        super(ScanHandler, self).prepare()
        self.template = "template/scan.html"

    def get(self):
        # L is log function , which include ok , info , err , fail, wrn
        self.L.ok('got')
        return self.render(self.template, post_page="/scan")

    @tornado.web.asynchronous
    def post(self):
        # you should get some argument from follow 
        post_args = self.get_argument("some_argument")
        # .....
        # for parse json post
        # post_args = json.loads(self.request.body.decode("utf8", "ignore"))['msg']
        
        # redirect or reply some content
        # self.redirect()  
        self.write("hello world")
        self.finish()
    


class RelayHandler(BaseHandler):
    
    def prepare(self):
        super(RelayHandler, self).prepare()
        self.template = "template/relay.html"

    @tornado.web.asynchronous
    def get(self):
        # L is log function , which include ok , info , err , fail, wrn
        url = self.get_argument('target')
        actions = self.get_argument('actions', None)
        port = self.get_argument('port', None)
        show(url, actions, port, color='cyan')
        if actions:
            if 'target' in url:
                u = re.findall(r'target=(.+)',url)[0]
            else:
                u = url
            if 'http' not in u:
                u = 'http://' + u
            
            actions = u + "\n" + actions.replace(",","\n")
            print()
            print(actions)
            print()
            if port:
                f = FLowNet(url=url, proxy='socks5://127.0.0.1:'+port)
            else:
                f = FLowNet(url=url)

            f.flow_doc(actions)
            self.write(f.html())
            
        else:
            if 'http' not in url:
                url = 'http://' + url

            if port:

                f = FLowNet(url=url, proxy='socks5://127.0.0.1:'+port)
                res = f.html()
                self.write(res)
            else:
                http_client = httpclient.HTTPClient()
                try:
                    response = http_client.fetch(url)
                    body = response.body
                    self.write(body)
                    # self.finish()
                except httpclient.HTTPError as e:
                    f = FLowNet(url=url)
                    res = f.html()
                    self.write(res)
                    # HTTPError is raised for non-200 responses; the response
                    # can be found in e.response.
                    # print("Error: " + str(e))
                    # self.write(str(e))
                except Exception as e:
                    # Other errors are possible, such as IOError.
                    print("Error: " + str(e))
                    self.write(str(e))
        self.finish()
        

    @tornado.web.asynchronous
    def post(self):
        # you should get some argument from follow 
        # data = json.loads(self.get_argument("data"))
        # .....
        # for parse json post
        # post_args = json.loads(self.request.body.decode("utf8", "ignore"))['msg']
        
        # redirect or reply some content
        # self.redirect()  
        self.write("hello world")
        self.finish()
    


class ActionsHandler(BaseHandler):
    
    def prepare(self):
        super(ActionsHandler, self).prepare()
        self.template = "template/actions.html"

    def get(self):
        # L is log function , which include ok , info , err , fail, wrn
        self.L.ok('got')
        return self.render(self.template, post_page="/acitons")

    @tornado.web.asynchronous
    def post(self):
        # you should get some argument from follow 
        # print(self.request.body)
        post_args = json.loads(self.get_argument('data'))
        # .....
        # for parse json post
        print(post_args)
        data = post_args['data']
        url = re.findall(r'target=(.+)', post_args['url'])[0]
        J = os.path.join
        lines = url+"\n"
        for l in data: lines += (l+"\n")
        lines += "[over]"
        hh = H(lines.encode("utf8"))
        dirs = J(self.settings['static_path'], 'files')
        if hh + ".txt" in os.listdir(dirs):
            pass
        else:
            with open(J(dirs, hh + ".txt"),  "w") as fp:
                fp.write(lines)

            
        
        # post_args = json.loads(self.request.body.decode("utf8", "ignore"))['msg']
        
        # redirect or reply some content
        # self.redirect()  
        self.write("hello world")
        self.finish()
    