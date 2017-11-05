import io
import time
from PIL import Image, ImageDraw
from kervi.camera import FrameCameraDeviceDriver
import picamera


class CameraDriver(FrameCameraDeviceDriver):
    def __init__(self):
        FrameCameraDeviceDriver.__init__(self)

    def capture_frames(self):
        with picamera.PiCamera() as camera:
            print("start Raspberry Pi camera")
            camera.resolution = (self.camera.width, self.camera.height)
            camera.framerate =  self.camera.fps
            camera.hflip = self.camera.flip_horizontal
            camera.vflip = self.camera.flip_vertical
            camera.shutter_speed = 0
            time.sleep(2)
            stream = io.BytesIO()
            for foo in camera.capture_continuous(stream, format="jpeg", use_video_port=True):
                stream.seek(0)
                image = Image.open(stream)
                self.frame_ready(image.copy())
                stream.seek(0)
                self.wait_next_frame()
                if self.terminate:
                    break
