# -*- coding: utf-8 -*-


from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QLabel,QWidget,QApplication,QPushButton,QCheckBox
from PyQt5.QtGui import QImage,QPixmap,QCursor
import sys

filename='as.png'

class shadowLabel(QLabel):
    def __init__(self,parent):
        super().__init__(parent)
        self.parent=parent
        self.setStyleSheet('QWidget{background-color:rgba(0,0,0,80)}')
class HCutLabel(QLabel):
    LineWidth=4
    LineLength=12
    def __init__(self,parent):
        super().__init__(parent)
        self.parent=parent
        self.setStyleSheet('QWidget{background-color:rgb(0,0,0)}')
        self.resize(self.LineLength,self.LineWidth)
        self.pos_name=None
    def mousePressEvent(self,e):
        self.parent.ispressed=self.pos_name.split('_')[0]
        self.parent.wpos=QCursor.pos().x(),QCursor.pos().y()
    def mouseReleaseEvent(self,e):
        self.parent.ispressed=None
    def enterEvent(self,e):
        self.setStyleSheet('QWidget{background-color:rgb(90,90,90)}')
    def leaveEvent(self,e):
        self.setStyleSheet('QWidget{background-color:rgb(0,0,0)}')
class VCutLabel(HCutLabel):
    def __init__(self,parent):
        super().__init__(parent)
        self.resize(self.LineWidth,self.LineLength)
class radio_click_text_label(QLabel):
    def __init__(self,d):
        super().__init__(d)
        pass
class CutImageWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.cutpart=(20,20,70,70)
        self.imageLabel=QLabel(self)
        self.imageLabel.setScaledContents(True)
        self.geometry_image=self.cutpart
        # self.imageLabel.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.create_cut_tool(*self.cutpart)
        self.resize(400,400)
        self.ispressed=None
        self.MinSize=(10,10)
        self.wpos=None  #鼠标初始位置
        self.moveto(*self.cutpart)
        self.ok_button=QPushButton(self)
        self.ok_button.setGeometry(365,370,25,18)
        self.ok_button.setText('OK')
        self.ok_button.clicked.connect(self.ok_event)
        self.ok_func=lambda x:None

        self.ratiobox=QCheckBox('应用于全部',self)
        self.ratiobox.move(270,370)
        self.ratiobox.stateChanged.connect(self.checkRatio)
        self.ratiobox.toggle()  #设置默认值 self.ratio_state=True
    def checkRatio(self,state):
        if state == QtCore.Qt.Checked:
            self.ratio_state=True
        else:
            self.ratio_state=False
        print(self.ratio_state)
    def ok_event(self,e):
        self.destroy()
        x1,y1,x2,y2=self.cutpart
        self.ok_func({'img_geometry':self.geometry_image,'cutpart_geometry':(x1,y1,x2-x1,y2-y1),'isall':self.ratio_state})
    def ok_connect(self,func):
        self.ok_func=func
    def create_cut_tool(self,x1=10,y1=10,x2=70,y2=70):
        self.shadow_up=shadowLabel(self)
        self.shadow_bottom=shadowLabel(self)
        self.shadow_right=shadowLabel(self)
        self.shadow_left=shadowLabel(self)

        self.up_left_label=HCutLabel(self)
        self.up_left_label.pos_name='up_left'
        self.up_middle_label=HCutLabel(self)
        self.up_middle_label.pos_name='up_middle'
        self.up_right_label=HCutLabel(self)
        self.up_right_label.pos_name='up_right'

        self.bottom_left_label=HCutLabel(self)
        self.bottom_left_label.pos_name='bottom_left'
        self.bottom_middle_label=HCutLabel(self)
        self.bottom_middle_label.pos_name='bottom_middle'
        self.bottom_right_label=HCutLabel(self)
        self.bottom_right_label.pos_name='bottom_right'

        self.right_up_label=VCutLabel(self)
        self.right_middle_label=VCutLabel(self)
        self.right_bottom_label=VCutLabel(self)
        self.right_up_label.pos_name='right_up'
        self.right_middle_label.pos_name='right_middle'
        self.right_bottom_label.pos_name='right_bottom'

        self.left_up_label=VCutLabel(self)
        self.left_middle_label=VCutLabel(self)
        self.left_bottom_label=VCutLabel(self)
        self.left_up_label.pos_name='left_up'
        self.left_middle_label.pos_name='left_middle'
        self.left_bottom_label.pos_name='left_bottom'

    def moveto(self,x1=10,y1=10,x2=70,y2=70):
        width=HCutLabel.LineWidth
        length=HCutLabel.LineLength
        window_length,window_width=self.height(),self.width()
        mx1,my1,mx2,my2=self.geometry_image
        mx2+=mx1
        my2+=my1
        if x1<mx1:x1=mx1
        if x2>mx2:x2=mx2
        if y1<my1:y1=my1
        if y2>my2:y2=my2
        self.up_left_label.move(x1-width,y1-width)
        self.up_middle_label.move((x2+x1-length)/2,y1-width)
        self.up_right_label.move(x2+width-length,y1-width)

        self.bottom_left_label.move(x1-width,y2)
        self.bottom_middle_label.move((x2+x1-length)/2,y2)
        self.bottom_right_label.move(x2+width-length,y2)

        self.right_up_label.move(x2,y1-width)
        self.right_middle_label.move(x2,(y2+y1-length)/2)
        self.right_bottom_label.move(x2,y2+width-length)

        self.left_up_label.move(x1-width,y1-width)
        self.left_middle_label.move(x1-width,(y2+y1-length)/2)
        self.left_bottom_label.move(x1-width,y2+width-length)

        self.shadow_up.setGeometry(0,0,window_width,y1)
        self.shadow_bottom.setGeometry(0,y2,window_width,window_length-y2)
        self.shadow_left.setGeometry(0,y1,x1,y2-y1)
        self.shadow_right.setGeometry(x2,y1,window_width-x2,y2-y1)
        self.cutpart=x1,y1,x2,y2
        self.sizeChangeEvent({'img_geometry':self.geometry_image,'cutpart_geometry':(x1,y1,x2-x1,y2-y1)})
    def mouseMoveEvent(self,e):
        if not self.ispressed:return
        wpos=self.wpos
        mpos=QCursor.pos().x(),QCursor.pos().y()
        x,y=mpos[0]-wpos[0],mpos[1]-wpos[1]
        x1,y1,x2,y2=self.cutpart
        if self.ispressed == 'left':
            if 0==x or x2-x1-x<=self.MinSize[0] or x1+x<self.geometry_image[0]:return
            else:x1+=x
        elif self.ispressed == 'right':
            if 0==x or x2+x-x1<=self.MinSize[0] or x2+x>self.geometry_image[0]+self.geometry_image[2]:return
            else:x2+=x
        elif self.ispressed =='up':
            if 0==y or y2-y-y1<=self.MinSize[1] or y1+y<self.geometry_image[1]:return
            else:y1+=y
        elif self.ispressed == 'bottom':
            if 0==y or y2+y-y1<=self.MinSize[1] or y2+y>self.geometry_image[1]+self.geometry_image[3]:return
            else:y2+=y
        self.wpos=mpos
        self.moveto(x1,y1,x2,y2)
    def setImage(self,qimage,geometry=None,ratio=0.8):
        self.imageLabel.setPixmap(QPixmap.fromImage(qimage))
        height_window,width_window=self.height(),self.width()
        height_image,width_image=qimage.height(),qimage.width()
        if geometry is None:
            height=height_window*ratio
            width=height/height_image*width_image
            if width>ratio*width_window:
                width=width_window*ratio
                height=width/width_image*height_image
            x=(width_window-width)/2
            y=(height_window-height)/2
            geometry=(int(x),int(y),int(width),int(height))
        self.geometry_image=geometry
        self.imageLabel.setGeometry(*geometry)
        self.moveto(geometry[0],geometry[1],geometry[0]+geometry[2],geometry[1]+geometry[3])

    def sizeChangeEvent(self,e):
        pass

if __name__=='__main__':
    app=QApplication(sys.argv)
    tw=CutImageWidget()
    tw.setImage(QImage('F:\\pythonAPP\\gif_maker\\1.png'))
    tw.show()
    app.exec_()
