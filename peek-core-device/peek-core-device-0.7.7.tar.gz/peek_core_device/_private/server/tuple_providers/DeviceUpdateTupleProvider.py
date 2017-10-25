from datetime import datetime
from typing import Union

from twisted.internet.defer import Deferred

from peek_core_device._private.storage.DeviceInfoTuple import DeviceInfoTuple
from peek_core_device._private.storage.DeviceUpdateTuple import DeviceUpdateTuple
from txhttputil.util.DeferUtil import deferToThreadWrap
from vortex.Payload import Payload
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleDataObservableHandler import TuplesProviderABC


class DeviceUpdateTupleProvider(TuplesProviderABC):
    def __init__(self, ormSessionCreator):
        self._ormSessionCreator = ormSessionCreator

    @deferToThreadWrap
    def makeVortexMsg(self, filt: dict,
                      tupleSelector: TupleSelector) -> Union[Deferred, bytes]:
        # Potential filters can be placed here.
        deviceId = tupleSelector.selector.get("deviceId")

        ormSession = self._ormSessionCreator()
        try:

            deviceInfo = None
            if deviceId is not None:
                deviceInfo = (
                    ormSession.query(DeviceInfoTuple)
                        .filter(DeviceInfoTuple.deviceId == deviceId)
                        .one()
                )

                deviceInfo.lastUpdateCheck = datetime.utcnow()
                ormSession.commit()

            tuples = []

            # Return just the one, latest update, if this is a device checking
            if deviceInfo:
                updates = (
                    ormSession.query(DeviceUpdateTuple)
                        .filter(DeviceUpdateTuple.deviceType == deviceInfo.deviceType)
                        .filter(DeviceUpdateTuple.isEnabled == True)
                        .order_by(DeviceUpdateTuple.buildDate)
                        .all()
                )

                if updates:
                    update = updates[-1]
                    if update.updateVersion != deviceInfo.updateVersion:
                        tuples = [update]

            # Else, this is the admin interface, return all of them.
            else:
                tuples = (
                    ormSession.query(DeviceUpdateTuple)
                        .order_by(DeviceUpdateTuple.buildDate)
                        .all()
                )

            # Create the vortex message
            return Payload(filt, tuples=tuples).toVortexMsg()

        finally:
            ormSession.close()
