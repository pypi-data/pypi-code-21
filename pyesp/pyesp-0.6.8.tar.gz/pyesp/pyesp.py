#
import threading
from queue import Queue
from time import time, sleep
from PyQt5.QtCore import Qt, QCoreApplication, QIODevice, QObject, pyqtSignal, pyqtSlot
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo


class SerialPort(QSerialPort):
    """docstring for SerialPort"""

    readline_signal = pyqtSignal(str)
    writeline_signal = pyqtSignal(str)

    def __init__(self, serial_config, logger=None, parent=None):
        super(SerialPort, self).__init__(parent)
        self.writeline_data = ''
        self.readline_ready = False
        self.readline_data = ''
        self.workerbreak = False
        self.apply_settings(serial_config)
        #
        self.readyRead.connect(self.ready_read)
        self.writeline_signal.connect(self.write_data)
        self.log = logger
        # --- queue, threads, worker
        self.nqueue = Queue()
        t = threading.Thread(target=self.worker)
        t.daemon = True  # thread dies when main thread exits.
        t.start()

    def apply_settings(self, settings):
        self.setPortName(settings['portName'])
        self.setBaudRate(settings['baudRate'])
        self.setDataBits(settings['dataBits'])
        self.setParity(settings['parity'])
        self.setStopBits(settings['stopBits'])
        self.setFlowControl(settings['flowControl'])
        self.linedelay = settings['linedelay']

    def open(self):
        if not self.isOpen():
            return super().open(QIODevice.ReadWrite)
        return True

    def close(self):
        if self.isOpen():
            return super().close()
        return True

    def transaction(self, data, callback=None):
        if not self.open():
            raise OSError('cant open port - '+self.portName())
        #
        for s in data.split('\r\n'):
            s = s + '\r\n'
            # write line
            self.write(bytearray(s, 'utf-8'))
            #
            if not self.waitForBytesWritten(100):
                raise BaseException('error write data - ' + str(data))
            #
            # read response
            if not self.waitForReadyRead(100):
                raise BaseException('transaction response timeout error')
            #
            response = self.readAll()
            #
            while self.waitForReadyRead(100):
                response += self.readAll()

            try:
                response = str(response, 'utf-8')
            except UnicodeDecodeError:
                response = 'UnicodeDecodeError'
            #
            start_index = response.find(s)
            if start_index != -1:
                response = response[start_index+len(s):]
            #
            if callback:
                callback(response)
            #
            sleep(self.linedelay/1000)
        #
        self.close()

    @pyqtSlot(str)
    def write_data(self, data):
        if self.open():
            if self.write(bytearray(data, 'windows-1251')) != 0:
                self.workerbreak = False
                return
        self.workerbreak = True

    @pyqtSlot()
    def ready_read(self):
        try:
            data = self.readAll()
            read = data.data().decode('windows-1251')
        except Exception as e:
            self.log(str(e), 'err')
            self.workerbreak = True
            return

        self.readline_data += read
        indx = self.readline_data.rfind('\r\n')
        if indx != -1:
            self.ready_readline(self.readline_data[:indx])
            self.readline_data = self.readline_data[indx+2:]

    def ready_readline(self, data):
        self.readline_ready = True
        self.readline_signal.emit(data)

    def write_line(self, string):
        self.nqueue.join()
        self.readline_data = ''
        self.writeline_data = string
        self.nqueue.put('writelines')

    def worker(self):
        while True:
            item = self.nqueue.get()

            with threading.Lock():

                if item == 'writelines':
                    for s in self.writeline_data.split('\r\n'):
                        if self.workerbreak == True:
                            break
                        # write line signal
                        self.readline_ready = False
                        self.writeline_signal.emit(s + '\r\n')
                        st = time()
                        # wait nodemcu respond
                        while self.readline_ready is not True:
                            if time() - st > 4:
                                print('Respond timeout ):', 'err')
                                self.workerbreak = True
                                break
                        sleep(self.linedelay/1000)

                    # reset read state and r/w lines data
                    self.readline_ready = False
                    self.workerbreak = False
                    self.writeline_data = ''

            self.nqueue.task_done()


class ESP(QCoreApplication):
    """docstring for ESP"""
    _api_file = {
        'MPY': 'data/api/mpython.json',
        'NODE': 'data/api/node.json'
    }

    def __init__(self, serialconfig, platform='USER', api_file=None, loglevel=0):
        super(ESP, self).__init__([])
        #
        self.platform = platform
        #
        if platform in ESP._api_file.keys():
            api_file = ESP._api_file[platform]
            try:
                import json
                with open(api_file, 'r') as f:
                    self.api = json.loads(f.read())
            except Exception as e:
                raise e('error load api json file, key - '+platform)
        elif api_file is None:
            raise BaseException('wrong api key or api json file')
        #
        self.txfer = b''
        self.rxfer = b''
        #
        self.serialport = SerialPort(serialconfig)
        #
        self.serialport.readline_signal.connect(
            self.read,
            no_receiver_check=True
        )
        #
        self._response_callback = None

    def send(self, command, response_callback=None, **kwargs):
        """ """
        self._response_callback = response_callback
        # esp memory optimization, split file data
        if command == 'filewrite':
            lines = kwargs.get('data', '').split('\n')
            kwargs['data'] = ''
            for line in lines:
                ln = line.replace("'", '"') + '\\n'
                api_cmd = self.api['filewriteline']
                kwargs['data'] += api_cmd.format(data=ln) + '\r\n'
        # format command and data field
        if command != 'line':
            self.txfer = self.api[command].format(**kwargs)
        else:
            self.txfer = kwargs['data']
        # prepare to send
        self.txfer += "\r\nprint('END')"
        self.txfer.replace(r'\r', r'\\r').replace(r'\n', r'\\n')
        # send self.txfer to esp
        self.serialport.write_line(self.txfer)
        #

    def read(self, data):
        # print(self.api)
        data = data.replace('>>> ', '')
        #
        print('esp read: ', data)
        if data not in self.txfer and self._response_callback:
            self._response_callback(data)
        #
        # if self.platform == 'MPY':
        #     end = data.find('>>>')
        #     if end != -1:
        #         data = data[:end]
        #
        # if len(data) and self._response_callback:
        #     self._response_callback(data)
