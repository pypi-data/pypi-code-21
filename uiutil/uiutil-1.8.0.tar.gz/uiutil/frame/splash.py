
import ttk
from PIL import Image, ImageTk
from Tkconstants import NW

from .frame import BaseFrame


class SplashFrame(BaseFrame):

    def __init__(self,
                 image_path,
                 image_width,
                 image_height,
                 info_title=None,
                 info_text=None,
                 wait_func=None,
                 *args,
                 **kwargs):

        self.wait_func = wait_func
        self.image_width = image_width
        self.image_height = image_height
        self.info_title = info_title
        self.info_text = info_text

        super(SplashFrame, self).__init__(*args, **kwargs)

        # Load Image
        self.image = Image.open(image_path)
        self.img_copy = self.image.copy()

        self.background_image = ImageTk.PhotoImage(self.image)

        self.background = self.label(image=self.background_image)
        self.background.bind('<Configure>', self._resize_image)

        if self.info_title is not None:
            info_title_style = ttk.Style()
            info_title_style.configure("SPLASH_INFO_TITLE.TLabel",
                                       foreground="black",
                                       font=('Helvetica', 30))

            self.label(text=self.info_title,
                       sticky=NW,
                       padx=15,
                       pady=20,
                       style="SPLASH_INFO_TITLE.TLabel")

        if self.info_text is not None:
            info_text_style = ttk.Style()
            info_text_style.configure("SPLASH_INFO_TEXT.TLabel",
                                      foreground="black",
                                      font=('Helvetica', 12))

            self.label(text=self.info_text,
                       sticky=NW,
                       padx=10,
                       row=1,
                       style="SPLASH_INFO_TEXT.TLabel")

        self.parent.master.update_geometry()

        if self.wait_func is not None:
            self.after(ms=500, func=self.run)

    def run(self):
        try:
            self.wait_func()

        except Exception as err:
            raise err

        finally:
            self.parent.master.exit()

    def _resize_image(self,
                      event):

        # Update background image
        self.image = self.img_copy.resize((self.image_width, self.image_height))

        self.background_image = ImageTk.PhotoImage(self.image)
        self.background.configure(image=self.background_image)
