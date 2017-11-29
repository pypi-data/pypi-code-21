#!/usr/bin/env python3
from PyQt5 import QtCore
from PyQt5.QtCore import QDir, Qt,QThread,pyqtSignal
from PyQt5.QtGui import QImage, QPixmap,QCursor,QFont,QPainter,QColor,QPen
from PyQt5.QtWidgets import (QApplication, QFileDialog, QLabel,QWidget,QPushButton,
        QMessageBox, QScrollArea, QSizePolicy,QLineEdit,QInputDialog,QDialog,
        QRadioButton,QMenu,QAction,QCheckBox,QVBoxLayout,QHBoxLayout,QColorDialog,QFontDialog)
from numpy import hstack,stack,fromfile,fromstring

import imageio
from . import CutImageWidget
import os
from os import path

from io import StringIO
import pip
import sys
import tempfile
from PIL import Image
from PIL import ImageFont
import yxspkg_songzviewer
sysplatform=sys.platform #mac:darwin
version='1.2.2'
software_name='SongZ GIF'
ffmpeg_file=None
cache_dir=tempfile.mkdtemp()
without_cv2=True #默认不采用cv2
without_audio=False #默认采用添加音频
temp_nn=14 #标记 只增加不减小
global_ndarry_max=8*1024*1024*1024 #设置ndarray占用的最大内存
del tempfile
print('temp folder path:',cache_dir)
def resizeimg(img,size):
    shape=img.shape
    if shape[:2]==size:return img 
    if img.dtype!='uint8':
        img=img.astype('uint8')
    pimg=Image.fromarray(img)
    pimg=pimg.resize((size[1],size[0]))
    x=fromstring(pimg.tobytes(),dtype='uint8')
    if len(shape)==2:
        x.shape=(size[0],size[1])
    else:
        x.shape=(size[0],size[1],-1)
    return x
def ndarryfile(s):
    if not isinstance(s,str):return s 
    n,shape,dtype=path.basename(s).split('_')
    shape=[int(i) for i in shape.split('.')]
    x=fromfile(s,dtype=dtype)
    x.shape=shape
    return x
def write_ndarryfile(s):
    global temp_nn
    shape,dtype=s.shape,s.dtype
    fname='{0}_{1}_{2}'.format(temp_nn,'.'.join([str(i) for i in shape]),dtype)
    p=path.join(cache_dir,fname)
    print(p)
    s.tofile(p)
    temp_nn+=1
    return p
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

class YLineEdit(QLineEdit): #高度和宽度输入框
    def connect(self,func):
        self.callback=func
    def keyReleaseEvent(self,e):
        self.callback(self.text())

class setupWidget(QWidget):
    def __init__(self,parent):
        super().__init__()
        size=(350,100)
        self.resize(*size)
        self.setWindowTitle(software_name)
        layout=QVBoxLayout()
        self.setLayout(layout)
        hlayout=QHBoxLayout()
        hlayout.addStretch() 
        l=QLabel('当前版本号：'+version)
        font=QFont()
        font.setPixelSize(25)
        l.setFont(font)
        hlayout.addWidget(l)
        hlayout.addStretch() 
        layout.addLayout(hlayout)

        hlayout=QHBoxLayout()
        hlayout.addStretch() 
        l=QPushButton('检查更新')
        font=QFont()
        font.setPixelSize(25)
        l.setFont(font)
        l.clicked.connect(lambda:parent.checkupdate(self,True))
        hlayout.addWidget(l)
        hlayout.addStretch() 
        layout.addLayout(hlayout)

class aboutWidget(QWidget):  #about
    def __init__(self,*d):
        super().__init__(*d)
        size=(350,100)
        self.resize(*size)
        self.setWindowTitle(software_name)
        layout=QVBoxLayout()
        self.setLayout(layout)
        hlayout=QHBoxLayout()
        hlayout.addStretch() 
        l=QLabel(software_name)
        font=QFont()
        font.setPixelSize(25)
        l.setFont(font)
        hlayout.addWidget(l)
        hlayout.addStretch() 
        layout.addLayout(hlayout)

        hlayout=QHBoxLayout()
        hlayout.addStretch() 
        l=QLabel('赠予我的Jesmine, ——Blacksong')
        font=QFont()
        font.setPixelSize(15)
        l.setFont(font)
        hlayout.addWidget(l)
        hlayout.addStretch() 
        layout.addLayout(hlayout)

        hlayout=QHBoxLayout()
        hlayout.addStretch() 
        l=QLabel('Copyright @ Blacksong')
        font=QFont()
        font.setPixelSize(15)
        l.setFont(font)
        hlayout.addWidget(l)
        hlayout.addStretch() 
        layout.addLayout(hlayout)

        hlayout=QHBoxLayout()
        hlayout.addStretch() 
        l=QLabel('版本号：{version}'.format(version=version))
        font=QFont()
        font.setPixelSize(15)
        l.setFont(font)
        hlayout.addWidget(l)
        hlayout.addStretch() 
        layout.addLayout(hlayout)

class waitMessage(QWidget):
    def __init__(self,s="稍等..."):
        super().__init__()
        self.text=QLabel(self)
        self.text.setText(s)
        self.setWindowTitle('Runing... ')
        self.text.setGeometry(40,0,200,80)
        self.resize(160,80)
        self.show()
