from PyQt5 import QtGui, QtCore,QtWidgets,uic

#from pySAXS.guisaxs.qt import dlgConcatenateui
from pySAXS.tools import isNumeric
from pySAXS.guisaxs import dataset
import numpy
import pySAXS

class DataElement():
    enabled=True
    qmin=0.0
    qmax=1.1
    def __init__(self,enabled,qmin,qmax):
        self.enabled=enabled
        self.qmin=qmin
        self.qmax=qmax

class dlgConcatenate(QtWidgets.QDialog):#,dlgConcatenateui.Ui_concatenateDialog):
    def __init__(self,parentwindow,newdatasetname=''):
        QtWidgets.QDialog.__init__(self)
        self.ui = uic.loadUi(pySAXS.UI_PATH+"dlgConcatenate.ui", self)#
        self.parentwindow=parentwindow
        self.data_dict=parentwindow.data_dict
        self.newdatasetname=newdatasetname
        self.mydata={}
        self.dataInWidget=[]
        # Set up the user interface from Designer.
        #self.setupUi(self)
        #construct UI
        self.ConstructUI()
        #QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("clicked(QAbstractButton*)"), self.click)#connect buttons signal
        self.ui.buttonBox.clicked.connect(self.click)
        self.pushButtonDOWN.clicked.connect(self.OnPushButtonDOWNclicked)
        self.pushButtonUP.clicked.connect(self.OnPushButtonUPclicked)
        self.tableWidget.cellChanged.connect(self.OnCellChanged)
        #QtCore.QObject.connect(self.tableWidget, QtCore.SIGNAL("itemActivated(QTableWidgetItem*)"), self.activated)#connect buttons signal
        
    def ConstructUI(self):
        self.lineEditNewName.setText(self.newdatasetname)
        for label in self.data_dict:
            if self.data_dict[label].checked:
                self.dataInWidget.append(label)
                qmin=self.data_dict[label].q.min()
                qmax=self.data_dict[label].q.max()
                self.mydata[label]=DataElement(True,qmin,qmax)
        
        #self.dataInWidget=self.listofdata
        self.ConstructTableWidget()
        
    def ConstructTableWidget(self):
        #print self.dataInWidget
        #for testing construct TableWidget
        self.tableWidget.clearContents()
        m = 0
        self.tableWidget.setRowCount(len(self.dataInWidget))
        for label in self.dataInWidget:
            #print label,m
            vitem = QtWidgets.QTableWidgetItem()
            vitem.setText(label)
            self.tableWidget.setVerticalHeaderItem(m, vitem)
            newitem = QtWidgets.QTableWidgetItem('')
            newitem.setCheckState(QtCore.Qt.Checked)
            self.tableWidget.setItem(m, 0, newitem)
            newitem = QtWidgets.QTableWidgetItem(str(self.mydata[label].qmin))
            self.tableWidget.setItem(m, 1, newitem)
            newitem = QtWidgets.QTableWidgetItem(str(self.mydata[label].qmax))
            self.tableWidget.setItem(m, 2, newitem)
            m+=1
            
    
    def OnCellChanged(self,row=None,column=None):
        if row is None or column is None:
            return
        label=self.dataInWidget[row]
        val=str(self.tableWidget.item(row,column).text())
        if column==0:
            #check box
            self.mydata[label].enabled=(self.tableWidget.item(row,column).checkState()==2)
            #5print self.mydata[label].enabled
            return
        if not isNumeric.isNumeric(val):
            #print 'value is not numeric'
            brush = QtGui.QBrush(QtGui.QColor(QtCore.Qt.cyan))
            brush.setStyle(QtCore.Qt.SolidPattern)
            self.tableWidget.item(row,column).setBackground(brush)
            return
        val=float(val)
        if column==1:
            #qmin
            self.mydata[label].qmin=val
            #print 'setqmin'
        elif column==2:
            #qmax
            #print 'setqmax'
            self.mydata[label].qmax=val
        brush = QtGui.QBrush(QtGui.QColor(QtCore.Qt.white))
        brush.setStyle(QtCore.Qt.SolidPattern)
        self.tableWidget.item(row,column).setBackground(brush)
    
    def click(self,obj=None):
        '''
        user clicked on the button box
        '''
        name=obj.text()
        #print name
        if name=="OK":
            self.close()
        elif name=="Apply":
            #compute
            self.concatenateDatas()
            #get new name
            self.newdatasetname=str(self.lineEditNewName.text())
            #apply
            self.parentwindow.data_dict[self.newdatasetname]=dataset.dataset(self.newdatasetname,self.newdatasetq,self.newdataseti,error=self.newdatasete)
            self.parentwindow.redrawTheList()
            self.parentwindow.Replot()
            
        else:
            #Close
            self.close()
    
    def OnPushButtonDOWNclicked(self):
        #which cell is activated ?
        row= self.tableWidget.currentRow()
        print row
        if row<0:
            return
        if row>=len(self.dataInWidget)-1:
            return
        #exchange rows
        temp=self.dataInWidget[row]
        self.dataInWidget[row]=self.dataInWidget[row+1]
        self.dataInWidget[row+1]=temp
        self.ConstructTableWidget()
        self.tableWidget.setCurrentCell (row+1,0)
        
    def OnPushButtonUPclicked(self):
        #which cell is activated ?
        row= self.tableWidget.currentRow()
        print row
        if row<=0:
            return
        #exchange rows
        temp=self.dataInWidget[row]
        self.dataInWidget[row]=self.dataInWidget[row-1]
        self.dataInWidget[row-1]=temp
        self.ConstructTableWidget()
        self.tableWidget.setCurrentCell(row-1,0)
    
    def concatenateDatas(self):
        '''
        create the new datas
        '''
        #how to know order of data
        #in the new version, I know the order
        ''''d={} #dict with key = qmin val=datasetname
        for name in self.listofdata:
            if self.listCheckBox[name].isChecked():
                #print "using ",name
                val=float(str(self.listTextCtrlqmin[name].getText()))
                if d.has_key(val):
                    print "Error, can not create datas, different datas have same qmin"
                    return
                d[val]=name
        l=d.keys() #l : list of sorted qmin
        l.sort()
        print l
        dataset=d[l[0]]
        '''
        
        first=True
        for label in self.mydata:
            dataset=self.mydata[label]
            if dataset.enabled:
                newq,newi,newe=self.clipDatas(label,dataset.qmin,dataset.qmax)# clip
                if first:
                    self.newdatasetq=newq
                    self.newdataseti=newi
                    self.newdatasete=newe
                    first=False
                else:
                    #concatenate with previous datas
                    self.newdatasetq=numpy.concatenate((self.newdatasetq,newq))
                    self.newdataseti=numpy.concatenate((self.newdataseti,newi))
                    self.newdatasete=numpy.concatenate((self.newdatasete,newe))
        #sort arrays
        sortedIndexes=numpy.argsort(self.newdatasetq)
        self.newdatasetq=self.newdatasetq[sortedIndexes]
        self.newdataseti=self.newdataseti[sortedIndexes]
        self.newdatasete=self.newdatasete[sortedIndexes]
    
    def clipDatas(self,datasetname,qmin,qmax):
        '''
        return q and i clipped
        '''
        q=self.data_dict[datasetname].q
        i=self.data_dict[datasetname].i
        e=self.data_dict[datasetname].error
        i=numpy.repeat(i,(q>=qmin)&(q<=qmax))
        q=numpy.repeat(q,(q>=qmin)&(q<=qmax))
        e=numpy.repeat(e,(e>=qmin)&(e<=qmax))
        #i=numpy.repeat(i,q<=qmax)
        #q=numpy.repeat(q,q<=qmax)
        return q,i,e
    
    def getValues(self):
        return self.listCheckBox,   self.listlabel0,   self.listQmin,  self.listQmax