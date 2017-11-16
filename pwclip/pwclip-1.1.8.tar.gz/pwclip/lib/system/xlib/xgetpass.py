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
"""x input window module"""
try:
	from tkinter import StringVar, Button, Entry, Frame, Label, Tk
except ImportError:
	from Tkinter import StringVar, Button, Entry, Frame, Label, Tk

def xgetpass(message="input will not be displayed"):
	"""gui representing function"""
	class XInput(Frame):
		"""class to capture user input for x environments"""
		inp = None
		def __init__(self, master):
			"""xinput init function"""
			Frame.__init__(self, master)
			self.pack()
			self.inputwindow()
		def _enterexit(self, _=None):
			"""exit by saving input"""
			self.inp = self.input.get()
			self.quit()
		def _exit(self, _=None):
			"""just exit (for ESC mainly)"""
			self.quit()
		def inputwindow(self):
			"""input window creator"""
			self.lbl = Label(self, text=message)
			self.lbl.pack()
			self.entry = Entry(self, show="*")
			self.entry.bind("<Return>", self._enterexit)
			self.entry.bind("<Control-c>", self._exit)
			self.entry.bind("<Escape>", self._exit)
			self.entry.pack()
			self.entry.focus_set()
			self.input = StringVar()
			self.entry["textvariable"] = self.input
			self.ok = Button(self)
			self.ok["text"] = "ok"
			self.ok["command"] = self._enterexit
			self.ok.pack(side="left")
			self.cl = Button(self)
			self.cl["text"] = "cancel"
			self.cl["command"] = self.quit
			self.cl.pack(side="right")
	# instanciate Tk and create window
	root = Tk()
	root.after(1, lambda: root.focus_force())
	win = XInput(root)
	win.lift()
	win.mainloop()
	root.destroy()
	return win.inp



if __name__ == '__main__':
	exit(1)
