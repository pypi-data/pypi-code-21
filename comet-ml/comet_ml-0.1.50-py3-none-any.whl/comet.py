'''
Author: Gideon Mendels

This module contains the main components of comet.ml client side

'''
from __future__ import print_function
import inspect
import threading
import sys, os

if sys.version_info[0] < 3:
    from Queue import Queue
else:
    from queue import Queue

import requests
import json
import uuid

import time

import websocket


import comet_ml
from comet_ml import config
from comet_ml import sklearn_logger
from comet_ml import keras_logger
from comet_ml.json_encoder import NestedEncoder


DEBUG = False

"""
A static class that handles the connection with the server.
"""


class RestServerConnection(object):
    server_address = os.environ.get('COMET_URL_OVERRIDE', 'https://www.comet.ml/api/client-lib/')

    def __init__(self):
        pass

    @staticmethod
    def get_run_id(api_key, project_name):
        """
        Gets a new run id from the server.
        :param api_key: user's API key
        :return: run_id - String
        """
        endpoint_url = RestServerConnection.server_address + "add/run"
        headers = {'Content-Type': 'application/json;charset=utf-8'}

        try:
            version_num = comet_ml.__version__
        except NameError:
            version_num = None

        payload = {"apiKey": api_key, "local_timestamp": int(time.time() * 1000), "projectName": project_name, "libVersion": version_num}
        r = requests.post(url=endpoint_url, data=json.dumps(payload), headers=headers)

        if r.status_code != 200:
            raise ValueError(r.content)

        res_body = json.loads(r.content.decode('utf-8'))
        run_id_server = res_body["runId"]
        ws_server = res_body["ws_url"]

        if "project_id" in res_body:
            project_id = res_body["project_id"]
        else:
            project_id = None

        if "msg" in res_body:
            print(res_body["msg"])

        return run_id_server, ws_server, project_id

    @staticmethod
    def send_message(message):
        """
        Sends a json with stdout/metric/code to the server.
        :param message: A message object containing the values to send
        :return: True if request was sucessful.
        """
        global run_id

        if message.stdout is not None:
            base_url = RestServerConnection.server_address + "add/stdout"
        else:
            base_url = RestServerConnection.server_address + "add/data"

        headers = {'Content-Type': 'application/json;charset=utf-8'}
        r = requests.post(url=base_url, data=message.to_json(), headers=headers)

        if r.status_code != 200:
            raise ValueError(r.content + ",to address %s With request: %s" % (base_url, message))

        if run_id is None:
            run_id = json.loads(r.content)['message']

        return True


class WebSocketConnection(threading.Thread):
    def __init__(self, server_address):
        threading.Thread.__init__(self)
        self.priority = 0.2
        self.daemon = True

        if DEBUG:
            websocket.enableTrace(True)

        self.address = server_address
        self.ws = self.connect_ws(self.address)


    def is_connected(self):
        if self.ws.sock is not None:
            return self.ws.sock.connected
        else:
            return False

    def connect_ws(self, server_address):
        ws = websocket.WebSocketApp(server_address,
                                         on_message=WebSocketConnection.on_message,
                                         on_error=WebSocketConnection.on_error,
                                         on_close=WebSocketConnection.on_close)
        ws.on_open = WebSocketConnection.on_open
        return ws

    def run(self):
        while True:
            try:
                self.ws.run_forever()
            except Exception as e:
                if sys is not None and DEBUG:
                    print(e, file=sys.stderr)

    def send(self, messages):
        messagesArr = []
        for message in messages:
            payload = {}
            # make sure connection is actually alive
            if message.stdout is not None:
                payload["stdout"] = message
            else:
                payload["log_data"] = message

            messagesArr.append(payload)

        if self.ws.sock:
            self.ws.send(json.dumps(messagesArr, cls=NestedEncoder))
            return
        else:
            self.wait_for_connection()

    def wait_for_connection(self):

        if not self.is_connected():
            num_tries = 0

            while not self.is_connected() and num_tries < 5:
                time.sleep(2)
                num_tries += 1

            if not self.is_connected():
                raise ValueError("Could not connect to server after multiple tries. ")

        return True

    @staticmethod
    def on_open(ws):
        if DEBUG:
            print("Socket connection open")

    @staticmethod
    def on_message(ws, message):
        if DEBUG:
            print(message)

    @staticmethod
    def on_error(ws, error):
        error_type_str = type(error).__name__
        ignores = ['WebSocketBadStatusException', 'error', 'WebSocketConnectionClosedException', 'ConnectionRefusedError', 'BrokenPipeError']

        if not DEBUG and error_type_str in ignores:
            return

        print(error)

    @staticmethod
    def on_close(ws):
        if DEBUG:
            print("### closed ###")


