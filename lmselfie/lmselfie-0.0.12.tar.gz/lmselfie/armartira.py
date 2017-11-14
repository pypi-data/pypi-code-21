import datetime
import time
from PIL import Image
import numpy as np
import shutil
import subprocess
import os

def copiarFotos(fotos, tira):
    #copiar al pendrive
    try:
        usbnamebytes = subprocess.check_output(['ls', '/media/pi'])
        usbname = usbnamebytes.decode("utf-8")[:-1]
        destinationFotos = '/media/pi/'+usbname+'/'
        destinationTiras = '/media/pi/'+usbname+'/'

        shutil.copy2(fotos[0], destinationFotos+fotos[0])
        shutil.copy2(fotos[1], destinationFotos+fotos[1])
        shutil.copy2(fotos[2], destinationFotos+fotos[2])
        shutil.copy2(tira, destinationTiras+tira)

        os.remove(fotos[0])
        os.remove(fotos[1])
        os.remove(fotos[2])
        os.remove(tira)
    except shutil.Error as e:
        print("Error: %s" % e)
    except IOError as e:
        print("Error: %s" % e.strerror)


def procesarFotos(listaFotos):
    imgs = [ Image.open(i) for i in listaFotos ]
    # pick the image which is the smallest, and resize the others to match it (can be arbitrary image shape here)
    min_shape = sorted( [(np.sum(i.size), i.size ) for i in imgs])[0][1]
    # for a vertical stacking it is simple: use vstack
    imgs_comb = np.vstack( (np.asarray( i.resize(min_shape) ) for i in imgs ) )
    imgs_comb = Image.fromarray( imgs_comb)

    sourceTira = 'fotoTira_'+datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")+'.jpg'
    imgs_comb.save( sourceTira )

    #enviar a imprimir
    copiarFotos(listaFotos, sourceTira)



#date = datetime.datetime.now().strftime("%m_%d_%Y_%H_%M_%S")
#camera.capture("/home/pi/photobooth/"+ date + ".jpg")
