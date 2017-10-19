from . import cv  # @UnresolvedImport
from .conversions import cv_to_numpy
from procgraph import Generator, Block
import time


class CVCapture(Generator):

    Block.alias('cv_capture')
    Block.config('cam', default=0)
    Block.config('width', default=160)
    Block.config('height', default=120)
    Block.config('fps', default=10)
    
    Block.output('rgb')
    
    def init(self):
        cam = self.config.cam
        width = self.config.width
        height = self.config.height
        fps = self.config.fps
        
        self.info('Capturing cam=%d %dx%d @%.1f fps' % (cam, width, height, fps))
        self.capture = cv.CaptureFromCAM(cam)
        cv.SetCaptureProperty(self.capture, cv.CV_CAP_PROP_FRAME_WIDTH, width)
        cv.SetCaptureProperty(self.capture, cv.CV_CAP_PROP_FRAME_HEIGHT, height)
        cv.SetCaptureProperty(self.capture, cv.CV_CAP_PROP_FPS, fps)
    
    def update(self):
        t = time.time()
        img = cv.QueryFrame(self.capture)
        rgb = cv_to_numpy(img)
        self.set_output('rgb', value=rgb, timestamp=t)
    
    def next_data_status(self):
        return (True, None)