class SaveThread(QThread):   
    trigger = pyqtSignal(tuple)
    def __int__(self):
        super().__init__()
    def setValue(self,parent,filename):
        self.filename=filename
        self.parent=parent
        if ffmpeg_file is None:
            self.ffmpeg=imageio.plugins.ffmpeg.get_exe()
        else:
            self.ffmpeg=ffmpeg_file
        parent.savedPath=path.dirname(filename)
    def generate_gif(self,jpgs,fps,size):
        writer=imageio.get_writer(self.filename , fps=fps)
        for i in jpgs:
            i=ndarryfile(i)
            if i.shape[:2]!=size:
                i=resizeimg(i,size)
            writer.append_data(i)
        writer.close()
    def get_music_file(self,duration):
        if without_audio:return None
        music_file=self.parent.text_music_label.text().strip()
        if not music_file:return None
        music_file,start_time=music_file.split('|')
        outfile=path.join(cache_dir,'2323232323.aac')
        os.system('{ffmpeg} -i "{infile}" -ss {start} -t  {duration} -acodec copy -y {outfile}'.format(ffmpeg=self.ffmpeg,infile=music_file,outfile=outfile,start=float(start_time),duration=float(duration)))
        return outfile
    def generate_video_cv2(self,jpgs,fps,size):
        writer=cv2.VideoWriter(self.filename,cv2.VideoWriter.fourcc(*'MPEG'),fps,(size[1],size[0]))
        for i in jpgs:
            i=resizeimg(ndarryfile(i),size)
            i=i[:,:,(2,1,0)]
            writer.write(i)
        writer.release()
        return None
    def generate_video(self,jpgs,fps,size):
        if without_cv2:
            ffmpeg_params=['-s','{w}x{h}'.format(w=size[1],h=size[0])]
            writer=imageio.get_writer(self.filename , fps=fps,ffmpeg_params=ffmpeg_params)
            for i in jpgs:
                writer.append_data(ndarryfile(i))
            writer.close()
        else:
            self.generate_video_cv2(jpgs,fps,size)
        music_file=self.get_music_file(len(jpgs)/fps)
        if music_file:
            ppname=path.join(path.dirname(self.filename),'.sdsd'+path.basename(self.filename))
            os.rename(self.filename,ppname)
            os.system('{ffmpeg} -i {video} -i {audio} -c copy -y {out}'.format(ffmpeg=self.ffmpeg, video=ppname,audio=music_file,out=self.filename))
            os.remove(ppname)
            os.remove(music_file)
    def generate_image(self,size):
        outimg=ndarryfile(self.parent.board.current_image.ndimage)
        if outimg.shape[-1]==4 and path.splitext(self.filename)[1].lower() in ['.jpg','.jpeg']:
            outimg=outimg[:,:,:3]
        outimg=resizeimg(outimg,size)
        imageio.imwrite(self.filename,outimg)

    def run(self):
        fps=float(self.parent.text_fps_label.text())
        jpgs=self.parent.getNdImages()
        size=int(self.parent.text_h_label.text()),int(self.parent.text_w_label.text())
        try:
            if self.filename[-4:]=='.gif':
                self.generate_gif(jpgs,fps,size)
            elif path.splitext(self.filename)[1] in self.parent.image_files:
                self.generate_image(size)
            else:
                self.generate_video(jpgs,fps,size)
        except Exception as e:
            self.trigger.emit((0,e)) 
            return
        self.trigger.emit((1,None)) 

class VideoReadThread(QThread):   
    trigger = pyqtSignal(tuple)
    def __int__(self):  
        super().__init__()  

    def setValue(self,videoreader):
        self.videoreader=videoreader

    def run(self):
        try:
            for i in self.videoreader:
                self.trigger.emit((i,))
        except:
            print('Reading warning!')
            return

class VideoCutter(QDialog):  #获取视频截取信息的输入对话框
    def __init__(self):
        super().__init__()
        self.info=None
        self.initUI()

    def initUI(self):
        h_p=20
        self.ts = QLabel("开始时间:", self)
        self.ts.move(10, h_p+2)
        self.ss = QLineEdit(self)
        self.ss.move(68, h_p)
        self.ss.resize(100,20)
        self.ss.setText('0:0:0')
        h_p+=25
        self.te = QLabel("结束时间:", self)
        self.te.move(10, h_p+2)
        self.se = QLineEdit(self)
        self.se.move(68, h_p)
        self.se.resize(100,20)
        self.se.setText('0:0:9')

        h_p+=25
        self.tf = QLabel("GIF帧率:", self)
        self.tf.move(10, h_p+2)
        self.sf = QLineEdit(self)
        self.sf.move(68, h_p)
        self.sf.resize(100,20)
        self.sf.setText('9')

        h_p+=35
        self.ok=QPushButton(self)
        self.ok.move(120,h_p)
        self.ok.setText('确定')
        self.ok.clicked.connect(self.accept)
        self.resize(200, 130)
        self.setWindowTitle("视频截取设置")
        self.show()

    def accept(self):
        start_time=[i.strip() for i in self.ss.text().split(':')]
        end_time=[i.strip() for i in self.se.text().split(':')]
        fps=self.sf.text().strip()
        try:
            start_time=float(start_time[0])*3600+float(start_time[1])*60+float(start_time[2])
            end_time=float(end_time[0])*3600+float(end_time[1])*60+float(end_time[2])
            fps=float(fps)
        except Exception as e:
            QMessageBox.information(self, "Input error",
                            "输入有误\n{0}".format(e))
            return
        self.info=start_time,end_time,fps
        super().accept()
    def get_info(self,duration,fps):
        if duration>10:
            duration=10
        self.se.setText('0:0:{0}'.format(str(duration)))
        self.sf.setText(str(fps))
        self.exec_()
        return self.info
class FontExample(QLabel):
    def setParent(self,parent):
        self.parent=parent
    def mousePressEvent(self,e):
        self.x0,self.y0=self.parent.position_input[0],self.parent.position_input[1]
        self.mx0,self.my0=e.pos().x(),e.pos().y()
    def mouseMoveEvent(self,e):
        self.parent.need_painted=True
        rotate=self.parent.rotate_input
        p_rate=self.parent.p_rate
        self.mx1,self.my1=e.pos().x(),e.pos().y()
        dx,dy=self.mx1-self.mx0,self.my1-self.my0
        dx*=-p_rate
        dy*=-p_rate

        # print(self.x0+dx,self.y0+dy)
        t=self.x0+dx,self.y0+dy
        self.parent.position_input=t
        self.parent.position_name.setText('%d,%d' % t)
