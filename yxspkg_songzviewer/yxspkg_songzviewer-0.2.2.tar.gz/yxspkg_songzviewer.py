#!/usr/bin/env python3
from PyQt5.QtCore import  QTimer
from PyQt5.QtGui import QImage, QPixmap,QMovie
from PyQt5.QtWidgets import (QApplication,  QLabel,QWidget,QMessageBox)

import imageio
import sys

__version__='0.2.2'
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
        self.border=0 #边界宽度
        self.label=QLabel(self)
        self.label.setScaledContents(True)
        self.label.setMinimumSize(400,400)
        self.setWindowTitle(s)
        self.factor=1
        
        self.factor_max=3
        self.factor_min=0.1
        self.open_file(name)
    def open_file(self,name):
        if name is None:
            self.show()
            return
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
    def resizeEvent(self,e):
        self.setPosition()
    def wheelEvent(self,e):
        if e.angleDelta().y()>0:
            factor=1.05
        else:
            factor=0.95
        self.scaleImage(factor)
    def scaleImage(self,factor):
        w,h=self.label.pixmap().size().width(),self.label.pixmap().size().height()
        tt=self.factor*factor
        if tt>self.factor_max or tt<self.factor_min:return
        self.factor*=factor
        self.label.resize(w*self.factor,h*self.factor)
        self.setPosition()
    def setPosition(self):
        w,h=self.width(),self.height()
        w_label,h_label=self.label.width(),self.label.height()
        self.label.move((w-w_label)/2,(h-h_label)/2)
    def preview(self,parent):
        self.nn=0
        self.jpgs, self.fps ,shape  = parent
        m=max(shape)
        t=max(1,m/500)
        shape=shape[0]/t,shape[1]/t
        self.factor=1/t
        self.label.resize(shape[1],shape[0])
        self.resize(shape[1]+self.border*2,shape[0]+self.border*2)
        self.setPosition()
        self.timer=QTimer(self)
        self.timer.timeout.connect(self.update_image)
        t=int(1/self.fps*1000)
        self.update_image()
        self.timer.start(t)
        self.show()

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