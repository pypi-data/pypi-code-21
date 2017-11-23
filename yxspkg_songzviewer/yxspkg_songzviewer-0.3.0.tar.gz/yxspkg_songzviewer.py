#!/usr/bin/env python3
from PyQt5.QtCore import  QTimer,Qt
from PyQt5.QtGui import QImage, QPixmap,QMovie
from PyQt5.QtWidgets import (QApplication,  QLabel,QWidget,QMessageBox,QPushButton)
import imageio
import sys
from os import path
import os

__version__='0.3.0'
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
class YCloseButton(QPushButton):
    def __init__(self,*d):
        super().__init__(*d)
        self.setStyleSheet("border:none;")
class YTitleLabel(QLabel):
    def __init__(self,*d):
        super().__init__(*d)
        self.parent=d[0]
    def mousePressEvent(self,e):
        self.xt,self.yt=self.parent.x(),self.parent.y() #窗口最原始的位置
        self.x0,self.y0=self.xt+e.x(),self.yt+e.y()

    def mouseMoveEvent(self,e):
        x,y=self.parent.x()+e.x(),self.parent.y()+e.y()
        dx,dy=x-self.x0,y-self.y0
        self.parent.move(self.xt+dx,self.yt+dy)
    def mouseDoubleClickEvent(self,e):
        if self.parent.isMaximized():
            self.parent.showNormal()
        else:
            self.parent.showMaximized()

class YToolButtons(QWidget):
    def __init__(self,*d):
        super().__init__(*d)
        self.parent=d[0]
        self.background=QLabel(self)
        self.background.setStyleSheet('QWidget{background-color:rgba(%d,%d,%d,%d)}' % self.parent.background_color)
    def resizeEvent(self,e):
        self.background.resize(e.size())

class NextPage(QLabel): #翻页按钮
    def __init__(self,*d):
        super().__init__(*d)
        self.setStyleSheet('QWidget{background-color:rgba(0,0,0,100)}')
        self.clicked_connect_func=lambda a:None
    def clicked_connect(self,func):
        self.clicked_connect_func=func
    def mousePressEvent(self,e):
        self.clicked_connect_func(e)

class GifPreview(QWidget):   #预览gif
    gif_types=('.gif',)
    image_types=('.jpg','.jpeg','.ico','.bmp','.png','.tiff','.icns')
    def __init__(self,s='SongZ Viewer',name=None):
        super().__init__()
        self.border=0 #边界宽度
        self.label=QLabel(self)
        self.label.setScaledContents(True)
        self.background_color=(255,255,255,255)
        self.setStyleSheet('QWidget{background-color:rgba(%d,%d,%d,%d)}' % self.background_color)
        self.setWindowFlags(Qt.CustomizeWindowHint)
        self.setMinimumSize(200,100)
        self.title_height=26
        self.bottom_height=50
        self.nextbutton_size=35
        self.first_window=True
        self.CloseButton=YCloseButton(self)
        self.CloseButton.setText('X')
        self.CloseButton.resize(self.title_height,self.title_height)
        self.CloseButton.clicked.connect(self.close)
        #标题栏
        self.TitleLabel=YTitleLabel(self)
        self.TitleLabel.move(0,0)
        #工具栏
        self.ToolButtons=YToolButtons(self)
        #翻页按钮
        self.nextbutton=NextPage(self)
        self.nextbutton.resize(self.nextbutton_size,self.nextbutton_size)
        self.nextbutton.clicked_connect(self.next_image)
        self.prebutton=NextPage(self)
        self.prebutton.resize(self.nextbutton_size,self.nextbutton_size)
        self.prebutton.clicked_connect(self.previous_image)


        self.factor=1
        self.factor_max=3
        self.factor_min=0.1
        self.dir_images=None
        self.dir_images_n=None
        self.source_name=name
        self.open_file(name)
    def get_images(self):
        dname=path.dirname(path.abspath(self.source_name))
        print(dname)
        # t=os.listdir(dname)
        t=[path.join(dname,i) for i in os.listdir(dname) if path.splitext(i)[-1].lower() in self.gif_types or path.splitext(i)[-1].lower() in self.image_types]
        return t
    def mouseDoubleClickEvent(self,e):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()
    def next_image(self,e):
        if self.dir_images is None:
            self.dir_images=self.get_images()
            self.dir_images_n=self.dir_images.index(path.abspath(self.source_name))
        self.dir_images_n+=1
        if self.dir_images_n>=len(self.dir_images):
            self.dir_images_n=0
        self.open_file(self.dir_images[self.dir_images_n])
    def previous_image(self,e):
        print('previous image')
    def open_file(self,name):
        if name is None:
            self.show()
            return
        if path.splitext(name)[-1].lower() in self.gif_types:
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
        title_height=self.title_height
        bottom_height=self.bottom_height
        w,h=self.width(),self.height()
        self.CloseButton.move(w-title_height,0)
        self.TitleLabel.resize(w-self.title_height,self.title_height)
        self.ToolButtons.setGeometry(0,h-bottom_height,w,bottom_height )
        h-=title_height+bottom_height
        w_label,h_label=self.label.width(),self.label.height()
        self.label.move((w-w_label)/2,title_height+(h-h_label)/2)
        self.nextbutton.move(w-15-self.nextbutton_size,h/2)
        self.prebutton.move(15,h/2)
    def preview(self,parent):
        self.nn=0
        self.jpgs, self.fps ,shape  = parent
        m=max(shape)
        t=max(1,m/500)
        shape=shape[0]/t,shape[1]/t
        self.factor=1/t
        self.label.resize(shape[1],shape[0])
        if self.first_window:
            self.resize(shape[1]+self.border*2,shape[0]+self.border*2+self.title_height+self.bottom_height)
            self.first_window=False
        self.setPosition()
        self.update_image()
        if self.fps != 0:
            self.timer=QTimer(self)
            self.timer.timeout.connect(self.update_image)
            t=int(1/self.fps*1000)
            self.timer.start(t)
        self.show()

def main():
    
    if len(sys.argv)==2:
        name=sys.argv[1]
    else:
        name=None
    app = QApplication(sys.argv)
    name='sdfe.png'
    gifMaker = GifPreview(name=name)
    sys.exit(app.exec_())
if __name__ == '__main__':
    main()