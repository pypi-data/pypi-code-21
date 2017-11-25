import datetime
import logging
import time
import io

from unicornclient import message
from unicornclient import routine

try:
    from picamera import PiCamera
except ImportError:
    PiCamera = None
    logging.warning("No picamera module")

class Routine(routine.Routine):
    def __init__(self):
        routine.Routine.__init__(self)
        self.manager = None

    def run(self):
        if not PiCamera:
            return

        camera = PiCamera()
        camera.resolution = (1024, 768)
        camera.start_preview()
        time.sleep(2) # Camera warm-up time

        while True:
            self.queue.get()

            pic_stream = io.BytesIO()
            camera.annotate_text = datetime.datetime.now().strftime("%H:%M:%S %d-%m-%Y")
            camera.capture(pic_stream, 'jpeg', resize=(320, 240))
            pic_stream.seek(0)
            data = pic_stream.read()

            header = {'type':'capture'}
            pic_message = message.Message(header)
            pic_message.set_body(data)
            self.manager.send(pic_message)

            self.queue.task_done()
