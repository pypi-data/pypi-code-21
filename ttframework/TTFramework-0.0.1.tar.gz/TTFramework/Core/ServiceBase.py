from abc import abstractmethod,ABCMeta

class ServiceBase(metaclass=ABCMeta):
    #消息循环主函数  BASE实现 子类可以直接复写为进程模式
    def processMain(self):
        while True:
            try:
                self.send_alive()
                _queue_value = self.queue.get(timeout=self.loopTime)
                if _queue_value == 'end':
                    try:
                        self.destory()
                    except:
                        pass
                    self.logger.info('服务[' + self.name + ']执行结束!')
                    quit(0)
            except Exception as e:
                pass
            try:
                self.mainLoop()
            except Exception as e:
                self.logger.error('服务[' + self.name + ']执行出错 错误信息:' + str(e))

    def send_alive(self):
        self.pipe_send_alive.send(self.name)

    # 处理过来的请求  各模块自己实现
    @abstractmethod
    def mainLoop(self):
        pass

    @abstractmethod
    def init(self):
        pass


    @abstractmethod
    def destory(self):
        pass
