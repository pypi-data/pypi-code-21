import queue
import threading
import logging

class Sender(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.socket = None
        self.queue = queue.Queue()

    def send(self, message):
        self.queue.put(message)

    def run(self):
        while True:
            message = self.queue.get()
            self.send_one(message)
            self.queue.task_done()

    def send_one(self, message):
        if not self.socket:
            return

        try:
            self.socket.sendall(message.encode())
        except OSError as err:
            logging.error('sender error')
            logging.error(err)
            self.socket = None
