from unicornclient import spy
from unicornclient import routine
from unicornclient import message

class Routine(routine.Routine):
    def __init__(self):
        routine.Routine.__init__(self)

    def run(self):
        while True:
            self.queue.get()
            self.send_status()
            self.queue.task_done()

    def send_status(self):
        status = self.get_status()
        payload = {
            'type':'status',
            'status': status
        }
        self.manager.forward('yocto', {})
        self.manager.send(message.Message(payload))

    def get_status(self):
        status = {
            'serial' : spy.get_serial(),
            'machine_id': spy.get_machine_id(),
            'hostname': spy.get_hostname(),
            'kernel': spy.get_kernel(),
            'uptime': spy.get_uptime(),
            'local_ip': spy.get_local_ip(),
            'addresses': spy.get_macs(),
            'temp': spy.get_temp(),
            'ssid': spy.get_ssid(),
            'signal_level': spy.get_signal_level(),
            'written_kbytes': spy.get_written_kbytes()
        }
        return status
