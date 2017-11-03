
from Tkconstants import NSEW

from uiutil.window.root import RootWindow
from uiutil.frame.splash import SplashFrame


class SplashWindow(RootWindow):

    def __init__(self,
                 image_path,
                 wait_func,
                 info_title=None,
                 info_text=None,
                 message=u'Splash Screen',
                 *args,
                 **kwargs):

        self.window_title = message
        self.image_path = image_path
        self.wait_func = wait_func
        self.info_title = info_title
        self.info_text = info_text

        super(SplashWindow, self).__init__(width=640,
                                           height=452,
                                           fixed=True,
                                           padding=u'0 0 0 0',
                                           *args,
                                           **kwargs)

    def _setup(self):
        self.overrideredirect(1)  # Setting this to 1 makes window borderless (plus no OS close button)

        # Override width and height now that screen width and height are available!
        width = int(self.winfo_screenwidth() * 0.3)
        height = int(self.winfo_screenheight() * 0.3)

        self.width = width
        self.height = height

        # Manually update geometry
        self.geometry(u'{w}x{h}+{x}+{y}'.format(w=self.width,
                                                h=self.height,
                                                x=(self.winfo_screenwidth() / 2) - (self.width / 2),
                                                y=(self.winfo_screenheight() / 2) - (self.height / 2)))

        self.splash = self.add_frame(frame=SplashFrame,
                                     parent=self._main_frame,
                                     image_path=self.image_path,
                                     image_width=width,
                                     image_height=height,
                                     info_title=self.info_title,
                                     info_text=self.info_text,
                                     wait_func=self.wait_func,
                                     sticky=NSEW)
