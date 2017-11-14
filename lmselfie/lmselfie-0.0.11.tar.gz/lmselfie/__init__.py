from tkinter import *

root = Tk()
root.attributes("-fullscreen", True)
w = Label(root, text="Hello World")
w.pack()
b = Button(text="Kill Me", command=sys.exit)
b.pack()

Button(text="otro boton", command=sys.exit).pack()
root.mainloop()
