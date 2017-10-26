
import multiprocessing,threading
from abc import abstractmethod,ABCMeta

class Base(object):

    def __init__(self):
        self._pipe_exec, self._pipe_result = multiprocessing.Pipe(True)
        self.__thread_exec = threading.Thread(target=self.exec_from_pipe, args=())
        self.__thread_exec.daemon = True
        self.__thread_exec.start()


    def exec_from_pipe(self):
        while True:
            try:
                _command = self._pipe_exec.recv()
                cmd = _command[0]
                value = _command[1]
                _ = self.exec_command(cmd,value)
                self._pipe_exec.send(_)
            except Exception as e:
                self._pipe_exec.send(None)

    def exec_command(self,cmd,params_value):
        if params_value == None:
            return getattr(self, cmd)()
        else:
            return getattr(self, cmd)(params_value)


    def send_pipe_command(self,params):
        self._pipe_result.send(params)
        return self._pipe_result.recv()




