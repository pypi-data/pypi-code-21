from unicornclient import hat
from unicornclient import routine

class Routine(routine.Routine):
    def __init__(self):
        routine.Routine.__init__(self)
        self.hat = hat.Microdot()

    def run(self):
        while True:
            data = self.queue.get()
            text = data['text'] if 'text' in data else None

            if text:
                self.hat.clear()
                self.hat.write_string(str(text))
                self.hat.show()

            self.queue.task_done()
