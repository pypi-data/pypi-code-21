from yesaide.worker import RawWorker


class RawForeman(RawWorker):
    """Special worker to manage other workers."""

    def __init__(self, dbsession=None):
        RawWorker.__init__(self, dbsession)
