try:
    import tkinter as tk
except ImportError:
    # Python 2
    import Tkinter as tk
import re
import os
import io

try:
    import requests
except ImportError:
    REQUESTS_AVAILABLE = False
    try:
        from urllib.request import urlopen
    except ImportError:
        # Python 2
        from urllib import urlopen
else:
    REQUESTS_AVAILABLE = True

try:
    from PIL.ImageTk import PhotoImage
except ImportError:
    PIL_AVAILABLE = False
else:
    PIL_AVAILABLE = True

from . import constants
from . import styles

global tk_
tk_ = None
global hierarchy
hierarchy = {}

__all__ = [
    "Application",
    "Button",
    "Entry",
    "Frame",
    "Image",
    "Text",
    "TkinterException",
    "Window",
]


class TkinterException(Exception, object):
    """Exception.
    Raised when tk.TclError is raised and no further information is
    available to handle the exception.
    """
    pass


def validate_nonnegative(name, x):
    if not isinstance(x, int):
        raise TypeError(constants.GENERIC_NOT_INTEGER.format(name))
    if x < 0:
        raise ValueError(constants.GENERIC_NOT_POSITIVE.format(name))


def validate_parent(x):
    try:
        x.widget
        if not isinstance(x, (Widget, Window)):
            raise TypeError(constants.PARENT_WRONG_TYPE)
        return
    except AttributeError:
        pass
    raise TypeError(constants.PARENT_WRONG_TYPE)


def validate_color(x):
    if not isinstance(x, str):
        raise TypeError(constants.COLOR_NOT_STRING)
    if x not in constants.COLORS and not re.match(
        constants.HEX_COLOR, x.lower()
    ):
        raise ValueError(constants.COLOR_UNKNOWN)


def validate_width(x):
    validate_nonnegative("width", x=x)


def validate_height(x):
    validate_nonnegative("height", x=x)


def validate_image(x):
    if not isinstance(x, str):
        raise TypeError(constants.IMAGE_NOT_STRING)
    if not os.path.isfile(x):
        raise FileNotFoundError(constants.IMAGE_NOT_FILE)


def validate_align(x):
    if not isinstance(x, str):
        raise TypeError(constants.ALIGN_NOT_STRING)
    if x not in constants.ALIGNMENTS:
        raise ValueError(constants.ALIGN_UNKNOWN)


def validate_row(x):
    validate_nonnegative("row", x=x)


def validate_column(x):
    validate_nonnegative("column", x=x)


def validate_rowspan(x):
    validate_nonnegative("rowspan", x=x)


def validate_columnspan(x):
    validate_nonnegative("columnspan", x=x)


def validate_value(x):
    if not isinstance(x, str):
        raise TypeError(constants.VALUE_NOT_STRING)


def validate_style(x):
    if not isinstance(x, styles.Style):
        raise TypeError(constants.STYLE_WRONG_TYPE)


def validate_anchor(x):
    if not isinstance(x, str):
        raise TypeError(constants.ANCHOR_NOT_STR)

    anchor_map = {"left": False, "right": False, "top": False, "bottom": False}
    for anchor in x.split("-"):
        if anchor not in constants.ANCHORS:
            raise ValueError(constants.ANCHOR_UNKNOWN)
        if anchor == "fill" and len(x.split("-")) > 1:
            raise ValueError(constants.ANCHOR_FILL_COMBINED)
        elif anchor == "left":
            if anchor_map["left"]:
                raise ValueError(constants.ANCHOR_REPEATED.format("'left'"))
            if anchor_map["right"]:
                raise ValueError(constants.ANCHOR_CONFLICT.format(
                    "'left'", "'right'")
                )
            anchor_map["left"] = True
        elif anchor == "right":
            if anchor_map["right"]:
                raise ValueError(constants.ANCHOR_REPEATED.format("'right'"))
            if anchor_map["left"]:
                raise ValueError(constants.ANCHOR_CONFLICT.format(
                    "'right'", "'left'")
                )
            anchor_map["right"] = True
        elif anchor == "top":
            if anchor_map["top"]:
                raise ValueError(constants.ANCHOR_REPEATED.format("'top'"))
            if anchor_map["bottom"]:
                raise ValueError(constants.ANCHOR_CONFLICT.format(
                    "'top'", "'bottom'")
                )
            anchor_map["top"] = True
        elif anchor == "bottom":
            if anchor_map["bottom"]:
                raise ValueError(constants.ANCHOR_REPEATED.format("'bottom'"))
            if anchor_map["top"]:
                raise ValueError(constants.ANCHOR_CONFLICT.format(
                    "'bottom'", "'top'")
                )
            anchor_map["bottom"] = True


