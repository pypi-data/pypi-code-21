from typing import Union

from twisted.internet.defer import Deferred

from peek_core_device._private.tuples.WebClientVortexDetailsTuple import \
    WebClientVortexDetailsTuple
from txhttputil.util.DeferUtil import deferToThreadWrap
from vortex.Payload import Payload
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleDataObservableHandler import TuplesProviderABC


class WebClientVortexDetailsTupleProvider(TuplesProviderABC):
    @deferToThreadWrap
    def makeVortexMsg(self, filt: dict,
                      tupleSelector: TupleSelector) -> Union[Deferred, bytes]:
        from peek_platform import PeekPlatformConfig


        tuple = WebClientVortexDetailsTuple()
        tuple.websocketPort = PeekPlatformConfig.config.webSocketPort

        # Create the vortex message
        return Payload(filt, tuples=[tuple]).toVortexMsg()
