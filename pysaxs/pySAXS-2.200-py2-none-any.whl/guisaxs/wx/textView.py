"""
project : pySAXS
description : function to print a message from a txt file to a dialog box
authors : Olivier Tache
Last changes :
    24-07-2012 OT
    13-03-2007 OT

"""
import wx
import  wx.lib.dialogs
import os
def ViewMessage(file,title="test"):
    f = open(file, "r")
    msg = f.read()
    f.close()
    msgu=unicode(msg,errors='replace')
    dlg = wx.lib.dialogs.ScrolledMessageDialog(None, msgu, title)
    dlg.ShowModal()

#------------------------------------------
if __name__=='__main__':
    import pySAXS
    app=wx.PySimpleApp()
    file=os.path.dirname(pySAXS.__file__)+os.sep+'LICENSE.txt'
    ViewMessage(file)
    app.MainLoop()