def validate_expandrow(x):
    validate_nonnegative("expandrow", x=x)


def validate_expandcolumn(x):
    validate_nonnegative("expandcolumn", x=x)


def validate_state(x):
    if not isinstance(x, str):
        raise TypeError(constants.STATE_NOT_STRING)
    if state not in constants.STATES:
        raise ValueError(constants.STATE_UNKNOWN)


def validate_title(x):
    if not isinstance(x, str):
        raise TypeError(constants.TITLE_NOT_STRING)


def validate_x_y_restrict(x, y):
    if y is not None:
        validate_height(y)
    if x is not None:
        validate_width(x)


def apply_style_recursively(instance, style):
    for widget in instance.widget.winfo_children():
        if isinstance(widget, tk.Entry):
            widget.configure(**style.entrystyle.active)
        elif isinstance(widget, tk.Label):
            widget.configure(**style.textstyle.active)
        elif isinstance(widget, tk.Button):
            widget.configure(**style.buttonstyle.active)
        elif isinstance(widget, tk.Frame):
            widget.configure(**style.framestyle.active)


def require_tk(name, instance):
    global tk_
    if not tk_:
        raise ValueError(constants.APPLICATION_NOT_EXISTS.format(
            name)
        )
    elif not instance.widget.winfo_exists():
        # The widget doesn't exist (has been destroyed).
        raise ValueError(constants.WIDGET_DESTROYED.format(
            name)
        )


def stream_image(url):
    image_bytes = []
    image_available = False
    if constants.REQUESTS_AVAILABLE:
        try:
            request = requests.get(url, stream=True)
        except request.exceptions.RequestException:
            pass
        else:
            for chunk in request.iter_content(constants.BUFFER_SIZE):
                image_bytes.append(chunk)
            image_bytes = bytes().join(image_bytes)
            image_available = True
    if not image_available:
        try:
            file_descriptor = urlopen(url)
            buffered_reader = io.BufferedReader(file_descriptor)
            while True:
                chunk = buffered_reader.read(constants.BUFFER_SIZE)
                if not chunk:
                    break
                image_bytes.append(chunk)
            image_bytes = bytes().join(image_bytes)
            image_available = True
        except OSError:
            pass
    if not image_available:
        raise ConnectionError(constants.IMAGE_STREAM_FAILED)


def load_photo_image(**kwargs):
    if constants.PIL_AVAILABLE:
        try:
            return PhotoImage(**kwargs)
        except OSError:
            pass
    try:
        return tk.PhotoImage(**kwargs)
    except tk.TclError:
        pass
    raise ValueError(constants.IMAGE_BUFFER_FAILED)


class Application(object):
    def __init__(self):
        global tk_
        if tk_:
            # A Tk object already exists.
            raise ValueError(constants.APPLICATION_ALREADY_EXISTS)
        tk_ = self
        self.widget = tk.Tk()
        self.widget.wm_withdraw()

    def destroy(self):
        global tk_
        if not tk_:
            # No Tk object remains, so this widget must already
            # have been destroyed.
            raise ValueError(constants.WIDGET_ALREADY_DESTROYED)
        else:
            # Only this Tk object remains.
            tk_ = None
            self.widget.destroy()

    def run(self):
        require_tk("run", self)
        self.widget.mainloop()


