#!/usr/bin/env python3
from PyQt5.QtCore import  QTimer,Qt,QSize,QPoint,QEvent
from PyQt5.QtGui import QImage, QPixmap,QPainter,QFont,QColor,QPen,QCursor
from PyQt5.QtWidgets import (QApplication,  QLabel,QWidget,QMessageBox,QDesktopWidget)
from numpy import stack
import imageio
import sys
from os import path
import os
import time
imread=imageio.imread
__version__='0.4.4'
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

class YTitleLabel(QLabel):
    def __init__(self,*d):
        super().__init__(*d)
        self.parent=d[0]
    def mousePressEvent(self,e):
        if self.parent.resizeWindow:
            self.parent.mousePressEvent(e)
            return
        self.xt,self.yt=self.parent.x(),self.parent.y() #窗口最原始的位置
        self.x0,self.y0=self.xt+e.x(),self.yt+e.y()

    def mouseMoveEvent(self,e):
        if self.parent.resizeWindow:
            self.parent.mouseMoveEvent(e)
            return
        x,y=self.parent.x()+e.x(),self.parent.y()+e.y()
        dx,dy=x-self.x0,y-self.y0
        self.parent.move(self.xt+dx,self.yt+dy)
    def mouseDoubleClickEvent(self,e):
        if self.parent.isMaximized():
            self.parent.showNormal()
        else:
            self.parent.showMaximized()
class YDesignButton(QLabel):
    position_dict={'center':Qt.AlignCenter,'left':Qt.AlignLeft,'hcenter':Qt.AlignHCenter,'vcenter':Qt.AlignVCenter,'justify':Qt.AlignJustify}
    def __init__(self,parent):
        super().__init__(parent)
        self.parent=parent
        self.clicked_connect_func=lambda :None
        self.setScaledContents(True)
        self.normal_qimg=None 
        self.focus_qimg=None
    def setNormalQimg(self,lines,color_background,color_text,img_size,width_pen=4):
        self.normal_qimg=self.getDrawLine(lines,color_background,color_text,img_size,width_pen)
        self.setPixmap(self.normal_qimg)
        if self.focus_qimg is None:
            self.focus_qimg = self.normal_qimg
    def setFocusQimg(self,lines,color_background,color_text,img_size,width_pen=4):
        self.focus_qimg=self.getDrawLine(lines,color_background,color_text,img_size,width_pen)
    def getDrawLine(self,lines,color_background,color_text,img_size,width_pen=4):
        qp=QPainter()
        img=QImage(img_size[0],img_size[1],QImage.Format_RGBA8888)
        img.fill(QColor(*color_background))
        qp.begin(img)
        qp.setPen(QPen(QColor(*color_text),width_pen,Qt.SolidLine))
 
        for i,j,m,n in lines:
            qp.drawLine(QPoint(i,j),QPoint(m,n))
        qp.end()
        qimg=QPixmap.fromImage(img)
        return qimg

    def mousePressEvent(self,e):
        self.clicked_connect_func()
    def enterEvent(self,e):
        self.setPixmap(self.focus_qimg)
    def leaveEvent(self,e):
        self.setPixmap(self.normal_qimg)

class NextPage(YDesignButton): #翻页按钮
    def __init__(self,*d):
        super().__init__(*d)
        self.clicked_connect_func=lambda a:None
        self.setStyleSheet('QWidget{background-color:rgba(0,0,0,0)}' )
        l=[(10,50,70,50),(50,10,90,50),(90,50,50,90)]
        self.setNormalQimg(l,(0,0,0,0),(255,255,255,0),(100,100),10)
        self.setFocusQimg(l,(0,0,0,0),(255,255,255,0),(100,100),15)
    def clicked_connect(self,func):
        self.clicked_connect_func=func
    def mousePressEvent(self,e):
        self.clicked_connect_func(e)

class PrePage(YDesignButton): #翻页按钮
    def __init__(self,*d):
        super().__init__(*d)
        self.setStyleSheet('QWidget{background-color:rgba(0,0,0,0)}' )
        self.clicked_connect_func=lambda a:None
        l=[(30,50,90,50),(50,10,10,50),(50,90,10,50)]
        self.setNormalQimg(l,(0,0,0,0),(255,255,255,0),(100,100),10)
        self.setFocusQimg(l,(0,0,0,0),(255,255,255,0),(100,100),15)
    def clicked_connect(self,func):
        self.clicked_connect_func=func
    def mousePressEvent(self,e):
        self.clicked_connect_func(e)
