from operator import attrgetter
from collections import Iterator, namedtuple
import itertools

from .prv_traces import TraceReceive, TraceMethod, TraceSend


__author__ = 'Alex Barcelo <alex.barcelo@bsc.es>'
__copyright__ = '2015 Barcelona Supercomputing Center (BSC-CNS)'

global_output = None

PrvTaskInfo = namedtuple("PrvTaskInfo",
                         ["application_id", "application_tag", "task_id", "task_tag"])


class PeekabooIterator(Iterator):
    """Iterator for lists which includes a peek() function."""
    def __init__(self, underlying_list):
        """Build the Peekaboo Iterator from a simple list.
        :param underlying_list: An list-like, which should have size and cannot
        be modified (or else the Peekaboo Iterator will have undefined behaviour).
        """
        self.l = underlying_list
        self.size = len(underlying_list)
        self.idx = 0

    def __iter__(self):
        return self

    def next(self):
        if self.idx == self.size:
            raise StopIteration
        else:
            i = self.idx
            self.idx += 1
            return self.l[i]

    def peek(self):
        if self.idx == self.size:
            raise StopIteration
        return self.l[self.idx]

    def finished(self):
        return self.idx == self.size


class PrvFileInput(object):
    """Manage a .prv file.

    This class allows easy management of .prv files.
    """
    def __init__(self, filename, task_info):
        """Initialize this .prv manager by opening the file and reading first line.
        :param filename: The path of the file.
        :param task_info: The application and task information of this file.

        This initializer starts by getting the timestamp of the file (first
        line), while leaving the file opened for further processing.
        """
        self.filename = filename
        self.f = open(filename, 'r')
        l = self.f.readline().strip().split(":")
        if l[0] != "5":
            raise RuntimeError("First line of the .prv file should be the synchronization mechanism (5:...)")

        self.trace_methods = []
        self.trace_send_requests = []
        self.trace_send_responses = []
        self.trace_receive = []

        self._it_tsreq = None
        self._it_tsresp = None
        self._it_trx = None

        self._prv_threads = []

        self.sync_millis = int(l[1])
        self.sync_nanos = int(l[2])
        self.sync_start = self.sync_millis * 1000 - self.sync_nanos
        self.sync_drift = 0  # See set_drift

        self._task_info = task_info

    def __str__(self):
        return "<PrvFileInput for file: {}, status:{}>".format(
            self.filename, "CLOSED" if self.f.closed else "OPENED")

    def preprocess_all(self):
        """Read all the lines in the file, in-memory organize and close."""
        print "Preprocessing file %s..." % self.filename,
        for strline in self.f:
            line = strline.strip().split(":")

            if line[0] == "0":
                self.trace_methods.append(TraceMethod.build_from_entry(line, nano_drift=self.sync_drift))

            elif line[0] == "2":
                self.trace_receive.append(TraceReceive.build_from_entry(line, nano_drift=self.sync_drift))
            else:
                new_item = TraceSend.build_from_entry(line, nano_drift=self.sync_drift)

                if line[0] == "1":
                    self.trace_send_requests.append(new_item)
                else:
                    self.trace_send_responses.append(new_item)

        # To avoid some strange network reordering of packets, simply sort by request_id
        self.trace_send_requests.sort(key=attrgetter("request_id"))
        self.trace_send_responses.sort(key=attrgetter("request_id"))
        self.trace_receive.sort(key=attrgetter("request_id"))

        # Prepare the iterators for the network matching
        self._it_tsreq = PeekabooIterator(self.trace_send_requests)
        self._it_tsresp = PeekabooIterator(self.trace_send_responses)
        self._it_trx = PeekabooIterator(self.trace_receive)

        print "Done!"
        self.f.close()

    def check_methods(self):
        """Match all enter-exit methods in this manager.

        This is not required, but doing it is a "checksum" on the data.
        """
        # this sort is stable, and this should work
        i = iter(sorted(self.trace_methods, key=attrgetter("thread_id")))

        def deep_checker(name, thread_id):
            # This traverses the "siblings"
            for e in i:
                if e.thread_id != thread_id:
                    raise RuntimeError("The check was unsuccessful, %s was unmatched in thread %d"
                                       % (name, thread_id))
                if e.is_enter():
                    deep_checker(e.full_name, thread_id)
                else:
                    if e.full_name != name:
                        raise RuntimeError("Trying to exit %s before exiting %s (at thread %d)"
                                           % (e.full_name, name, thread_id))
                    # everything seems ok
                    return

        for thread_navigator in i:
            deep_checker(thread_navigator.full_name, thread_navigator.thread_id)

        # No raise === everything ok!
        return True

    @staticmethod
    def _is_network_match(tx, rx):
        """Check if two trace entries are a valid match (connection type).
        :type tx: TraceSend
        :type rx: TraceReceive
        :param tx: The transmit tuple.
        :param rx: The receive tuple.
        :return: True if it is a matching connection, false otherwise.
        """
        return tx.request_id == tx.request_id and \
            tx.method_id == rx.method_id and \
            tx.sending_port == rx.origin_host_port

    def check_send_to(self, prv_rx):
        """Check if the provided send-receive is valid.
        :type prv_rx: PrvFileInput
        :param prv_rx: Another PrvFile instance.
        :return: True if it is a valid network connection, false otherwise. In
        addition to internal storage for latter Paraver file generation.
        """
        try:
            remote_rx = prv_rx._it_trx.peek()
        except StopIteration:
            return False

        try:
            local_tx = self._it_tsreq.peek()
            if self._is_network_match(local_tx, remote_rx):
                global_output.add_network(local_tx.time,
                                          self._task_info, self._it_tsreq.next(),
                                          prv_rx._task_info, prv_rx._it_trx.next())
                return True
        except StopIteration:
            # Check the other one
            pass

        try:
            local_tx = self._it_tsresp.peek()
            if self._is_network_match(local_tx, remote_rx):
                global_output.add_network(local_tx.time,
                                          self._task_info, self._it_tsresp.next(),
                                          prv_rx._task_info, prv_rx._it_trx.next())
                return True
        except StopIteration:
            pass
        return False

    def get_absolute_start(self):
        """Get the starting time of the trace.
        :return: The value (in nanos) according to the beginning of the trace
        """
        # It has been preevaluated in preprocess_all
        return self.sync_start

    def set_drift(self, nano_drift):
        """Set the drift for this specific file.
        :param nano_drift: The value (in nanoseconds and with sign) to add to
        the events on this file.

        This should be set before processing any file in the file.
        """
        self.sync_drift = nano_drift

    def done(self):
        """Return True when all internal iterators are finished (all network traces have been processed)."""
        return self._it_tsreq.finished() and \
            self._it_tsresp.finished() and \
            self._it_trx.finished()

    def debug_head_info(self):
        """Print information on the head of network traces (do a peek on each iterator)."""
        print self
        print "     TxSendReq:", self._it_tsreq.peek() if not self._it_tsreq.finished() else " --finished--"
        print "    TxSendResp:", self._it_tsresp.peek() if not self._it_tsresp.finished() else " --finished--"
        print "            Rx:", self._it_trx.peek() if not self._it_trx.finished() else " --finished--"

    def dump_methods(self):
        """Dump all the method information onto the global output PrvFileOutput instance."""
        pass