class Widget(object):
    def __init__(self, parent, wtype, **kwargs):
        try:
            kwargs.pop("image_path")
        except KeyError:
            pass
        self.widget = wtype(master=parent.widget, **kwargs)
        try:
            self.widget.__image = kwargs["image"]
            # Keep a reference to the image as to avoid
            # garbage collection.
            self.widget.__image_path = kwargs["image_path"]
        except KeyError:
            # The widget doesn't support images.
            pass
        global hierarchy
        hierarchy[self] = []
        hierarchy[parent].append(self)
        self.style = None

    def destroy(self):
        require_tk("destroy", self)
        self.hide()
        self.widget.destroy()

    def display(
                self,
                row,
                column,
                rowspan=1,
                columnspan=1,
                expandrow=0,
                expandcolumn=0,
                anchor="fill"
               ):
        require_tk("display", self)
        validate_row(row)
        validate_column(column)
        if rowspan is not None:
            validate_rowspan(rowspan)
        if columnspan is not None:
            validate_columnspan(columnspan)
        if expandrow is not None:
            validate_expandrow(expandrow)
        if expandcolumn is not None:
            validate_expandcolumn(expandcolumn)
        if anchor is not None:
            validate_anchor(anchor)
            anchor = "".join([constants.ANCHORS[n] for n in anchor.split("-")])
        self.widget.master.grid_rowconfigure(row, weight=expandrow)
        self.widget.master.grid_columnconfigure(column, weight=expandcolumn)
        self.widget.grid(
            row=row,
            column=column,
            rowspan=rowspan,
            columnspan=columnspan,
            sticky=anchor
        )

    def set_state(self, state):
        require_tk("set_state", self)
        try:
            self.widget.configure(state=state)
            return
        except tk.TclError:
            # The widget does not support switching state.
            pass
        raise TkinterException("this widget does not support switching state")

    def focus(self):
        require_tk("focus", self)
        self.widget.focus()

    def hide(self):
        require_tk("hide", self)
        self.widget.grid_forget()

    def get_style(self):
        require_tk("get_style", self)
        return self.style

    def set_style(self, style, recursive=False):
        require_tk("set_style", self)
        validate_style(style)
        stylename = self.__class__.__name__.lower() + "style"
        self.widget.configure(**getattr(style, stylename).active)
        self.style = style
        if not recursive:
            return
        apply_style_recursively(self, style=style)

    @property
    def parent(self):
        for widget in hierarchy:
            if self in hierarchy[widget]:
                return widget

    @property
    def children(self):
        for child in hierarchy[self]:
            yield child


class Window(object):
    def __init__(
                 self,
                 width=400,
                 height=400,
                 background=None,
                 title=""
                ):
        if not tk_:
            raise ValueError(
                "can't create this window, no Application instance exists"
            )
        if width is not None:
            validate_width(width)
        if height is not None:
            validate_height(height)
        if title is not None:
            validate_title(title)
        if background is not None:
            validate_color(background)
            background = constants.COLORS.get(background, background)
        self.widget = tk.Toplevel(
            master=tk_.widget,
            width=width,
            height=height,
            background=background,
        )
        self.widget.wm_title(title)
        global hierarchy
        hierarchy[self] = []
        self.style = None

    def get_minsize(self):
        require_tk("get_minsize", self)
        return self.widget.wm_minsize()

    def set_minsize(self, width=None, height=None):
        require_tk("set_minsize", self)
        validate_x_y_restrict(width, height)
        self.widget.wm_minsize(height=height, width=width)

    def get_maxsize(self):
        require_tk("get_maxsize", self)
        return self.widget.wm_maxsize()

    def set_maxsize(self, width=None, height=None):
        require_tk("set_maxsize", self)
        validate_x_y_maxsize(width, height)
        self.widget.wm_maxsize(height=height, width=width)

    def get_width(self):
        require_tk("get_width", self)
        return self.widget.winfo_width()

    def set_width(self, width):
        require_tk("set_width", self)
        validate_width(width)
        self.widget.configure(width=width)

    def get_height(self):
        require_tk("get_height", self)
        return self.widget.winfo_height()

    def set_height(self, height):
        require_tk("set_height", self)
        validate_height(height)
        self.widget.configure(height=height)

    def get_background(self):
        require_tk("get_background", self)
        return self.widget.cget("background")

    def set_background(self, background):
        require_tk("set_background", self)
        validate_color(background)
        background = constants.COLORS.get(background, background)
        self.widget.configure(background=background)

    def focus(self):
        require_tk("focus", self)
        self.widget.focus_set()

    def destroy(self):
        require_tk("destroy", self)
        self.widget.wm_withdraw()
        self.widget.destroy()

    def hide(self):
        require_tk("hide", self)
        self.widget.wm_withdraw()

    def show(self):
        require_tk("show", self)
        self.widget.deiconify()

    def get_title(self):
        require_tk("get_title", self)
        return self.widget.wm_title()

    def set_title(self, title):
        require_tk("set_title", self)
        validate_title(title)
        self.widget.wm_title(title)

    def get_style(self):
        require_tk("get_style", self)
        return self.style

    def set_style(self, style, recursive=False):
        require_tk("set_style", self)
        validate_style(style)
        stylename = self.__class__.__name__.lower() + "style"
        self.widget.configure(**getattr(style, stylename).active)
        self.style = style
        if not recursive:
            return
        apply_style_recursively(self, style=style)

    @property
    def children(self):
        for child in hierarchy[self]:
            yield child


