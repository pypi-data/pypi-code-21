import psutil


class CpuInfo:
    pass


class MemInfo:
    pass


class NetInfo:
    pass


class ServerInfo:

    def __init__(self, cpu=None, mem=None, net=None):
        self._cpu_info = cpu
        self._mem_info = mem
        self._net_info = net

    def getCpuInfo(self):
        return self._cpu_info

    def getMemInfo(self):
        return self._mem_info

    def getNetInfo(self):
        return self._net_info

