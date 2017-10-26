import multiprocessing
import os
import threading
from .DatetimePlus import DatetimePlus


class Logger(object):
    __logList = None
    __isPrint = True
    __level = 0
    __levelDict = {
        1:'Debug',
        2:'Info',
        3:'Warning',
        4:'Error',
        5:'Fatal'
    }
    __logPath = ''

    def createFileName(self,level):
        dateStr = DatetimePlus.get_nowdate_to_str()
        result = dateStr + '_' + self.__levelDict.get(level,'Normal') + '.log'
        return result


    def write(self,s,level,dt):
        s = dt + ':' + str(s)
        if self.__isPrint:
            print(s)
        if level < self.__level:
            return
        fileName = self.__logPath + self.createFileName(level)
        with open(fileName,'a') as f:
            f.write(s + '\r\n')

    def info(self,s):
        self.__logList.put([s, 2, DatetimePlus.get_nowdatetime_to_str()])

    def debug(self,s):
        self.__logList.put([s, 1, DatetimePlus.get_nowdatetime_to_str()])

    def warning(self,s):
        self.__logList.put([s, 3, DatetimePlus.get_nowdatetime_to_str()])

    def error(self,s):
        self.__logList.put([s, 4, DatetimePlus.get_nowdatetime_to_str()])

    def fatal(self,s):
        self.__logList.put([s, 5, DatetimePlus.get_nowdatetime_to_str()])

    def normal(self,s):
        self.__logList.put([s, 0, DatetimePlus.get_nowdatetime_to_str()])

    def __getQueue(self):
        while True:
            try:
                lv = self.__logList.get(timeout=1)
                self.write(lv[0],lv[1],lv[2])
            except Exception as e:
                pass

    def __init__(self,configer):
        self.configer = configer
        self.__level = self.configer.logger_level
        self.__isPrint = self.configer.is_debug
        self.__logList = multiprocessing.Queue()
        self.__logPath = self.configer.data_path + 'Logs/'
        if not os.path.exists(self.__logPath):
            os.makedirs(self.__logPath)
        self.thread = threading.Thread(target=self.__getQueue,args=())
        self.thread.daemon = True
        self.thread.start()
