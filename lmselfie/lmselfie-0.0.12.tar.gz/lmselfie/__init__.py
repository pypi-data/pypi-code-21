from tkinter import *
from gpiozero import Button as GPIOButton, LED as GPIOLed
from sacarfoto import *
from armartira import *

def do_something():
    message.set("Button was pressed")

def do_photobooth():
    message.set("iniciando tira de fotos")
    fotos = tomarFotosPiCamera(camera, 21)
    procesarFotos(fotos)
    message.set("LISTO")


camera = PiCamera()

root = Tk()
root.attributes("-fullscreen", True)
message = StringVar()
message = "Hello World"

w = Label(master, textvariable=message)
w.pack()

b = Button(text="Kill Me", command=sys.exit)
b.pack()

Button(text="otro boton", command=do_photobooth).pack()

btnFisico1 = GPIOButton(16)
btnFisico2 = GPIOButton(20)
btnFisico1.when_pressed = do_photobooth
btnFisico2.when_pressed = do_something

root.mainloop()
