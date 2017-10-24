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
"""x yes/no message/answer window module"""

try:
	from tkinter import Button, Frame, Label, Tk
except ImportError:
	from Tkinter import Button, Frame, Label, Tk

def xyesno(message="do you accept that?"):
	"""gui representing function"""
	class XYesNo(Frame):
		"""password clipping class for tkinter.Frame"""
		yesno = False
		def __init__(self, master):
			Frame.__init__(self, master)
			self.pack()
			self.inputwindow()
		def _enterexit(self, _=None):
			"""exit by saving challenge-response for input"""
			self.yesno = True
			self.quit()
		def _exit(self, _=None):
			"""just exit (for ESC mainly)"""
			self.quit()
		def inputwindow(self):
			"""password input window creator"""
			self.lbl = Label(self, text=message)
			self.lbl.pack()
			self.bind("<Return>", self._enterexit)
			self.bind("<Escape>", self._exit)
			self.pack()
			self.focus_set()
			self.ok = Button(self)
			self.ok["text"] = "ok"
			self.ok["command"] = self._enterexit
			self.ok.pack(side="left")
			self.cl = Button(self)
			self.cl["text"] = "cancel"
			self.cl["command"] = self._exit
			self.cl.pack(side="right")
	# instanciate Tk and create window
	root = Tk()
	root.after(1, lambda: root.focus_force())
	xyn = XYesNo(root)
	xyn.lift()
	xyn.mainloop()
	root.destroy()
	return xyn.yesno



if __name__ == '__main__':
	exit(1)
