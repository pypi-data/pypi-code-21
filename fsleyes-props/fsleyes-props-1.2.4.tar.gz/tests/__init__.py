#!/usr/bin/env python
#
# __init__.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#

from __future__ import print_function

import gc
import time

import wx

from  fsl.utils.platform import platform as fslplatform


def run_with_wx(func, *args, **kwargs):

    gc.collect()

    propagateRaise = kwargs.pop('propagateRaise', True)
    startingDelay  = kwargs.pop('startingDelay',  500)
    finishingDelay = kwargs.pop('finishingDelay', 500)
    callAfterApp   = kwargs.pop('callAfterApp',   None)

    result = [None]
    raised = [None]

    app    = [wx.App()]
    frame  = wx.Frame(None)
    panel  = wx.Panel(frame)
    sizer  = wx.BoxSizer(wx.VERTICAL)
    sizer.Add(panel, flag=wx.EXPAND, proportion=1)
    frame.SetSizer(sizer)
    frame.Layout()

    if callAfterApp is not None:
        callAfterApp()

    def wrap():

        try:
            if func is not None:
                result[0] = func(panel, *args, **kwargs)

        except Exception as e:
            print(e)
            raised[0] = e

        finally:
            def finish():
                frame.Destroy()
                app[0].ExitMainLoop()

            wx.CallLater(finishingDelay, finish)

    frame.Show()

    wx.CallLater(startingDelay, wrap)

    app[0].MainLoop()

    if raised[0] and propagateRaise:
        raise raised[0]

    del app[0]
    return result[0]


def addall(parent, widgets):
    sizer = wx.BoxSizer(wx.VERTICAL)
    parent.SetSizer(sizer)
    for w in widgets:
        sizer.Add(w, flag=wx.EXPAND, proportion=1)
    parent.Layout()
    parent.Refresh()
    realYield()



# Under GTK, a single call to
# yield just doesn't cut it
def realYield(centis=10):
    for i in range(int(centis)):
        wx.YieldIfNeeded()
        time.sleep(0.01)


# stype:
#   0 for single click
#   1 for double click
#   2 for separatemouse down/up events
def simclick(sim, target, btn=wx.MOUSE_BTN_LEFT, pos=None, stype=0):

    w, h = target.GetClientSize().Get()
    x, y = target.GetScreenPosition()

    if pos is None:
        pos = [0.5, 0.5]

    x += w * pos[0]
    y += h * pos[1]

    sim.MouseMove(x, y)
    wx.Yield()
    if   stype == 0: sim.MouseClick(btn)
    elif stype == 1: sim.MouseDblClick(btn)
    else:
        sim.MouseDown(btn)
        sim.MouseUp(btn)
    realYield()



def simtext(sim, target, text, enter=True):
    target.SetFocus()
    target.SetValue(text)

    # KeyDown doesn't seem to work
    # under docker/GTK so we have
    # to hack
    if enter and fslplatform.wxPlatform == fslplatform.WX_GTK:
        parent = target.GetParent()
        if type(parent).__name__ == 'FloatSpinCtrl':
            parent._FloatSpinCtrl__onText(None)
        else:
            sim.KeyDown(wx.WXK_RETURN)
    elif enter:
        sim.KeyDown(wx.WXK_RETURN)
    realYield()


def simkey(sim, target, key, down=True, up=False):
    if target is not None: target.SetFocus()
    if down:               sim.KeyDown(key)
    if up:                 sim.KeyUp(key)
    realYield()
