import logging
from pathlib import Path

from twisted.internet import defer
from twisted.internet.defer import Deferred, inlineCallbacks

from peek_core_device._private.server.controller.UpdateController import \
    UpdateController
from peek_core_device._private.server.controller.EnrollmentController import \
    EnrollmentController
from peek_core_device._private.server.controller.OnlineController import OnlineController
from vortex.TupleAction import TupleActionABC
from vortex.handler.TupleActionProcessor import TupleActionProcessorDelegateABC
from vortex.handler.TupleDataObservableHandler import TupleDataObservableHandler

logger = logging.getLogger(__name__)


class MainController(TupleActionProcessorDelegateABC):
    def __init__(self, dbSessionCreator, tupleObservable: TupleDataObservableHandler,
                 deviceUpdateFilePath: Path):
        self._dbSessionCreator = dbSessionCreator
        self._tupleObservable = tupleObservable

        self._enrollmentController = EnrollmentController(
            dbSessionCreator, tupleObservable
        )

        self._onlineController = OnlineController(
            dbSessionCreator, tupleObservable
        )

        self._updateController = UpdateController(
            dbSessionCreator, tupleObservable, deviceUpdateFilePath
        )

    @property
    def deviceUpdateController(self):
        return self._updateController

    def shutdown(self):
        self._enrollmentController.shutdown()
        self._onlineController.shutdown()
        self._updateController.shutdown()

    @inlineCallbacks
    def processTupleAction(self, tupleAction: TupleActionABC) -> Deferred:
        result = yield self._enrollmentController.processTupleAction(tupleAction)
        if result is not None:
            defer.returnValue(result)

        result = yield self._onlineController.processTupleAction(tupleAction)
        if result is not None:
            defer.returnValue(result)

        result = yield self._updateController.processTupleAction(tupleAction)
        if result is not None:
            defer.returnValue(result)

        raise NotImplementedError(tupleAction.tupleName())