'''
This class extends threading.Thread and provides a simple concurrent queue
and an async service that pulls data from the queue and sends it to the server.
'''


class Streamer(threading.Thread):
    def __init__(self, ws_server_address):
        threading.Thread.__init__(self)
        self.daemon = True
        self.messages = Queue()
        self.counter = 0
        self.ws_connection = WebSocketConnection(ws_server_address)
        self.ws_connection.start()
        self.ws_connection.wait_for_connection()


    def put_messge_in_q(self, message):
        '''
        Puts a message in the queue
        :param message: Some kind of payload, type agnostic
        '''
        if message is not None:
            self.messages.put(message)

    def close(self):
        '''
        Puts a None in the queue which leads to closing it.
        '''
        self.messages.put(None)
        self.messages.join()

    def run(self):
        '''
        Continuously pulls messages from the queue and sends them to the server.
        '''
        self.ws_connection.wait_for_connection()

        while True:
            try:
                if self.ws_connection is not None and self.ws_connection.is_connected():
                    messages = self.getn(1)

                    if messages is None:
                        break

                    self.ws_connection.send(messages)

            except Exception as e:
                if sys is not None:
                    print(e, file=sys.stderr)
        return

    def getn(self, n):
        msg = self.messages.get() # block until at least 1
        self.counter += 1
        msg.set_offset(self.counter)
        result = [msg]
        try:
            while len(result) < n:
                anotherMsg = self.messages.get(block=False) # dont block if no more messages
                self.counter += 1
                anotherMsg.set_offset(self.counter)
                result.append(anotherMsg)
        except:
            pass
        return result

    def waitForFinish(self):
        print("uploading stats to Comet before program termination (may take several seconds)")

        import time
        startTime = time.time()

        while not self.messages.empty():
            now = time.time()
            if (now - startTime > 30):
                break
        if config.experiment is not None:
            print("go to https://www.comet.ml/view/%s to view your run." % config.experiment.api_key)
        else:
            print("go to https://www.comet.ml to view your run.")


'''
A class the overwrites sys.stdout with itself.
The class prints everything as normal to console but also submits
every line to Streamer
'''


class StdLogger(object):
    # todo: this doesn't log the output from C libs (tensorflow etc)
    def __init__(self, streamer):
        '''
        :param streamer: An instance of Streamer() to allow sending to server.
        '''
        self.terminal = sys.stdout
        self.streamer = streamer
        self.api_key = None
        sys.stdout = self

    def write(self, line):
        '''
        Overrides the default IO write(). Writes to console + queue.
        :param line: String printed to stdout, probably with print()
        '''
        self.terminal.write(line)
        payload = Message(api_key=self.api_key, experiment_key=None)
        payload.set_stdout(line)
        self.streamer.put_messge_in_q(payload)

    def flush(self):
        self.terminal.flush()

    def set_api_key(self, key):
        self.api_key = key

    def isatty(self):
        return False


