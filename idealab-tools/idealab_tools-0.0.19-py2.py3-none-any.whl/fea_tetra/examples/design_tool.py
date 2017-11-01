# -*- coding: utf-8 -*-
"""
Created on Wed Jun 21 14:49:07 2017

@author: danaukes
"""

import PyQt5.QtGui as qg
import PyQt5.QtWidgets as qw
import PyQt5.QtCore as qc

import os
import sys
import pyqtgraph.opengl as pgo

import idealab_tools.fea_tetra.examples.tube_gravity as tg
import logging
import traceback

base = os.path.abspath(os.path.normpath(os.path.expanduser('~')))
filename = os.path.join(base,'error_log.txt')

logger = logging.Logger('design_tool',level=logging.DEBUG)
handler = logging.FileHandler(filename=filename,mode='w')
logger.addHandler(handler)  
excepthook_internal = sys.excepthook

def excepthook(exctype,value,tb):
    if exctype is not SystemExit:
        message = '''{}: {}'''.format(str(exctype),str(value))
        print(message)

        tbmessage = traceback.format_tb(tb)
        tbmessage = '  '.join(tbmessage)

        logger.error(message)
        logger.debug('\n'+tbmessage)
        
        excepthook_internal(exctype,value,tb)

class W2(pgo.GLViewWidget):
    nominal_width = 640
    nominal_height = 480
    def sizeHint(self):
        return qc.QSize(self.nominal_width, self.nominal_height)    



class Widget(qw.QWidget):
    nominal_width = 800
    nominal_height = 600
    def __init__(self):
        super(Widget,self).__init__()
        
        layout1 = qw.QHBoxLayout()
        self.text = ''
        
        self.w = W2() 
        self.button_ok = qw.QPushButton('Compute')
        self.field_diameter = qw.QLineEdit('.01')
        self.field_length = qw.QLineEdit('.1')
        self.field_youngs = qw.QLineEdit('1e6')
        self.field_poisson = qw.QLineEdit('.3')
#        w.addItem(mi)

        self.field_output = qw.QTextEdit()
        layout2 = qw.QVBoxLayout()

        
        layout1_1 = qw.QHBoxLayout()
        layout1_1.addStretch()
        layout1_1.addWidget(self.button_ok)
        layout1_1.addStretch()

        fields = self.field_diameter,self.field_length,self.field_youngs,self.field_poisson
        labels = 'diameter','length','youngs', 'poisson'
        
        for label,field in zip(labels,fields):
            layout = qw.QVBoxLayout()
            layout.addWidget(qw.QLabel(label))
            layout.addWidget(field)
            layout2.addLayout(layout)
        
        
        layout2.addStretch()
        layout2.addLayout(layout1_1)
        layout2.addWidget(self.field_output)

        layout1.addWidget(self.w)
        layout1.addLayout(layout2)
        self.setLayout(layout1)
        
        self.button_ok.clicked.connect(self.compute_outer)

    def write(self, text):
        self.text+=text
        self.field_output.setText(self.text)

    def sizeHint(self):
        buffer_x = 14
        buffer_y = 36
        return qc.QSize(self.nominal_width - buffer_x, self.nominal_height - buffer_y)    
    
    def compute_outer(self):
        diameter = float(self.field_diameter.text())
        length = float(self.field_length.text())
        poisson = float(self.field_poisson.text())
        youngs = float(self.field_youngs.text())
        mi = tg.compute(diameter,length,youngs,poisson,lcar = 0)
        self.w.addItem(mi)


if __name__=='__main__':        
    app = qg.QApplication(sys.argv)
    sys.excepthook = excepthook          


    w = Widget()    

    sys.stdout = w
    sys.stderr = w

    w.show()
    app.exec_()
    sys.exit()
