from picamera import PiCamera
import datetime
import time
from time import sleep
from gpiozero import LED as GPIOLed

def parpadearLed(pinIO):
    if pinIO>0:
        led = GPIOLed(pinIO)
        for x in range(3):
            led.on()
            sleep(0.25)
            led.off()
            sleep(0.25)

def tomarFotosPiCamera(camera, pinLed):
    #camera.resolution = (2592, 1944)
    camera.start_preview()
    myList=[]
    for i in range(3):
        sleep(2)
        parpadearLed(pinLed)
        tiempo = 'foto_'+datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")+'.jpg'
        myList.append(tiempo)
        camera.capture(tiempo)
    camera.stop_preview()
    return myList
