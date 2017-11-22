from multiprocessing import Process

from dataclay.debug.javaserver import JavaServerManager
from dclay_server import main
from dataclay import initialize


__author__ = 'Alex Barcelo <alex.barcelo@bsc.es>'
__copyright__ = '2015 Barcelona Supercomputing Center (BSC-CNS)'

if __name__ == "__main__":
    initialize()

    # Execution Environment
    p = Process(target=main, name="dataClay Server Process")
    p.daemon = True
    p.start()

    server = JavaServerManager()
    print "Ready to do things"
    with server:
        print "Hey you! I'm in a with"

    print "Finished"
