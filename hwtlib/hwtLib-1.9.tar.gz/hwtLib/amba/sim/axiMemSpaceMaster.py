from hwtLib.sim.abstractMemSpaceMaster import AbstractMemSpaceMaster


class AxiLiteMemSpaceMaster(AbstractMemSpaceMaster):
    def _writeAddr(self, addrChannel, addr, size):
        addrChannel.data.append(addr)

    def _writeData(self, data, mask):
        w = self._bus._ag.w.data
        w.append((data, mask))

    def _write(self, addr, size, data, mask):
        self._writeAddr(self._bus._ag.aw, addr, size)
        self._writeData(data, mask)

    def _read(self, addr, size):
        self._writeAddr(self._bus._ag.ar, addr, size)
