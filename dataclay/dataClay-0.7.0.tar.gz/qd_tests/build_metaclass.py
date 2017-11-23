from io import BytesIO

from dataclay import initialize
from dataclay.core.containers import *
from dataclay.debug.test_classes import easy_classes
from dataclay.managers.classes.factory import MetaClassFactory

__author__ = 'Alex Barcelo <alex.barcelo@bsc.es>'
__copyright__ = '2015 Barcelona Supercomputing Center (BSC-CNS)'

if __name__ == "__main__":
    initialize()

    mcf = MetaClassFactory()

    mcf.add_package("test_classes", easy_classes)

    print mcf.classes[0]

    s = BytesIO()
    serialization_bytes = mcf.classes[0].serialize(s)
    s.seek(0)
    mc = MetaClass.deserialize(s)

    print mc.name