class FontEditor(QDialog):  #获取字体设置信息
    def __init__(self):
        super().__init__()
        self.info=None
        self.font_input=QFont()
        self.color_input=QColor(0,0,0)
        self.pointSize_default_font=self.font_input.pointSize()
        self.weight_default_font=50
        self.position_input=0,-30
        self.need_painted=True
        self.rotate_default_font=0
        self.rotate_input = self.rotate_default_font
        self.qp=QPainter()
        self.pen_weight=9
        
    def setColor(self):
        #options = QColorDialog.ColorDialogOptions(QFlag.QFlag(colorDialogOptionsWidget.value()))
        color = QColorDialog.getColor(Qt.green, self, "Select Color")
        if color.isValid():
            self.need_painted=True
            self.color_name.setText(color.name())
            self.color_input=color 
    def ndarrayonlabel(self,ndimg):
        qimg=ndarry2qimage(ndimg)
        qimg=qimg.scaledToHeight(ImageLabel.global_height)
        self.example.setPixmap(QPixmap.fromImage(qimg))
    def setFont(self):
        #options = QFontDialog.FontDialogOptions(QFlag(fontDialogOptionsWidget.value()))
        #font, ok = QFontDialog.getFont(ok, QFont(self.label_font.text()), self, "Select Font",options)
        font, ok = QFontDialog.getFont(self.font_input)
        if ok:
            self.need_painted=True
            self.font_input=font 
            self.size_name.setText(str(font.pointSize()))
            self.weight_name.setText(str(font.Weight()))

    def paintEvent(self,e):
        if not self.need_painted:return
 
        self.need_painted=False
        qp=self.qp
        Qimg=self.Qimg.copy()
        qp.begin(Qimg)
        qp.rotate(self.rotate_input)
        qp.setFont(self.font_input)
        qp.setPen(self.color_input)
        shape=self.ndimg.shape
        qp.setWindow(self.position_input[0],self.position_input[1],shape[1],shape[0])
        qp.drawText(0,0,self.get_text_input())
        qp.end()
        Qimg=Qimg.scaledToHeight(ImageLabel.global_height)
        pimg=QPixmap.fromImage(Qimg)
        self.example.setPixmap(pimg)
        
    def initUI(self):
        l_content=QHBoxLayout()
        self.ts = QLabel("内容:")
        self.ss = QLineEdit()
        self.ss.setText('我能吞下玻璃而不伤害身体')
        l_content.addWidget(self.ts)
        l_content.addWidget(self.ss)
        l_font=QHBoxLayout()
        self.font = QLabel("字体:")
        self.font_label = QLabel('我能吞下玻璃而不伤身体')
        self.font_selector=QPushButton('选择')
        self.font_selector.clicked.connect(self.setFont)
        l_font.addWidget(self.font )
        l_font.addWidget(self.font_label ,2)
        l_font.addWidget(self.font_selector)
        
        l_color=QHBoxLayout()
        self.color = QLabel("颜色:")
        self.color_name = QLineEdit()
        self.color_selector=QPushButton('选择')
        self.color_selector.clicked.connect(self.setColor)
        l_color.addWidget(self.color)
        l_color.addWidget(self.color_name)
        l_color.addWidget(self.color_selector)
        l_size=QHBoxLayout()
        self.size = QLabel("大小:")
        self.size_name = QLineEdit()
        self.size_name.setText(str(self.pointSize_default_font))
        self.size_up=QPushButton('增大')
        self.size_down=QPushButton('减小')
        self.size_up.clicked.connect(lambda :self.__changeSize(1))
        self.size_down.clicked.connect(lambda :self.__changeSize(-1))
        l_size.addWidget(self.size)
        l_size.addWidget(self.size_name)
        l_size.addWidget(self.size_up)
        l_size.addWidget(self.size_down)

        l_weight=QHBoxLayout()
        self.weight = QLabel("粗细:")
        self.weight_name = QLineEdit()
        self.weight_name.setText(str(self.weight_default_font))
        self.weight_up=QPushButton('增大')
        self.weight_down=QPushButton('减小')
        self.weight_up.clicked.connect(lambda :self.__setFontWeight(10))
        self.weight_down.clicked.connect(lambda :self.__setFontWeight(-10))
        l_weight.addWidget(self.weight)
        l_weight.addWidget(self.weight_name)
        l_weight.addWidget(self.weight_up)
        l_weight.addWidget(self.weight_down)

        l_rotate=QHBoxLayout()
        self.rotate = QLabel("旋转:")
        self.rotate_name = QLineEdit('0')
        self.rotate_name.setText(str(self.rotate_default_font))
        self.rotate_up=QPushButton('顺时针')
        self.rotate_down=QPushButton('逆时针')
        self.rotate_up.clicked.connect(lambda :self.__setFontrotate(10))
        self.rotate_down.clicked.connect(lambda :self.__setFontrotate(-10))
        l_rotate.addWidget(self.rotate)
        l_rotate.addWidget(self.rotate_name)
        l_rotate.addWidget(self.rotate_up)
        l_rotate.addWidget(self.rotate_down)

        l_position=QHBoxLayout()
        self.position = QLabel("位置:")
        self.position_name = QLineEdit()
        self.position_name.setReadOnly(True)
        self.position_name.setText('0,0')
        l_position.addWidget(self.position)
        l_position.addWidget(self.position_name)

        
        self.ok=QPushButton()
        self.ok.setText('应用')
        self.ok.clicked.connect(self.accept)

        self.example=FontExample()
        self.example.setParent(self)
        self.ndarrayonlabel(self.ndimg)
        
        layout=QVBoxLayout()
        layout.addLayout(l_content)
        layout.addLayout(l_font)
        layout.addLayout(l_color)
        layout.addLayout(l_size)
        layout.addLayout(l_weight)
        layout.addLayout(l_rotate)
        layout.addLayout(l_position)
        layout.addStretch(1)
        layout.addWidget(self.ok)
        
        hlayout=QHBoxLayout()
        hlayout.addWidget(self.example)
        hlayout.addLayout(layout)
        
        
        self.setLayout(hlayout)

        self.setWindowTitle("文字设置")

        self.show()
    def get_text_input(self):
        s=self.ss.text()
        return s.replace('\\n','\n')
    def __setFontrotate(self,a):
        s=self.rotate_name.text()
        s=int(s)+a 
        self.rotate_name.setText(str(s))
        self.rotate_input=s 
        self.need_painted=True
    def __setFontWeight(self,a):
        self.need_painted=True
        s=self.weight_name.text()
        s=int(s)+a 
        self.weight_name.setText(str(s))
        self.font_input.setWeight(s)
        self.pen_weight=s

    def __changeSize(self,a):
        self.need_painted=True
        s=self.size_name.text()
        s=int(s)+a
        self.size_name.setText(str(s))
        self.font_input.setPointSize(s)

    def apply_input(self):
        pass
    def accept(self):
        self.info=self.font_input,self.color_input,self.position_input,self.rotate_input, self.get_text_input()
        super().accept()
    def get_info(self,parent):
        self.parent=parent
        self.info=None
        self.ndimg=ndarryfile(parent.board.current_image.ndimage)
        self.Qimg=ndarry2qimage(self.ndimg)
        self.p_rate=self.ndimg.shape[0]/ImageLabel.global_height #实际尺寸与图片显示的尺寸的比值
        self.initUI()
        self.exec_()
        return self.info


