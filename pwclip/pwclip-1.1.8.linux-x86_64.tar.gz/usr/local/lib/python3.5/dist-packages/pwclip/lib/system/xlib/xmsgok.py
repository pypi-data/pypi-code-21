#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
#
# This file is free software by d0n <d0n@janeiskla.de>
#
# You can redistribute it and/or modify it under the terms of the GNU -
# Lesser General Public License as published by the Free Software Foundation
#
# This is distributed in the hope that it will be useful somehow.
#
# !WITHOUT ANY WARRANTY!
#
# Without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.

try:
	from tkinter import StringVar, Button, Entry, Frame, Label, Tk
except ImportError:
	from Tkinter import StringVar, Button, Entry, Frame, Label, Tk

def xmsgok(message="press any key to continue"):
	"""gui representing function"""
	class XMessage(Frame):
		"""password clipping class for tkinter.Frame"""
		def __init__(self, master):
			Frame.__init__(self, master)
			self.pack()
			self.inputwindow()
		def _exit(self, _=None):
			"""just exit (for ESC mainly)"""
			self.quit()
		def inputwindow(self):
			"""password input window creator"""
			self.lbl = Label(self, text=message)
			self.lbl.pack()
			self.bind("<Key>", self._exit)
			self.pack()
			self.focus_set()
			self.ok = Button(self)
			self.ok["text"] = "ok"
			self.ok["command"] = self._exit
			self.ok.pack()
	# instanciate Tk and create window
	root = Tk()
	xms = XMessage(root)
	xms.lift()
	xms.mainloop()
	root.destroy()
