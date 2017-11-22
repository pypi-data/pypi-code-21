from dataclay import DataClayObject, dclayMethod

# For this to work, the stubs had to be already imported
from DataClayDomain.dataclay.collections import DataClayArrayList


class RemoteCollectionsProbe(DataClayObject):
    """
    @dclayProperty DataClayDomain.dataclay.collections.DataClayArrayList collection
    """
    @dclayMethod()
    def __init__(self):
        self.collection = None

    def create_collection(self):
        self.collection = DataClayArrayList()
