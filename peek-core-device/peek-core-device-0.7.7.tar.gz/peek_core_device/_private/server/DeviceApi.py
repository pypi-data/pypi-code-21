import logging
from typing import Optional

from twisted.internet.defer import Deferred

from peek_core_device._private.server.controller.MainController import MainController
from peek_core_device._private.storage.DeviceInfoTuple import DeviceInfoTuple
from peek_core_device.server.DeviceApiABC import DeviceApiABC
from vortex.DeferUtil import deferToThreadWrapWithLogger, noMainThread

logger = logging.getLogger(__name__)


class DeviceApi(DeviceApiABC):
    def __init__(self, mainController: MainController,
                 ormSessionCreator):
        self._mainController = mainController
        self._ormSessionCreator = ormSessionCreator

    @deferToThreadWrapWithLogger(logger)
    def deviceDescription(self, deviceToken: str) -> Deferred:
        return self.deviceDescriptionBlocking(deviceToken)

    def deviceDescriptionBlocking(self, deviceToken: str) -> Optional[str]:
        noMainThread()

        ormSession = self._ormSessionCreator()
        try:
            all = (
                ormSession.query(DeviceInfoTuple)
                    .filter(DeviceInfoTuple.deviceToken == deviceToken)
                .all()
            )

            if not all:
                return None

            return all[0].description

        finally:
            ormSession.close()

    def shutdown(self):
        pass