class PrvFileOutput(object):
    """Manage a set of outputs for Paraver."""
    def __init__(self, base_path):
        """Initialize this manager with a base string for the output files."""
        self._base_path = base_path

        self._output_lines = []

    def add_network(self, timestamp, tx_prv_info, tx_trace, rx_prv_info, rx_trace):
        pass

    def dump(self):
        pass


def network_check(prv_files):
    """Simple function for easier profiling."""
    still_working = True
    while still_working:
        still_working = False
        for prv_tx, prv_rx in itertools.permutations(prv_files, 2):
            if prv_tx.check_send_to(prv_rx):
                still_working = True
                break  # micro optimization question: should this line be erased?


def main(config_structure, output_path, verify=False):
    print 'Starting dataClay Paraver "merge" util'

    global global_output
    global_output = PrvFileOutput(output_path)

    prv_files = list()
    appl_id = 0
    for application, data in config_structure:
        if "file" in data:
            prv_ti = PrvTaskInfo(appl_id, application, 0, "main")
            prv = PrvFileInput(data["file"], prv_ti)
            prv.application_id = appl_id
            prv.application_tag = application
            prv_files.append(prv)
        if "tasks" in data:
            task_id = 1
            for t in data["tasks"]:
                prv_ti = PrvTaskInfo(appl_id, application, task_id, t["name"])
                prv = PrvFileInput(t["file"], prv_ti)
                prv_files.append(prv)
                task_id += 1
        appl_id += 1

    ns_start_time = min([prv.get_absolute_start() for prv in prv_files])

    for prv in prv_files:
        prv.set_drift(prv.get_absolute_start() - ns_start_time)
        prv.preprocess_all()
        if verify:
            prv.check_methods()

    # Check all the networks
    network_check(prv_files)

    if not all([prv.done() for prv in prv_files]):
        print "Warning! Not all traces has been processed, some network problems."
        print "Head status:"
        for prv in prv_files:
            prv.debug_head_info()
        raise RuntimeError("Refusing to finish with unprocessed network traces.")

    global_output.dump()
