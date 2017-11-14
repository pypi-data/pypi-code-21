#!/home/km/mytestenv/bin/python3

from tkinter import *
from tkinter import ttk

from numtogreek import n2g

root = Tk()
root.title("Numbers")

v = StringVar()
v1 = IntVar()
def convnum(event):
    s = ''
    try:
        if v1.get() == 1:
            
            s = n2g.n2g(ent.get())
            v.set(s.upper())
        elif v1.get() == 2:
            s = n2g.n2g(ent.get())
            v.set(s.lower())
        else:
            s = n2g.n2g(ent.get())
            v.set(s.title())
    except:
        v.set('Δώστε αριθμό!!')
        
lbl = ttk.Label(root, text='Δώστε αριθμό:')
lbl.grid(column=0, row=0)
lbl1 = ttk.Label(root, anchor=E, textvariable=v, wraplength=200)
lbl1.grid(column=0, row=1, columnspan=2)
ent = ttk.Entry(root)
ent.grid(column=1, row=0)
ent.bind('<Return>', convnum)

##ent.insert(0, 'Εδώ γράψτε ακέραιο αριθμό')
lblfrm = ttk.Labelframe(root, relief=RIDGE, labelanchor=SE, text='Πεζά - Κεφαλαία')
lblfrm.grid(column=2, row=0, rowspan=2)
rbutton1 = ttk.Radiobutton(lblfrm, text="ΚΕΦΑΛΑΙΑ", variable=v1, value=1, command=lambda:convnum(0))
rbutton1.grid(column=0, row=0, sticky=W)
v1.set(1)
rbutton2 = ttk.Radiobutton(lblfrm, text="πεζά", variable=v1, value=2, command=lambda:convnum(0))
rbutton2.grid(column=0, row=1, sticky=W)
rbutton3 = ttk.Radiobutton(lblfrm, text="Τίτλος", variable=v1, value=3, command=lambda:convnum(0))
rbutton3.grid(column=0, row=2, sticky=W)

v.set('')
for child in root.winfo_children():
    child.grid_configure(pady=5, padx=5)
ent.focus_set()
root.mainloop()