class Message(object):
    def __init__(self, api_key, experiment_key):
        self.apiKey = api_key
        self.experimentKey = experiment_key
        self.runId = run_id
        self.projectId = project_id
        self.local_timestamp = int(time.time() * 1000)

        # The following attributes are optional
        self.metric = None
        self.param = None
        self.graph = None
        self.code = None
        self.stdout = None
        self.offset = None
        self.fileName = None
        self.installed_packages = None

    def set_installed_packages(self, val):
        self.installed_packages = val

    def set_offset(self, val):
        self.offset = val

    def set_metric(self, name, value):
        self.metric = {"metricName": name, "metricValue": value}

    def set_param(self, name, value):
        self.param = {"paramName": name, "paramValue": value}

    def set_graph(self, graph):
        self.graph = graph

    def set_code(self, code):
        self.code = code

    def set_stdout(self, line):
        self.stdout = line

    def set_filename(self, fname):
        self.fileName = fname

    def to_json(self):
        json_re = json.dumps(self.repr_json(), sort_keys=True, indent=4, cls=NestedEncoder)
        return json_re

    def repr_json(self):
        return self.__dict__

    def __str__(self):
        return self.to_json()

    def __len__(self):
        return len(self.to_json())



'''
An instance of experiment. Takes the values from the different implementations and unifies them
for the server. Basically submits stuff to the Streamer queue.
'''


