from datetime import datetime, timedelta
import pycurl
import websocket
import json
import time

from netboy.curl.boy import CurlBoy

SOCKET_TIMEOUT = 1
TIMEOUT = 10


class GenericElement(object):
    def __init__(self, name, parent):
        self.name = name
        self.parent = parent

    def __getattr__(self, attr):
        func_name = '{}.{}'.format(self.name, attr)

        def generic_function(**args):
            self.parent.pop_messages()
            self.parent.message_counter += 1
            message_id = self.parent.message_counter
            call_obj = {'id': message_id, 'method': func_name, 'params': args}
            self.parent.ws.send(json.dumps(call_obj))
            result, _ = self.parent.wait_result(message_id)
            return result

        return generic_function


class ChromeInterface(object):
    message_counter = 0

    def __init__(self, browser, host='localhost', port=9222, socket_timeout=SOCKET_TIMEOUT, timeout=TIMEOUT):
        self.timeout = timeout
        self.socket_timeout = socket_timeout
        self.browser = browser
        self.target_id = str(self.new_target())
        page_url = 'ws://{}:{}/devtools/page/{}'.format(host, port, self.target_id)
        self.ws = websocket.create_connection(page_url, timeout=socket_timeout)
        # self.json_endp()

    def json_endp(self):
        boy = CurlBoy()
        resp = boy.get('http://127.0.0.1:9222/json', httpheader=["Content-Type: application/json; charset=utf-8"],
                       http_version=pycurl.CURL_HTTP_VERSION_1_1,
                       useragent='curl/7.53.1')
        return resp

    def new_target(self, width=1280):
        req = {}
        req['id'] = self.message_counter
        self.message_counter += 1
        req['method'] = 'Target.createTarget'
        req['params'] = {"url": "about:blank", "browserContextId": 1, "width": width}  # , "height": 1696}
        self.browser.send(json.dumps(req))
        try:
            message = self.browser.recv()
        except Exception as e:
            return None
        message = json.loads(message)
        if 'result' in message:
            return message['result']['targetId']
        return None

    def close_target(self, target_id=None):
        req = {}
        req['id'] = self.message_counter
        self.message_counter += 1
        req['method'] = 'Target.closeTarget'
        req['params'] = {"targetId": target_id or self.target_id}
        self.browser.send(json.dumps(req))
        try:
            message = self.browser.recv()
        except Exception as e:
            return None
        message = json.loads(message)
        if 'result' in message:
            return message['result']
        return None

    def close(self):
        if self.ws:
            self.ws.close()

    def get_all_targets(self):
        req = {}
        req['id'] = self.message_counter
        self.message_counter += 1
        req['method'] = 'Target.getTargets'
        # req['params'] = {"targetId": self.target_id}
        self.ws.send(json.dumps(req))
        print('hahah')
        try:
            message = self.ws.recv()
        except Exception as e:
            return None
        message = json.loads(message)
        if 'result' in message:
            return [e['targetId'] for e in message['result']['targetInfos']]
        return None

    def close_all_targets(self):
        targets = self.get_all_targets()
        results = []
        if targets:
            for target_id in targets:
                result = self.close_target(target_id)
                results.append(result)
        return results


    # Blocking
    def wait_message(self, socket_timeout=None):
        try:
            message = self.ws.recv()
        except Exception as e:
            return None
        return json.loads(message)

    # Blocking
    def wait_event(self, event, timeout=None, socket_timeout=None):
        if socket_timeout:
            self.ws.settimeout(socket_timeout)
        timeout = timeout if timeout is not None else self.timeout
        start_time = time.time()
        messages = []
        matching_message = None
        while True:
            now = time.time()
            if now - start_time > timeout:
                break
            try:
                message = self.ws.recv()
                parsed_message = json.loads(message)
                messages.append(parsed_message)
                if 'method' in parsed_message and parsed_message['method'] == event:
                    matching_message = parsed_message
                    break
            except Exception as e:
                break
        return (matching_message, messages)

    # Blocking
    def wait_result(self, result_id, timeout=None, socket_timeout=None):
        if socket_timeout:
            self.ws.settimeout(socket_timeout)
        timeout = timeout if timeout is not None else self.timeout

        start_time = time.time()
        messages = []
        matching_result = None
        while True:
            now = time.time()
            if (now - start_time) > timeout:
                break
            try:
                message = self.ws.recv()
                parsed_message = json.loads(message)
                messages.append(parsed_message)
                if 'result' in parsed_message and parsed_message['id'] == result_id:
                    matching_result = parsed_message
                    break
            except Exception as e:
                break
        return (matching_result, messages)

    # Non Blocking
    def pop_messages(self, timeout=None, socket_timeout=None):
        if socket_timeout:
            self.ws.settimeout(socket_timeout)
        timeout = timeout if timeout is not None else self.timeout
        start_time = time.time()
        messages = []
        while True:
            now = time.time()
            if now - start_time > timeout:
                break
            try:
                message = self.ws.recv()
                messages.append(json.loads(message))
            except Exception as e:
                break
        return messages

    def __getattr__(self, attr):
        genericelement = GenericElement(attr, self)
        self.__setattr__(attr, genericelement)
        return genericelement