class Frame(Widget):
    def __init__(
                 self,
                 parent,
                 width=200,
                 height=200,
                 background=None
                ):
        validate_parent(parent)
        if width is not None:
            validate_width(width)
        if height is not None:
            validate_height(height)
        if background is not None:
            validate_color(background)
            background = constants.COLORS.get(background, background)
        super(Frame, self).__init__(
            parent=parent,
            wtype=tk.Frame,
            width=width,
            height=height,
            background=background
        )

    def get_width(self):
        require_tk("get_width", self)
        return self.widget.winfo_width()

    def set_width(self, width):
        require_tk("set_width", self)
        validate_width(width)
        self.widget.configure(width=width)

    def get_height(self):
        require_tk("get_height", self)
        return self.widget.winfo_height()

    def set_height(self, height):
        require_tk("set_height", self)
        validate_height(height)
        self.widget.configure(height=height)

    def get_background(self):
        require_tk("get_background", self)
        return self.widget.cget("background")

    def set_background(self, background):
        require_tk("set_background", self)
        validate_color(background)
        background = constants.COLORS.get(background, background)
        self.widget.configure(background=background)


class Text(Widget):
    def __init__(
                 self,
                 parent,
                 value="",
                 foreground=None,
                 background=None,
                 align="center"
                ):
        validate_parent(parent)
        if value is not None:
            validate_value(value)
        if foreground is not None:
            validate_color(foreground)
            background = constants.COLORS.get(background, background)
        if background is not None:
            validate_color(background)
            background = constants.COLORS.get(background, background)
        validate_align(align)
        super(Text, self).__init__(
            parent=parent,
            wtype=tk.Label,
            text=value,
            foreground=foreground,
            background=background,
            justify=align
        )

    def get_value(self):
        require_tk("get_value", self)
        return self.widget.cget("text")

    def set_value(self, value):
        require_tk("set_value", self)
        self.widget.configure(text=value)

    def get_foreground(self):
        require_tk("get_foreground", self)
        return self.widget.cget("foreground")

    def set_foreground(self, foreground):
        require_tk("set_foreground", self)
        validate_color(foreground)
        foreground = constants.COLORS.get(foreground, foreground)
        self.widget.configure(foreground=foreground)

    def get_background(self):
        require_tk("get_background", self)
        return self.widget.cget("background")

    def set_background(self, background):
        require_tk("set_background", self)
        validate_color(background)
        background = constants.COLORS.get(background, background)
        self.widget.configure(background=background)

    def get_align(self):
        require_tk("get_align", self)
        return self.widget.cget("justify")

    def set_align(self, align):
        require_tk("set_align", self)
        validate_align(align)
        self.widget.configure(justify=align)


