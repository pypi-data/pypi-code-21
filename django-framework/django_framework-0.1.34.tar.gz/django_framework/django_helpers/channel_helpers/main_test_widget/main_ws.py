import arrow
import json

import thread
import time

import websocket

class RequestMimic(object):
    
    def __init__(self, method, url, query_params = None, body =None, data = None, headers = None, **kwargs):
        self.kwargs = kwargs
        self.method = method.upper()
        if self.method not in ['GET', 'PUT', 'POST', 'DELETE']:
            raise ValueError('You cannot send a method that is not a get, put, post or delete')
        
        self.url = url
        
        self.path = self.url
        
        self.type = 'http' # we're making http mimics
        
        # how to set query_params
        # dict version:  {'filter': {'id' :1}}
        # string version: 'filter[id]=1'
        # NOT WORKING:  json.dumps({'filter': {'id' :1}}) <--- don't do this
        self.query_params = query_params
        self.data = data
        
        self.body = body
        
        self.requested_at = arrow.utcnow().timestamp
        self.respond_by = arrow.utcnow().timestamp + 5
        
        self.headers = headers
        if self.headers == None:
            self.headers = {}
        
        
        self.response = None
    
    def get_response(self):
        self.response = dict(
            
            method = self.method,
            path = self.path,
            
            type = self.type, # we're making http mimics
            
            
            query_params = self.query_params,
            data = self.data,
            
            body = self.body,
            
            requested_at = self.requested_at,
            respond_by = self.respond_by,
            
            headers = self.headers,
                )
        
        return self.response


def make_request(text):

    mydict = {
            "method"       : "GET",
            "url"          : text+ '/models/',
            "query_params" : None,
            "data"         : {},
            "body"         : None,
            "headers" : {
                "HTTP_AUTHORIZATION" : "Token **DES**862748f3c822417ea94e407f2a074613fcc11f1363886fdb42c1fd38aa8da1d97abeee8c54f9091f3f19b1498060399a9c0bd178d61fa3f6993456a99ee331f3a7df8b0a4472add702e03d16844201aa3a6397aa11af3a9e914a9ce71f3a1848546084e6574ddf9f24caaea58c3fce6402336c77ad414d4b64691acec72c9649648f0d528f430bfb48ffafc29b340f0c24b2a7cd3db718f44c9d98ca8088bed7be7dcdc812ede638e73f2183707808ad837067ce93077df446d01d336a9a7553f9da5b7dca1c92494d650c9c5c15806446e85d39a5615b362ab4ebcca3174b9346fc96fba7defdbd0879c14b4fc99a835d9ea51f56159d61"},

            "text" : "oh that is wierd"
    }

    return RequestMimic( **mydict).get_response()

def on_message(ws, message):
    
    print('This is reply,', message)

def on_error(ws, error):
    print error

def on_close(ws):
    print "### closed ###"

def on_open(ws):
    def run(*args):
        send_message(ws)
#         for i in range(3):
#             time.sleep(1)
#             ws.send("Hello %d" % i)
#         time.sleep(1)
#         ws.close()
        print "thread terminating..."
    thread.start_new_thread(run, ())
    

def send_message(ws):
    
    while True:
        time.sleep(0.1)
        text = raw_input(prompt = "\nWhat should I send it?")
        
        payload = make_request(text = text)
        
        text = json.dumps(payload)
        ws.send(text)
        
        if text == 'quit':
            ws.close()
            break

if __name__ == "__main__":
    websocket.enableTrace(True)
    header = ["Token : 1"]
    ws = websocket.WebSocketApp("ws://localhost:8000/ch/", header= header,
                              on_message = on_message,
                              on_error = on_error,
                              on_close = on_close)
    ws.on_open = on_open
    
    
#     send_message(ws)
    
    ws.run_forever()
    
    