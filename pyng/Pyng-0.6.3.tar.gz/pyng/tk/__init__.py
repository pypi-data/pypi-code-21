#!/usr/bin/python
"""
    __init__.py                      Nat Goodspeed
    Copyright (C) 2017               Nat Goodspeed

NRG 2017-10-26
"""

import os
import __main__                         # for filename of main script

BULLET = u"\u2022"                      # U+2022 is "bullet"

try:
    WINDOW_TITLE = os.path.basename(__main__.__file__)
except AttributeError:
    WINDOW_TITLE = "pyng/tk"

# from http://stackoverflow.com/questions/3352918/how-to-center-a-window-on-the-screen-in-tkinter
def center(win):
    """generic center function for any Tkinter window"""
    # do this before retrieving any geometry to ensure accurate values
    win.update_idletasks()
    # width of client area
    width = win.winfo_width()
    # winfo_rootx() is client area's left x; winfo_x() is outer frame's left x
    frm_width = win.winfo_rootx() - win.winfo_x()
    # outer frame overall width is client width plus two frame widths
    win_width =  width + 2 * frm_width
    # height of client area
    height = win.winfo_height()
    # winfo_rooty() is client area's top y; winfo_y() is outer frame's top y
    # y is measured from top, therefore winfo_rooty() > winfo_y()
    titlebar_height = win.winfo_rooty() - win.winfo_y()
    # outer frame overall height = client height plus titlebar plus frame width
    win_height = height + titlebar_height + frm_width
    x = (win.winfo_screenwidth() - win_width) // 2
    y = (win.winfo_screenheight() - win_height) // 2
    win.geometry('%sx%s+%s+%s' % (width, height, x, y))
    ## if win.attributes('-alpha') == 0:
    ##     win.attributes('-alpha', 1.0)
    win.deiconify()
