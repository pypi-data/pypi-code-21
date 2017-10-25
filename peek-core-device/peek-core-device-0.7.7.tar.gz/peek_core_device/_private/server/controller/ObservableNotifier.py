import logging

from twisted.internet import reactor

from peek_core_device._private.storage.DeviceInfoTuple import DeviceInfoTuple
from peek_core_device._private.storage.DeviceUpdateTuple import DeviceUpdateTuple
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleActionProcessor import TupleActionProcessorDelegateABC
from vortex.handler.TupleDataObservableHandler import TupleDataObservableHandler

logger = logging.getLogger(__name__)


class ObservableNotifier(TupleActionProcessorDelegateABC):
    @classmethod
    def notifyDeviceInfo(cls, deviceId: str,
                         tupleObservable: TupleDataObservableHandler):
        reactor.callLater(0, cls._notifyDeviceInfoObservable, deviceId, tupleObservable)

    @staticmethod
    def _notifyDeviceInfoObservable(deviceId: str,
                                    tupleObservable: TupleDataObservableHandler):
        """ Notify the observer of the update

         This tuple selector must exactly match what the UI observes

        """

        tupleObservable.notifyOfTupleUpdate(
            TupleSelector(DeviceInfoTuple.tupleName(), dict(deviceId=deviceId))
        )

        tupleObservable.notifyOfTupleUpdate(
            TupleSelector(DeviceInfoTuple.tupleName(), dict())
        )


    @classmethod
    def notifyDeviceUpdate(cls, deviceType: str,
                         tupleObservable: TupleDataObservableHandler):
        reactor.callLater(0, cls._notifyDeviceTypeObservable, deviceType, tupleObservable)

    @staticmethod
    def _notifyDeviceTypeObservable(deviceType: str,
                                    tupleObservable: TupleDataObservableHandler):
        """ Notify the observer of the update

         This tuple selector must exactly match what the UI observes

        """

        tupleObservable.notifyOfTupleUpdate(
            TupleSelector(DeviceUpdateTuple.tupleName(), dict(deviceType=deviceType))
        )

        tupleObservable.notifyOfTupleUpdate(
            TupleSelector(DeviceUpdateTuple.tupleName(), dict())
        )