class BorderLine(QLabel):
    def __init__(self,*d):
        super().__init__(*d)
        self.setStyleSheet('QWidget{background-color:rgba(0,0,0,100)}')
class YViewerLabel(QLabel):
    def __init__(self,*d):
        super().__init__(*d)
        self.parent=d[0]
    def mousePressEvent(self,e):

        if self.parent.resizeWindow:
            self.parent.mousePressEvent(e)
            return
        
        self.xt,self.yt=self.x(),self.y() #图片
        self.x0,self.y0=self.xt+e.x(),self.yt+e.y()

    def mouseMoveEvent(self,e):
        if self.parent.resizeWindow:
            self.parent.mouseMoveEvent(e)
            return
        x,y=self.x()+e.x(),self.y()+e.y()
        dx,dy=x-self.x0,y-self.y0
        self.move(self.xt+dx,self.yt+dy)
    def mouseDoubleClickEvent(self,e):
        if e.button()==Qt.RightButton:
            self.parent.setAutoplay()
            return
        if self.parent.isMaximized():
            self.parent.showNormal()
        else:
            self.parent.showMaximized()
class GifPreview(QWidget):   #预览gif
    gif_types=('.gif',)
    image_types=('.jpg','.jpeg','.ico','.bmp','.png','.tiff','.icns')
    def __init__(self,s='SongZ Viewer',name=None):
        super().__init__()
        self.timer=None
        self.autoplay=False
        self.autoplay_interval=1000
        self.border=0 #边界宽度
        self.label=YViewerLabel(self)
        self.label.setScaledContents(True)
        self.background_color=(255,255,255,255)
        self.setStyleSheet('QWidget{background-color:rgba(%d,%d,%d,%d)}' % self.background_color)
        self.setWindowFlags(Qt.FramelessWindowHint)#FramelessWindowHint
        self.setMinimumSize(200,100)
        self.minimumSize_window=200,100
        self.title_height=26
        self.bottom_height=0
        
        self.first_window=True
        self.CloseButton=YDesignButton(self)
        self.CloseButton.setNormalQimg([(30,30,70,70),(30,70,70,30)],(0,0,0,0),(0,0,0,0),(100,100),4)
        self.CloseButton.setFocusQimg([(30,30,70,70),(30,70,70,30)],(255,0,0,255),(255,255,255),(100,100),4)
        self.CloseButton.setStyleSheet('QWidget{background-color:rgba(0,0,0,0)}' )
        g=QDesktopWidget().availableGeometry()
        self.max_image_height=g.height()
        self.nextbutton_size=(50,self.max_image_height)


        self.CloseButton.resize(self.title_height,self.title_height)
        self.CloseButton.clicked_connect_func=(self.close)
        #标题栏
        self.TitleLabel=YTitleLabel(self)
        self.TitleLabel.move(0,0)
        self.TitleLabel.setStyleSheet('QWidget{background-color:rgba(0,0,0,0)}' )

        #翻页按钮
        self.nextbutton=NextPage(self)
        self.nextbutton.resize(*self.nextbutton_size)
        self.nextbutton.clicked_connect(self.next_image)
        self.prebutton=PrePage(self)
        self.prebutton.resize(*self.nextbutton_size)
        self.prebutton.clicked_connect(self.previous_image)
        # self.nextbutton.hide()
        # self.prebutton.hide()

        self.factor=1
        self.factor_max=5
        self.factor_min=0.04
        self.dir_images=None
        self.dir_images_n=None
        self.leftborder=BorderLine(self)
        self.rightborder=BorderLine(self)
        self.topborder=BorderLine(self)
        self.bottomborder=BorderLine(self)
        self.open_file(name)


    def get_images(self):
        dname=path.dirname(path.abspath(self.source_name))
        t=[path.join(dname,i) for i in os.listdir(dname) if path.splitext(i)[-1].lower() in self.gif_types or path.splitext(i)[-1].lower() in self.image_types]
        return t

    def next_image(self,e):
        if not self.dir_images:
            self.dir_images=self.get_images()
            if not self.dir_images:return
            filepath=path.abspath(self.source_name)
            if filepath in self.dir_images:
                self.dir_images_n=self.dir_images.index(filepath)
            else:
                self.dir_images_n=-1
        self.dir_images_n+=1
        if self.dir_images_n>=len(self.dir_images):
            self.dir_images_n=0
        self.open_file(self.dir_images[self.dir_images_n])
    def previous_image(self,e):
        if not self.dir_images:
            self.dir_images=self.get_images()
            if not self.dir_images:return
            filepath=path.abspath(self.source_name)
            if filepath in self.dir_images:
                self.dir_images_n=self.dir_images.index(filepath)
            else:
                self.dir_images_n=0
        self.dir_images_n-=1
        if self.dir_images_n<0:
            self.dir_images_n = len(self.dir_images)
            self.dir_images_n=0
        self.open_file(self.dir_images[self.dir_images_n])
    def open_file(self,name):
        self.source_name=name
        if name is not None:
            try:
                if path.splitext(name)[-1].lower() in self.gif_types:
                    self.gif(name)
                else:
                    self.image(name)
                return
            except Exception as e:
                print(e,self.source_name)
                self.label.setText('cannot open file:{0}\nError:{1}'.format(self.source_name,e))
                if self.first_window:
                    self.resize(400,400)
                    self.show()
    def gif(self,name):
        try:
            x=imageio.get_reader(name)
            meta=x.get_meta_data()
            fps=1000/meta.get('duration',None)
            jpgs=list(x)
            size=jpgs[0].shape
            size=size[1],size[0]
        except Exception as e:
            print('imageio',e)
            x=imageio.get_reader(name,'ffmpeg')
            meta=x.get_meta_data()
            fps=meta['fps']
            size=meta['size']
            jpgs=list(x)
        self.preview((jpgs,fps,(size[1],size[0])))
    def image(self,name):
        s=imread(name)
        shape=s.shape 
        self.preview(([s],0.0001,shape[:2]))
    def update_image(self):
        if self.nn>=len(self.jpgs):self.nn=0
        x=self.jpgs[self.nn]
        qimg=ndarry2qimage(x)
        self.label.setPixmap(QPixmap.fromImage(qimg))
        self.nn+=1

    def scaleImage(self,factor):
        tt=self.factor*factor
        if tt>self.factor_max or tt<self.factor_min:return
        pixmap=self.label.pixmap()
        if pixmap is None:return
        w,h=pixmap.size().width(),pixmap.size().height()
        self.factor*=factor

        x0,y0=self.label.x(),self.label.y()
        w0,h0=self.width()/2,self.height()/2
        #(w0-x0)factor=(w0-x)
        self.label.move(w0-factor*(w0-x0),h0-factor*(h0-y0))
        self.label.resize(w*self.factor,h*self.factor)
        if h*self.factor<self.max_image_height:
            self.setPosition()
    def setPosition(self):
        title_height=self.title_height
        bottom_height=self.bottom_height
        w,h=self.width(),self.height()
        self.CloseButton.move(w-title_height,0)
        self.TitleLabel.resize(w-self.title_height,self.title_height)

        # h-=title_height+bottom_height
        w_label,h_label=self.label.width(),self.label.height()
        self.label.move((w-w_label)/2,(h-h_label)/2)
        self.nextbutton.move(w-self.nextbutton_size[0],title_height)
        self.prebutton.move(0,title_height)
        self.leftborder.resize(1,h)
        self.topborder.resize(w,1)
        self.rightborder.setGeometry(w-1,0,1,h)
        self.bottomborder.setGeometry(0,h-1,w,1)
    def setAutoplay(self):
        if self.autoplay is True:
            self.autoplay=False
            self.timer_auto.stop()
        else:
            self.autoplay = True
            self.timer_auto=QTimer(self)
            self.timer_auto.timeout.connect(lambda :self.next_image(None))
            self.timer_auto.start(self.autoplay_interval)
    def preview(self,parent):
        self.nn=0
        self.jpgs, self.fps ,shape  = parent
        m=max(shape)
        t=max(1,m/self.max_image_height)
        shape=shape[0]/t,shape[1]/t
        self.factor=1/t
        self.label.resize(shape[1],shape[0])
        if self.first_window:
            self.resize(shape[1]+self.border*2,shape[0]+self.border*2+self.bottom_height)
            self.first_window=False
        else:
            w,h=self.width(),self.height()
            print(w,h,self.source_name)
            self.resize(max(w,shape[1]),max(h,shape[0]))
            self.timer.stop()
        self.setPosition()
        self.update_image()
        if self.fps != 0:
            self.timer=QTimer(self)
            self.timer.timeout.connect(self.update_image)
            t=int(1/self.fps*1000)
            self.timer.start(t)
        self.show()
    def isresizeMouse(self,x,y):

        x0,y0=self.x(),self.y()
        w0,h0=self.width(),self.height()
        width=4
        distance=8
        if x<x0+width and y0+h0-distance>y>y0+distance:#left
            self.setCursor(QCursor(Qt.SizeHorCursor))
            self.resizeWindow='Left'
        elif x>x0+w0-width and y0+h0-distance>y>y0+distance:#right
            self.setCursor(QCursor(Qt.SizeHorCursor))
            self.resizeWindow='Right'
        elif y<y0+width and x0+w0-distance>x>x0+distance:#top
            self.setCursor(QCursor(Qt.SizeVerCursor))
            self.resizeWindow='Top'
        elif y>y0+h0-width and x0+w0-distance>x>x0+distance:#bottom
            self.setCursor(QCursor(Qt.SizeVerCursor))
            self.resizeWindow='Bottom'
        elif x<x0+distance and y<y0+distance:#LeftTop
            self.setCursor(QCursor(Qt.SizeFDiagCursor))
            self.resizeWindow='LeftTop'
        elif x>x0-distance+w0 and y>y0-distance+h0:#RightBottom
            self.setCursor(QCursor(Qt.SizeFDiagCursor))
            self.resizeWindow='RightBottom'
        elif x<x0+distance and y>y0-distance+h0:#LeftBottom
            self.setCursor(QCursor(Qt.SizeBDiagCursor))
            self.resizeWindow='LeftBottom'
        else:
            self.resizeWindow = False
            self.setCursor(QCursor(Qt.ArrowCursor))


    def hide_button(self,x):

        w=self.width()
        if x<w/4:
            self.prebutton.show()
            self.nextbutton.hide()
        elif x>w/4*3:
            self.nextbutton.show()
            self.prebutton.hide()
        else:
            self.prebutton.hide()
            self.nextbutton.hide()
    def runResizeWindow(self):
        pos=QCursor.pos()
        x,y=pos.x(),pos.y()
        if self.resizeWindow == 'Left':
            wt=self.w0+self.x0-x
            if self.minimumSize_window[0]>wt:return
            self.setGeometry(x,self.y0,wt,self.h0)
        elif self.resizeWindow == 'Right':
            wt=x-self.x0
            self.resize(wt,self.h0)
        elif self.resizeWindow == 'Bottom':
            ht=y-self.y0
            self.resize(self.w0,ht)
        elif self.resizeWindow == 'Top':
            ht=self.y0-y+self.h0
            if self.minimumSize_window[1]>ht:return
            self.setGeometry(self.x0,y,self.w0,ht)
        elif self.resizeWindow == 'RightBottom':
            wt,ht=x-self.x0,y-self.y0
            self.resize(wt,ht)
        elif self.resizeWindow == 'LeftTop':
            wt,ht=self.x0-x+self.w0,self.y0-y+self.h0
            if self.minimumSize_window[0]>wt:
                wt=self.minimumSize_window[0]
                x=self.x() 
            if self.minimumSize_window[1]>ht:
                ht=self.minimumSize_window[1]
                y=self.y()
            self.setGeometry(x,y,wt,ht)
        elif self.resizeWindow == 'LeftBottom':
            wt,ht=self.x0-x+self.w0,y-self.y0
            if self.minimumSize_window[0]>wt:
                wt=self.minimumSize_window[0]
                x=self.x() 
            if self.minimumSize_window[1]>ht:
                ht=self.minimumSize_window[1]
            self.setGeometry(x,self.y0,wt,ht)
    def mousePressEvent(self,e):
        if self.resizeWindow:
            self.x0,self.y0=self.x(),self.y()
            self.w0,self.h0=self.width(),self.height()
    def mouseMoveEvent(self,e):
        if self.resizeWindow:
            self.runResizeWindow()
    def resizeEvent(self,e):
        self.setPosition()
    def wheelEvent(self,e):
        if e.angleDelta().y()>0:
            factor=1.05
        else:
            factor=0.95
        self.scaleImage(factor)
    def leaveEvent(self,e):
        self.nextbutton.hide()
        self.prebutton.hide()
    def mouseDoubleClickEvent(self,e):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()
    def eventFilter(self,source,event):
        t=event.type()
        if t == QEvent.MouseMove:
            if event.buttons() == Qt.NoButton:
                pos=QCursor.pos()
                # self.hide_button(pos.x()-self.x())
                if not self.isMaximized():
                    self.isresizeMouse(pos.x(),pos.y())
        return super().eventFilter(source,event)

def main():
    
    if len(sys.argv)==2:
        name=sys.argv[1]
    else:
        name='null.null'
    app = QApplication(sys.argv)
    # name='/home/yxs/Pictures/tt.gif'
    Viewer = GifPreview(name=name)
    app.installEventFilter(Viewer)
    sys.exit(app.exec_())
if __name__ == '__main__':
    main()