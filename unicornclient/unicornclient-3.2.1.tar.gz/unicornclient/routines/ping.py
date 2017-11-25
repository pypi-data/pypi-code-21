from unicornclient import routine
from unicornclient import message

class Routine(routine.Routine):
    def __init__(self):
        routine.Routine.__init__(self)
        self.last_ping_id = None

    def run(self):
        while True:
            data = self.queue.get()

            ping_id = data['id'] if 'id' in data else None
            if ping_id:
                self.last_ping_id = ping_id
                payload = {'type': 'pong', 'id': ping_id}
                self.manager.send(message.Message(payload))

            self.queue.task_done()