class ImageLabel(QLabel):
    global_height=400
    def __init__(self,d):
        super().__init__(d)
        self.factor=1
        self.father=d
        self.setScaledContents(True)

        self.pages=QLabel(self)
        self.pages.move(0,0)
        self.pages.resize(70,20)
        self.father.current_image=self

    def mousePressEvent(self,e):
        self.father.current_image=self
        self.father.isPressing=True
    def setImage(self,img):
        self.size=img.width(),img.height()
        img=img.scaledToHeight(self.global_height)
        self.setPixmap(QPixmap.fromImage(img))
        self.number=self.father.scaleImage(self)
    def setndimage(self,name): #Filename 可以是文件名 也可以是 ndarry
        self.father.ndarry_n+=name.size*name.itemsize
        if self.father.ndarry_n>self.father.ndarry_max:
            name=write_ndarryfile(name)
        self.ndimage=name

class ImageBoard(QWidget):
    def __init__(self,*d):
        super().__init__(*d)
        self.isMoving=False
        self.current_image=None
        self.need_init_set=True
        self.isPressing=False
        self.image_list=list()
        self.ndarry_n=0
        self.ndarry_max=global_ndarry_max

    def mouseMoveEvent(self,e):
        pass
    def mouseReleaseEvent(self,e):
        self.isPressing=False
        self.need_init_set=True
    def scaleImage(self,image):
        right=self.width()
        # print(right)
        w=image.pixmap().size().width()
        self.image_list.append([image,0,w,right]) #[图片label，编号,宽度，右边位置]
        image.move(right,0)
        right+=w
        self.resize(right,self.height())

class DrawImageWidget(QLabel): #用来绘制图片的Widget，不需要显示出来，后台运行
    def __init__(self,*d):
        super().__init__(*d)
        self.need_painted=False
        self.resize(2,2)
    def paintEvent(self,e):
        if not self.need_painted:return
        qp=QPainter()
        for i,img in enumerate(self.jpgs):
            img=ndarryfile(img)
            qimg=ndarry2qimage(img)
            qp.begin(qimg)
            qp.rotate(self.rotate_input)
            qp.setFont(self.font_input)
            qp.setPen(self.color_input)
            shape=img.shape
            qp.setWindow(self.position_input[0],self.position_input[1],shape[1],shape[0])
            qp.drawText(0,0,self.text_input)
            qp.end()
            img=Image.fromqimage(qimg)
            img=fromstring(img.tobytes(),dtype='uint8')
            img.shape=shape
            self.jpgs[i]=img
        self.need_painted=False
        self.finished_func()
    def setValue(self,font,color,position,rotate,text,jpgs):
        self.color_input=color 
        self.font_input=font 
        self.text_input=text 
        self.position_input=position 
        self.rotate_input = rotate 
        self.jpgs=jpgs
    def start_painting(self):
        self.need_painted=True
    def finished_connect(self,func):
        self.finished_func=func
class YScrollArea(QScrollArea):
    def __init__(self,*d):
        super().__init__(*d)
        self.bar=self.horizontalScrollBar()
    def wheelEvent(self,e):
        bar=self.bar
        if e.angleDelta().y()>0:
            m=-50
        else:m=50
        v=bar.value()
        bar.setValue(v+m)
    def enterEvent(self,e):
        self.entered=True
    def leaveEvent(self,e):
        self.entered=False

