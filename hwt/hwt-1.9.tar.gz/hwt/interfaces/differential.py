from hwt.interfaces.std import Signal
from hwt.synthesizer.interfaceLevel.interface import Interface


class DifferentialSig(Interface):
    def _declr(self):
        self.n = Signal()
        self.p = Signal()
