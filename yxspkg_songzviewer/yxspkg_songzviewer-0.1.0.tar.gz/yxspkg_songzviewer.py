#!/usr/bin/env python3
from PyQt5.QtCore import  QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import (QApplication,  QLabel,QWidget,QMessageBox)

import imageio
import sys

__version__='0.1.0'
__author__='Blacksong'

def ndarry2qimage(npimg): #ndarry图片转化为qimage图片
    if npimg.dtype!='uint8':
        npimg=npimg.astype('uint8')
    shape=npimg.shape
    if len(shape)==3 and shape[2]==4:
        return QImage(npimg.tobytes(),shape[1],shape[0],shape[1]*shape[2],QImage.Format_RGBA8888)
    if len(shape)==2:
        npimg=stack((npimg,npimg,npimg),2)
        shape=npimg.shape
    s=QImage(npimg.tobytes(),shape[1],shape[0],shape[1]*shape[2],QImage.Format_RGB888)
    return s

class GifPreview(QWidget):   #预览gif

    def __init__(self,s='SongZ Viewer',name=None):
        super().__init__()
        
        self.label=QLabel(self)
        self.label.setScaledContents(True)
        self.setWindowTitle(s)
        self.show()
        self.open_file(name)
    def open_file(self,name):
        if name is None:return
        if name[-3:].lower()=='gif':
            self.gif(name)
        else:
            self.image(name)
    def gif(self,name):
        x=imageio.get_reader(name,'ffmpeg')
        meta=x.get_meta_data()
        fps=meta['fps']
        size=meta['size']
        jpgs=[i for i in x]
        self.preview((jpgs,fps,(size[1],size[0])))
    def image(self,name):
        print('name')
        s=imageio.imread(name)
        shape=s.shape 
        self.preview(([s],0.0001,shape[:2]))
    def update_image(self):
        if self.nn>=len(self.jpgs):self.nn=0
        x=self.jpgs[self.nn]
        qimg=ndarry2qimage(x)
        self.label.setPixmap(QPixmap.fromImage(qimg))
        self.nn+=1

    def preview(self,parent):
        self.nn=0
        self.jpgs, self.fps ,shape  = parent
        print(shape)
        m=max(shape)
        print(m)
        t=max(1,m/500)
        shape=shape[0]/t,shape[1]/t
        print(shape)
        self.label.setGeometry(10,10,shape[1],shape[0])
        self.resize(shape[1]+20,shape[0]+20)
        self.timer=QTimer(self)
        self.timer.timeout.connect(self.update_image)
        t=int(1/self.fps*1000)
        self.update_image()
        self.timer.start(t)

def main():
    
    if len(sys.argv)==2:
        name=sys.argv[1]
    else:
        name=None
    app = QApplication(sys.argv)
    gifMaker = GifPreview(name=name)
    sys.exit(app.exec_())
if __name__ == '__main__':
    main()