class GifMaker(QWidget):
    video_files=['.mp4','.mkv','.ts','.avi','.flv','.mov','.mpg','.m4v']
    image_files=['.jpg','.jpeg','.bmp','.png','.ico','.icns','.tiff']

    def __init__(self):
        super().__init__()
        self.videoclip=None
        self.setAcceptDrops(True)
        self.h=True
        self.interval=1
        self.savedPath=QDir.homePath()
        self.board = self.init_board()
        self.scrollArea=YScrollArea(self)
        width,height=820,400
        self.resize(width,height)
        self.setMinimumSize(width,height)
        self.setMaximumSize(width,height)
        self.scrollArea.setWidget(self.board)
        self.scrollArea.resize(700,400)
        self.scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.bar=self.scrollArea.horizontalScrollBar()
        left_p=705
        h_p=10
        self.outputlabel=QLabel(self)
        self.outputlabel.setGeometry(left_p,h_p,90,15)
        self.outputlabel.setText('输出设置:')

        h_p+=25
        self.f_label=QLabel(self)
        self.f_label.setGeometry(left_p,h_p,60,20)
        self.f_label.setText('帧数：')
        self.text_f_label=QLabel(self)
        self.text_f_label.setGeometry(750,h_p,40,16)
        self.text_f_label.setText('0')
        
        h_p+=20
        self.fps_label=QLabel(self)
        self.fps_label.setGeometry(left_p,h_p,60,20)
        self.fps_label.setText('帧率：')
        self.text_fps_label=QLineEdit(self)
        self.text_fps_label.setText('10')
        self.text_fps_label.setGeometry(750,h_p,40,16)

        h_p+=21
        self.h_label=QLabel(self)
        self.h_label.setGeometry(left_p,h_p,60,20)
        self.h_label.setText('高度：')
        self.text_h_label=YLineEdit(self)
        self.text_h_label.connect(self.__check_height)
        self.text_h_label.setGeometry(750,h_p,40,16)
        h_p+=20
        self.w_label=QLabel(self)
        self.w_label.setGeometry(left_p,h_p,60,20)
        self.w_label.setText('宽度：')
        self.text_w_label=YLineEdit(self)
        self.text_w_label.connect(self.__check_width)
        self.text_w_label.setGeometry(750,h_p,40,16)
        h_p+=15
        self.ratiobox=QCheckBox('保持高宽比例',self)
        self.ratiobox.move(left_p,h_p+10)
        self.ratiobox.stateChanged.connect(self.checkRatio)
        self.ratiobox.toggle()  #设置默认值 self.ratio_state=True 
        
        h_p=200
        self.cutButton=QPushButton(self)
        self.cutButton.setGeometry(701,h_p,49,30)
        self.cutButton.setText('裁剪')
        self.cutButton.clicked.connect(self.cut)
        self.textbutton=QPushButton(self)
        self.textbutton.setGeometry(751,h_p,49,30)
        self.textbutton.setText('文字')
        self.textbutton.clicked.connect(self.__drawText)
        self.textbutton.setEnabled(False)
        
        h_p=370
        w_w=(width-700-4)/2
        self.openbutton=QPushButton(self)
        self.openbutton.setGeometry(701,h_p,w_w,30)
        self.openbutton.setText('打开')
        self.openbutton.clicked.connect(self.open)
        self.savebutton=QPushButton(self)
        self.savebutton.setGeometry(701+(width-700)/2,h_p,w_w,30)
        self.savebutton.setText('保存')
        self.savebutton.clicked.connect(self.save)
        self.savebutton.setEnabled(False)
        self.openbutton.setEnabled(False) #禁用 打开 按钮，等待所有模块加载完毕后启用
        h_p-=40
        self.musicbutton=QPushButton(self)
        self.musicbutton.setGeometry(701,h_p,40,30)
        self.musicbutton.setText('音乐')
        self.musicbutton.clicked.connect(self.__insert_music)
        self.text_music_label=QLineEdit(self)
        self.text_music_label.setGeometry(750,h_p+2,60,26)
        h_p-=80
        self.previewbutton=QPushButton(self)
        self.previewbutton.setGeometry(701,h_p,49,30)
        self.previewbutton.setText('预览')
        self.previewbutton.clicked.connect(self.preview)
        self.testbutton=QPushButton(self)
        self.testbutton.setGeometry(751,h_p,49,30)
        self.testbutton.setText('测试')
        self.testbutton.clicked.connect(self.test)
        self.testbutton.hide()
        self.drawWidget=DrawImageWidget(self)
        self.drawWidget.hide()

        self.setWindowTitle(software_name)
        self.resize(800, 400)
        self.show()
        self.nn= 0 
        self.create_right_key_menu()

        self.update_sum_frames()
        self.timer=QtCore.QTimer(self)
        self.timer.timeout.connect(self.after_run)
        self.timer.start(30)
    def after_run(self):#用于图形界面启动后导入模块以及检查更新
        # import imageio
        # from . import CutImageWidget
        # import re,os
        # from os import path
        # global imageio,CutImageWidget,re,os,path
        # if not without_cv2:
        #     import cv2
        #     global cv2
        self.openbutton.setEnabled(True) #模块加载完毕 启用打开按钮
        # self.checkupdate(self,False)  #开机自动检查更新
        self.timer.stop()
    def checkupdate(self,parent,display_already):
        x=StringIO()
        self.waitmsg=waitMessage()
        out=sys.stdout
        sys.stdout=x
        out_argv=sys.argv
        sys.argv=['pip','install','yxspkg_songzgif','-U','--user']
        pip.main()
        sys.argv=out_argv
        sys.stdout=out 
        x.seek(0,0)
        t=x.read()
        self.waitmsg.close()
        if t.find('already up-to-date')!=-1:
            if display_already:
                QMessageBox.information(parent, "Update","已经是最新版本")
        else:
            QMessageBox.information(parent, "Update","已经更新到最新版本，重启后可用")

    def init_board(self):
        board=ImageBoard()
        board.resize(0,400)
        board.setMinimumSize(0,400)
        return board
    def closeEvent(self,e):
        try:
            for i in os.listdir(cache_dir):
                print('remove',i)
                os.remove(path.join(cache_dir,i))
            os.removedirs(cache_dir)
        except:
            pass
        sys.exit(0)
    def setEnabled_size(self,state):
        self.text_h_label.setEnabled(state)
        self.text_w_label.setEnabled(state)
        self.ratiobox.setEnabled(state)
        self.cutButton.setEnabled(state)
        self.savebutton.setEnabled(state)
        self.text_fps_label.setEnabled(state)
        self.previewbutton.setEnabled(state)
        self.textbutton.setEnabled(state)

    def create_right_key_menu(self):
        self.setContextMenuPolicy(Qt.CustomContextMenu)  
        self.customContextMenuRequested.connect(self.show_right_menu)  
  
        self.rightMenu = QMenu(self)  
        
        self.deleteCurrentAct = QAction("删除该帧", self,  triggered=self.__delete_image_current)
        self.rightMenu.addAction(self.deleteCurrentAct) 
        self.deleteBeforeAct = QAction("删除该帧及之前所有帧", self,  triggered=self.__delete_image_before)
        self.rightMenu.addAction(self.deleteBeforeAct) 
        self.deleteBehindAct = QAction("删除该处及之后所有帧", self,  triggered=self.__delete_image_behind)
        self.rightMenu.addAction(self.deleteBehindAct) 
        self.deleteSpecialAct = QAction("删除指定帧", self,  triggered=self.__delete_image_special)
        self.rightMenu.addAction(self.deleteSpecialAct) 
        self.deleteAllAct = QAction("删除所有帧", self, shortcut="delete",triggered=lambda:self.delete_image(0,-1))
        self.rightMenu.addAction(self.deleteAllAct) 
        
        self.rightMenu.addSeparator() 
        self.changefpsAct = QAction("改变帧率", self, triggered=self.__changefps)
        self.rightMenu.addAction(self.changefpsAct) 
        self.rightMenu.addSeparator() 
        self.insertimageAct = QAction("插入文件", self, triggered=self.__insertfile)
        self.rightMenu.addAction(self.insertimageAct) 
        self.reverseAct = QAction("逆序", self,triggered=self.__reverseimage)
        self.rightMenu.addAction(self.reverseAct)

        self.rotateAct = QAction("逆时针旋转90度", self,triggered=lambda :self.__rotate(90))
        self.rightMenu.addAction(self.rotateAct)

        self.rotate270Act = QAction("顺时针旋转90度", self,triggered=lambda :self.__rotate(270))
        self.rightMenu.addAction(self.rotate270Act)

        self.rotate180Act = QAction("旋转180度", self,triggered=lambda :self.__rotate(180))
        self.rightMenu.addAction(self.rotate180Act)

        self.rotate_1Act = QAction("左右镜像对称", self,triggered=lambda :self.__rotate(-1))
        self.rightMenu.addAction(self.rotate_1Act)

        self.rotate_2Act = QAction("上下镜像对称", self,triggered=lambda :self.__rotate(-2))
        self.rightMenu.addAction(self.rotate_2Act)

        self.mergeAct = QAction("合成一张图", self,triggered=self.__mergeimage)
        self.rightMenu.addAction(self.mergeAct)

        self.rightMenu.addSeparator() 
        self.saveimageAct = QAction("图片另存为", self, triggered=self.__saveimage)
        self.rightMenu.addAction(self.saveimageAct) 
        self.rightMenu.addSeparator() 
        self.setupAct = QAction("设置", self,triggered=self.__setup)
        self.rightMenu.addAction(self.setupAct) 
        self.rightMenu.addSeparator() 
        self.setupAct = QAction("关于"+software_name, self, triggered=self.__about)
        self.rightMenu.addAction(self.setupAct) 
        self.right_act=[self.changefpsAct ,self.mergeAct,self.rotate_2Act,self.rotate_1Act,self.rotate180Act,self.rotate270Act,self.rotateAct,self.reverseAct,self.deleteCurrentAct,self.deleteBeforeAct,self.deleteBehindAct,self.deleteAllAct,self.saveimageAct,self.insertimageAct,self.deleteSpecialAct]
    def __mergeimage(self):
        height=int(self.text_h_label.text())
        ndimages=self.getNdImages()
        shape0=ndarryfile(ndimages[0]).shape
        self.delete_image(0,-1)
        def ttf(a):
            i=ndarryfile(a)
            shape=i.shape
            if len(shape)==2:
                i=stack((i,i,i),2)
            elif len(shape)==3 and shape[2]==4:
                i=i[:,:,:3]
            else:
                pass
            return resizeimg(i,(height,int(i.shape[1]*height/i.shape[0])))
        img=hstack([ttf(i) for i in ndimages])
        self.after_open((img,))
    def finished_response(self):
        self.drawWidget.hide()
        jpgs=self.drawWidget.jpgs
        self.delete_image(0,-1)
        self.after_open(jpgs)
    def __drawText(self):
        info = FontEditor().get_info(self)
        if info:
            self.drawWidget=DrawImageWidget(self)
            self.drawWidget.setValue(*info,self.getNdImages())
            self.drawWidget.start_painting()
            self.drawWidget.finished_connect(self.finished_response)
            self.drawWidget.show()
    def __changefps(self):
        fps0=float(self.text_fps_label.text())
        fps, ok = QInputDialog.getDouble(self, "QInputDialog.getDouble()", "输入帧率fps:", fps0, 0, 100, 2)
        if ok:
            jpgs=self.getNdImages()
            n=len(jpgs)*fps/fps0
            if n-int(n)>0.5:
                n2=int(n)+1
            else:
                n2=int(n)
            if n2==len(jpgs):return
            self.delete_image(0,len(jpgs))
            self.text_fps_label.setText(str(fps))
            for i in range(n2):
                t=int(i*fps0/fps)
                self.after_open((ndarryfile(jpgs[t]),))
    def __about(self):
        self._about=aboutWidget()
        self._about.show()
    def __rotate(self,angle=90):
        ndimages=self.getNdImages()
        self.delete_image(0,-1)
        op=self.after_open
        if angle==90:
            l=[op((ndarryfile(i)[:,::-1].swapaxes(1,0),)) for i in ndimages]
        elif angle==180:
            l=[op((ndarryfile(i)[::-1][:,::-1],)) for i in ndimages]
        elif angle==270:
            l=[op((ndarryfile(i)[::-1].swapaxes(1,0),)) for i in ndimages]
        elif angle==-2:
            l=[op((ndarryfile(i)[::-1],)) for i in ndimages]
        elif angle==-1:
            l=[op((ndarryfile(i)[:,::-1],)) for i in ndimages]
        else:
            return
    def __reverseimage(self):
        ndimages=self.getNdImages()
        ndimages.reverse()
        self.delete_image(0,-1)
        [self.after_open((ndarryfile(i),)) for i in ndimages]
    def __insertfile(self):#插入文件后覆盖之后的内容
        fileName,_ = QFileDialog.getOpenFileNames(self, "Open File",self.savedPath)
        if not fileName:return
        number=self.board.current_image.number
        self.delete_image(number-1,-1)
        self.open_files(fileName)
    def __insert_music(self):
        fileName,_ = QFileDialog.getOpenFileName(self, "Open File",self.savedPath)
        if not fileName:return
        self.text_music_label.setText(fileName+'|0.0')
    def __saveimage(self): #单独导出一张照片
        self.save(output_types="png Files (*.png);;jpg Files (*.jpg);;bmp Files (*.bmp);;All Files (*)")

    def checkRatio(self,state):
        if state == Qt.Checked:
            h=self.text_h_label.text().strip()
            w=self.text_w_label.text().strip()
            if not h or not w:
                self.ratio_value=None  #图片高宽值（h,w)
            else:
                self.ratio_value=int(h)/int(w)
            self.ratio_state=True
        else:
            self.ratio_value=None
            self.ratio_state=False
    def __setup(self):
        self.setuplabel=setupWidget(self)
        self.setuplabel.show()
    def __check_height(self,s):#获取高度值
        if not s.isdigit() or self.ratio_state is False or self.ratio_value is None:return
        s=int(s)
        self.text_w_label.setText(str(int(s/self.ratio_value)))
    def __check_width(self,s):#获取宽度值
        if not s.isdigit() or self.ratio_state is False or self.ratio_value is None:return
        s=int(s)
        self.text_h_label.setText(str(int(s*self.ratio_value)))
    def __delete_image_current(self): #删除该帧及以前的图片
        n=self.board.current_image.number
        self.delete_image(n-1,n) 

    def __delete_image_behind(self): #删除该帧及以后的图片

        self.delete_image(self.board.current_image.number-1,-1)
    def __delete_image_special(self):
        start=self.board.current_image.number
        end=len(self.board.image_list)
        text,ok3 = QInputDialog.getText(self, "删除","起始帧-结束帧:",QLineEdit.Normal, "{0}-{1}".format(start,end))
        text=text.replace(' ','').split('-')
        if len(text)!=2 or not text[0].isdigit() or not text[1].isdigit():
            QMessageBox.information(self, software_name,"输入有误！！")
            return
        start,end=text
        start,end=int(start),int(end)
        if start>end or end>len(self.board.image_list):
            QMessageBox.information(self, software_name,"输入有误！！")
            return
        self.delete_image(start-1,end)

    def __delete_image_before(self): #删除该帧及以前的图片

        self.delete_image(0,self.board.current_image.number)

    def show_right_menu(self, pos): # 重载弹出式菜单事件
        if not self.scrollArea.entered:return
        if len(self.board.image_list)==0:
            for i in self.right_act:
                i.setEnabled(False)
        else:
            for i in self.right_act:
                i.setEnabled(True)
        self.rightMenu.exec_(QCursor.pos())  
    def delete_image(self,start,end):   #删除图片range(start,end)
        print(start,end)
        if end==-1:end=len(self.board.image_list)
        if end>len(self.board.image_list) or end<start:return False
        for i in self.board.image_list[start:end]:
            i[0].hide()
        if start==0:
            p_right=0
        else:
            p_right=sum(self.board.image_list[start-1][-2:])
        for i in self.board.image_list[end:]:
            image,number,width,position=i
            image.move(p_right,0)
            i[3]=p_right
            p_right+=width
        self.board.image_list=self.board.image_list[:start]+self.board.image_list[end:]
        self.board.resize(p_right,self.board.height())
        self.release_label_useless()
        self.update_sum_frames()

    def dropEvent(self,e):
        if e.mimeData().hasUrls():
            files = [url.toLocalFile() for url in e.mimeData().urls()]
            self.open_files(files)
        else:
            e.ignore()
    def release_label_useless(self):#释放多余的qlabel 减小内存占用
        n,n0=len(self.board.image_list),len(self.board.children())
        if n0-n<25:return
        v=self.scrollArea.bar.value()
        print('release',n0-n)
        ndimages=self.getNdImages()
        self.board=self.init_board()
        self.scrollArea.setWidget(self.board)
        self.board.show()
        [self.after_open((ndarryfile(i),)) for i in ndimages]
        self.scrollArea.bar.setValue(v)
    def dragEnterEvent(self,e):
        e.accept()
    def getNdImages(self):
        return [i[0].ndimage for i in self.board.image_list]
    def save(self,testname=None,output_types="Gif Files (*.gif);;Mp4 Files (*.mp4);;Avi Files (*.avi);;All Files (*)"):
        def save_ok(a):
            self.waitmsg.close()
            if a[0]:
                QMessageBox.information(self,software_name,"成功保存了呦！")
            else:
                QMessageBox.information(self,software_name,"GG 保存出错了。\n{0}".format(a[1]))
        
        fileName,ext_f= QFileDialog.getSaveFileName(self, "Save Gif",self.savedPath,output_types)
        if not fileName:return
        self.waitmsg=waitMessage('正在保存......')
        print(fileName)
        self.savethread=SaveThread()
        self.savethread.setValue(self,fileName)
        self.savethread.trigger.connect(save_ok)
        self.savethread.start()
    def update_sum_frames(self):  
        #此函数在图片帧数发生变化时会调用  很有用
        #更新帧数，图片左上角角标，图片编码( ImageLabel.number),
        self.text_f_label.setText(str(len(self.board.image_list)))
        for i,v in enumerate(self.board.image_list):
            t=i*self.interval+1
            v[0].pages.setText(str(t))
            v[0].number=t
            v[1]=t
        if not self.board.image_list: #保存按钮的开关设置
            self.ratio_value=None
            self.setEnabled_size(False)
            return
        self.setEnabled_size(True)

        image=self.board.image_list[0][0]
        if self.ratio_value is None and self.ratio_state is True:
            self.ratio_value=image.size[1]/image.size[0]
        self.text_h_label.setText(str(image.size[1]))
        self.text_w_label.setText(str(image.size[0]))

    def display_async(self,s):
        self.after_open(s)
    def drawText(self,font,color,size,position):
        print(font,color,size,position)
        qp = QPainter()
        img=ndarryfile(img)
        img=ndarry2qimage(img)
        qp.begin(img)
        qp.setPen(color)
        font.setPixelSize(size)
        qp.setFont(font)
        qp.drawText(pos[0],pos[1],1000,1000,QtCore.Qt.AlignLeft,text)
        qp.end()
    def editGif(self,filename):
        videoreader=imageio.get_reader(filename,'ffmpeg')
        fps=videoreader.get_meta_data()['fps']
        self.videoThread=VideoReadThread()
        self.videoThread.setValue(videoreader)
        self.videoThread.trigger.connect(self.display_async)
        self.videoThread.start()
        self.text_fps_label.setText('{0:.2f}'.format(fps))
    def video2gif(self,filename):
        videoreader=imageio.get_reader(filename,'ffmpeg')
        meta_data=videoreader.get_meta_data()
        duration=meta_data['duration']
        fps0=meta_data['fps']
        k=VideoCutter().get_info(duration,fps0)
        print(k)
        if k is None:return
        else:
            start,end,fps=k
            if end<start or fps<=0:return
        end=min(duration,end)
        def v_reader(reader,p_start,p_end,fps):
            for i in range(p_start,p_end):
                t=int(i/fps)
                yield reader.get_data(t)
        n=int((end-start)*fps)
        p_start=int(start*fps)
        self.videoThread=VideoReadThread()
        self.videoThread.setValue(v_reader(videoreader,p_start,p_start+n,fps/fps0))
        self.videoThread.trigger.connect(self.display_async)
        self.videoThread.start()
        self.text_fps_label.setText('{0:.2f}'.format(fps))
        self.text_music_label.setText(filename+'|'+str(start))
    def open_files(self,files):# 对需要打开的文件进行甄别
        files=[i for i in files if path.isfile(i)]
        if not files: return
        self.savedPath=path.dirname(files[0])
        ext=path.splitext(files[0])[1]
        # print(ext)
        try:
            if len(files)==1:
                if ext.lower() in self.video_files:
                    self.video2gif(files[0])
                elif ext.lower()=='.gif':
                    self.editGif(files[0])
                elif ext.lower() in self.image_files:
                    t=imageio.imread(files[0])
                    self.after_open([t,])
                return
            else:
                self.waitmsg=waitMessage()
                for i in files:
                    t=imageio.imread(i)
                    self.after_open([t,])
                self.waitmsg.close()
        except Exception as e:
            QMessageBox.information(self,software_name,"额,打开文件出错了,请重试。\n{0}".format(e))
    def open(self):#通过打开按钮来打开文件
        fileName,_ = QFileDialog.getOpenFileNames(self, "Open File",self.savedPath)
        self.open_files(fileName)
    def after_open(self,fileName): #文件已经打开，fileName是传输进来的ndarray图像列表 
        if fileName:
            for i in fileName:
                image=ndarry2qimage(i)
                self.noImage=False  
                imageLabel=ImageLabel(self.board)
                imageLabel.setImage(image)
                imageLabel.setndimage(i)
                imageLabel.show()
            self.update_sum_frames()
    def preview(self):
        jpgs=self.getNdImages()
        jpgs=[ndarryfile(i) for i in jpgs]
        fps=self.text_fps_label.text()
        fps=float(fps)
        print(fps)
        shape=jpgs[0].shape
        x=yxspkg_songzviewer.GifPreview(None).gif((jpgs,fps,(shape[1],shape[0])))
        # x=GifPreview().preview(self)
    def cut(self):  #裁剪图片功能开始执行
        self.t=CutImageWidget.CutImageWidget()
        self.cutting_img=self.board.current_image.ndimage
        qimg=ndarry2qimage(self.cutting_img)
        self.t.setImage(qimg)
        self.t.ok_connect(self.get_cutsize)
        self.t.show()
    def update_cut(self,number):
        x1,y1,x2,y2=self.keep_size
        t=self.getNdImages()
        self.delete_image(0,-1)
        for i,img in enumerate(t):
            img=ndarryfile(img)
            if i==number-1 or number == -1:
                self.after_open((img[y1:y2,x1:x2],))
            else:
                self.after_open((img,))
    def get_cutsize(self,info):  #获取到裁剪后图片的大小
        img_geometry=info['img_geometry']
        if not info['isall']:
            number=self.board.current_image.number
        else:
            number=-1
        cutpart_geometry=info['cutpart_geometry']
        if img_geometry==cutpart_geometry:return
        x1,y1,w1,h1=img_geometry
        x2,y2,w2,h2=cutpart_geometry
        h,w=self.cutting_img.shape[:2]

        x2-=x1
        y2-=y1
        x1,y1=0,0

        x=x2/w1
        y=y2/h1 
        xx=x+w2/w1
        yy=y+h2/h1

        x,y,xx,yy=int(x*w),int(y*h),int(xx*w),int(yy*h)
        self.keep_size=x,y,xx,yy
        npos=self.board.current_image.number
        self.update_cut(number)
        self.board.current_image=self.board.image_list[npos-1][0]
        self.scrollArea.bar.setValue(self.board.image_list[npos-1][3])

    def test(self):  #测试按钮
        s=FontEditor().get_info(self)
        print(s)
def main():

    app = QApplication(sys.argv)
    gifMaker = GifMaker()
    sys.exit(app.exec_())
    return
if __name__ == '__main__':
    main()
    # print(dir(ImageFont))
    # s=ImageFont.truetype('黑体.ttf',23)
    # fname='4.jpg'
    # g=imageio.imread(fname)
    # font=QFont()
    # qp=QPainter()
    # qp.setFont(font)
    # x=TextOnImage(g,qp,(0,0),'haha')
    # imageio.imwrite(x,'sd.jpg')

    
    # print(g.shape)
    # qimage2ndarry(s)
    # print(dir(QImage))