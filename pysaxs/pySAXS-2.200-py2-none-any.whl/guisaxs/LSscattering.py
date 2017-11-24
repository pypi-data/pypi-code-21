#10-11-2009 OT : Replaced LsScattering by GuiSAXS.py
from GuiSAXS import *
if __name__== '__main__':
    app = wx.App()
    frame = GuiSAXS(None, 1)
    app.MainLoop()