class Entry(Widget):
    def __init__(
                 self,
                 parent,
                 value="",
                 foreground=None,
                 background=None,
                 align="left"
                ):
        validate_parent(parent)
        if value is not None:
            validate_value(value)
        if foreground is not None:
            validate_color(foreground)
            foreground = constants.COLORS.get(foreground, foreground)
        if background is not None:
            validate_color(background)
            background = constants.COLORS.get(background, background)
        if align is not None:
            validate_align(align)
        super(Entry, self).__init__(
            parent=parent,
            wtype=tk.Entry,
            foreground=foreground,
            background=background,
            justify=align
        )
        if value is not None:
            self.set_value(value=value)

    def get_value(self):
        require_tk("get_value", self)
        return self.widget.cget("text")

    def set_value(self, value):
        require_tk("set_value", self)
        validate_value(value)
        self.widget.configure(text=value)

    def get_foreground(self):
        require_tk("get_foreground", self)
        return self.widget.cget("foreground")

    def set_foreground(self, foreground):
        require_tk("set_foreground", self)
        validate_color(foreground)
        foreground = constants.COLORS.get(foreground, foreground)
        self.widget.configure(foreground=foreground)

    def get_background(self):
        require_tk("get_background", self)
        return self.widget.cget("background")

    def set_background(self, background):
        require_tk("set_background", self)
        validate_color(background)
        background = constants.COLORS.get(background, background)
        self.widget.configure(background=background)

    def get_align(self):
        require_tk("get_align", self)
        return self.widget.cget("justify")

    def set_align(self, align):
        require_tk("set_align", self)
        validate_align(align)
        self.widget.configure(justify=align)


class Button(Widget):
    def __init__(
                 self,
                 parent,
                 value="",
                 image=None,
                 foreground=None,
                 background=None,
                 align="center"
                ):
        validate_parent(parent)
        if value is not None:
            validate_value(value)
        image_path = image if image is not None else ""
        if image is not None:
            validate_image(image)
            image = load_photo_image(file=image)
        if foreground is not None:
            validate_color(foreground)
            foreground = constants.COLORS.get(foreground, foreground)
        if background is not None:
            validate_color(background)
            background = constants.COLORS.get(background, background)
        if align is not None:
            validate_align(align)
        super(Button, self).__init__(
            parent=parent,
            wtype=tk.Button,
            text=value,
            image=image,
            image_path=image_path,
            foreground=foreground,
            background=background,
            justify=align
        )

    def get_value(self):
        require_tk("get_value", self)
        return self.widget.cget("text")

    def set_value(self, value):
        require_tk("set_value", self)
        validate_value(value)
        self.widget.configure(text=value)

    def get_foreground(self):
        require_tk("get_foreground", self)
        return self.widget.cget("foreground")

    def set_foreground(self, foreground):
        require_tk("set_foreground", self)
        validate_color(foreground)
        foreground = constants.COLORS.get(foreground, foreground)
        self.widget.configure(foreground=foreground)

    def get_background(self):
        require_tk("get_background", self)
        return self.widget.cget("background")

    def set_background(self, background):
        require_tk("set_background", self)
        validate_color(background)
        background = constants.COLORS.get(background, background)
        self.widget.configure(background=background)

    def get_image(self):
        require_tk("get_image", self)
        return self.widget.__image_path

    def set_image(self, image):
        require_tk("set_image", self)
        validate_image(image)
        image_path = image
        image = load_photo_image(file=image)
        self.widget.configure(image=image)
        self.widget.__image_path = image_path
        self.widget.__image = image

    def get_align(self):
        require_tk("get_align", self)
        return self.widget.cget("justify")

    def set_align(self, align):
        require_tk("set_align", self)
        validate_align(align)
        self.widget.configure(justify=align)


class Image(Widget):
    def __init__(
                 self,
                 parent,
                 file
                ):
        validate_image(file)
        image = load_photo_image(file=file)
        super(Image, self).__init__(
            parent=parent,
            wtype=tk.label,
            image=image
        )

    def get_width(self):
        require_tk("get_width", self)
        return self.widget.__image.width()

    def get_height(self):
        require_tk("get_height", self)
        return self.widget.__image.height()

    def get_image(self):
        require_tk("get_image", self)
        return self.widget.__image_path

    def set_image(self, image):
        require_tk("set_image", self)
        validate_image(image)
        image_path = image
        image = load_photo_image(file=image)
        self.widget.configure(image=image)
        self.widget.__image_path = image_path
        self.widget.__image = image
