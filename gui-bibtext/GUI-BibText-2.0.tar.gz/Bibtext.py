#!/usr/bin/env python

"""
Code for generating the bibtex key from Google Scholar for the list of papers, whose names are stored
    in the excel sheet.


Author: Himanshu Mittal (himanshu.mittal224@gmail.com)
Referred: https://github.com/venthur/gscholar
"""
try:
	# Windows
    import tkinter as tkin
except ImportError:
    # Mac
    import Tkinter as tkin

import extract

def fetchKey():
	global Entry1
	extract.extractr(Entry1.get())

def Bibtex():
	global Entry1

	mainwindow = tkin.Tk()
	mainwindow.title('BibTex Key Extractor')

	tkin.Label(mainwindow,text = "Path To Excel File:").grid(row=0)

	Entry1 = tkin.Entry(mainwindow)

	Entry1.grid(row=0,column=1)

	Entry1.focus()

	tkin.Button(mainwindow,text = 'Fetch',command = fetchKey).grid(row=3, column =0)
	tkin.Button(mainwindow, text='Close', command=mainwindow.destroy).grid(row=3, column =1)

	mainwindow.mainloop()