class Experiment(object):
    def __init__(self, api_key, project_name=None, log_code=True, calling_class=None):
        '''
        Init a new experiment.
        :param api_key: key used to send data to server.
        '''
        config.experiment = self

        self.project_name = project_name

        self.api_key = api_key

        # Generate a unique identifier for this experiment.
        self.id = self._generate_guid()
        self.alive = False

        global streamer
        global logger
        global run_id
        global project_id

        try:
            # This init the streamer and logger for the first time.
            # Would only be called once.
            if (streamer is None and logger is None):
                # Get an id for this run
                try:
                    run_id, ws_server_address, project_id = RestServerConnection.get_run_id(self.api_key, self.project_name)
                    full_ws_url = ws_server_address + "?apiKey=" + api_key + "&runId=" + run_id
                except ValueError:
                    print("Failed to establish connection to Comet server. Please check you internet connection. Your "
                          "experiment would not be logged")
                    return


                # Initiate the streamer
                streamer = Streamer(full_ws_url)
                # Overwride default sys.stdout and feed to streamer.
                logger = StdLogger(streamer)
                # Start streamer thread.
                streamer.start()

            self.streamer = streamer
            logger.set_api_key(self.api_key)

            self.alive = True

        except:
            print('comet.ml error: run will not be logged')


        # This allows different implementations to provide the correct source code with logging
        # our library code.
        try:
            #todo gidim: test this works.
            if self.__in_notebook():
                # self.set_notebook_name()
                pass
            else:
                self.set_filename(self._get_filename())


            self.set_pip_packages()
            self.set_cmd_args()

            if log_code:
                self.set_code(self._get_source_code())
        except Exception as e:
            print('comet.ml error: failed to set run metadata (code/pip/file-name)')


        print("your run is live at: https://www.comet.ml/view/%s" % self.api_key)

    def log_step_end(self, step):
        if self.alive:
            message = Message(self.api_key, self.id)
            message.set_param("curr_step", step)
            self.streamer.put_messge_in_q(message)

    def log_accuracy(self,acc):
        self.log_metric("acc",acc)

    def log_loss(self,loss):
        self.log_metric("loss",loss)

    def log_step(self,step):
        self.log_parameter("curr_step",step)

    def log_epoch_end(self, epoch_cnt):
        '''
        Logs that the current epoch finished + number. required for progress bars.
        :param epoch_cnt: integer
        '''
        if self.alive:
            message = Message(self.api_key, self.id)
            message.set_param("curr_epoch", epoch_cnt)
            self.streamer.put_messge_in_q(message)

    def log_metric(self, name, value):
        """
        Logs a metric (i.e accuracy, f1). Required for training visualizations.
        :param name: Metric name - String
        :param value: Metric value - float
        """
        if self.alive:
            message = Message(self.api_key, self.id)
            message.set_metric(name, value)
            self.streamer.put_messge_in_q(message)

    def log_parameter(self, name, value):
        '''
        Logs an hyper parameters
        :param name: Parameter name - String
        :param value: Parameter value - String
        '''
        if self.alive:
            message = Message(self.api_key, self.id)
            message.set_param(name, value)
            self.streamer.put_messge_in_q(message)

    def set_num_of_epocs(self,num):
        pass

    def log_epoch_ended(self):
        pass

    def log_current_epoch(self, value):
        if self.alive:
            message = Message(self.api_key, self.id)
            message.set_metric('curr_epoch', value)
            self.streamer.put_messge_in_q(message)


    def log_multiple_params(self,dic, prefix=None):
        if self.alive:
            for k,v in dic.items():
                if prefix is not None:
                    k = prefix + "_" + str(k)

                self.log_parameter(k,v)

    def log_dataset_hash(self, data):
        try:
            import hashlib
            data_hash = hashlib.md5(str(data).encode('utf-8')).hexdigest()
            self.log_parameter("dataset_hash", data_hash[:12])
        except:
            print('failed to create dataset hash')


    def set_code(self, code):
        '''
        Sets the current experiment script's code. Should be called once per experiment.
        :param code: String
        '''
        if self.alive:
            message = Message(self.api_key, self.id)
            message.set_code(code)
            self.streamer.put_messge_in_q(message)

    def set_model_graph(self, graph):
        '''
        Sets the current experiment computation graph.
        :param graph: JSON
        '''
        if self.alive:

            if type(graph).__name__ == "Graph": # Tensorflow Graph Definition
                from google.protobuf import json_format
                graph_def = graph.as_graph_def()
                graph = json_format.MessageToJson(graph_def)

            message = Message(self.api_key, self.id)
            message.set_graph(graph)
            self.streamer.put_messge_in_q(message)

    def set_filename(self, fname):
        if self.alive:
            message = Message(self.api_key, self.id)
            message.set_filename(fname)
            self.streamer.put_messge_in_q(message)

    def set_pip_packages(self):
        if self.alive:
            try:
                import pip
                installed_packages = pip.get_installed_distributions()
                installed_packages_list = sorted(["%s==%s" % (i.key, i.version)
                                                  for i in installed_packages])
                message = Message(self.api_key, self.id)
                message.set_installed_packages(installed_packages_list)
                self.streamer.put_messge_in_q(message)
            except: #TODO log/report error
                pass

    def set_cmd_args(self):
        if self.alive:
            if len(sys.argv) > 1:
                for i, arg in enumerate(sys.argv):
                    message = Message(self.api_key, self.id)
                    message.set_param("run arg_%s" % i, str(arg))
                    self.streamer.put_messge_in_q(message)


    def keras_callback(self):
        if self.alive:
            from comet_ml.frameworks import KerasCallback
            return KerasCallback(self)
        else:
            from comet_ml.frameworks import EmptyKerasCallback
            return EmptyKerasCallback()

    def _get_source_code(self):
        '''
        Inspects the stack to detect calling script. Reads source code from disk and logs it.
        '''

        class_name = self.__class__.__name__

        for frame in inspect.stack():
            if class_name in frame[4][0]:  # 4 is the position of the calling function.
                path_to_source = frame[1]
                if os.path.isfile(path_to_source):
                    with open(path_to_source) as f:
                        return f.read()
                else:
                    print("Failed to read source code file from disk: %s" % path_to_source, file=sys.stderr)

    def _get_filename(self):
        if (len(sys.argv) > 0):
            return sys.argv[0]
        else:
            return None

    def __in_notebook(self):
        return False

    @staticmethod
    def _generate_guid():
        return str(uuid.uuid4())


def on_exit_dump_messages() :
    if streamer is not None:
        streamer.waitForFinish()


streamer = None
logger = None
run_id = None
project_id = None

import atexit
atexit.register(on_exit_dump_messages)