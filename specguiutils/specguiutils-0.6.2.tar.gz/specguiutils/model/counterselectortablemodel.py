'''
 Copyright (c) 2017, UChicago Argonne, LLC
 See LICENSE file.
'''
import PyQt5.QtCore as qtCore
import logging
logger = logging.getLogger(__name__)

COUNTER_HEADER_INIT = ['Counter',]
BLANK_ROW_NAME = '1'
BLANK_ROW_VALUE = False

class CounterSelectorTableModel(qtCore.QAbstractTableModel):

    def __init__(self,parent=None, counterOpts=None ):
        super(CounterSelectorTableModel, self).__init__(parent)
        self.counterData = [[0], ]
        self.setCounterOptions(counterOpts)
        self.initializeBlankRow()
        
    def initializeDataRows(self, counterOpts     ,scanLabels):
        logger.debug("Entering %s" % scanLabels)

        self.beginRemoveRows( qtCore.QModelIndex(), 0, self.rowCount() -1 )
        for row in range(self.rowCount()):
            self.removeRow(row)
        self.counterData = [[0], ]
        self.endRemoveRows()
        if counterOpts is not None:
            numCountOpts = len(counterOpts)
        else:
            numCountOpts = 0
        if numCountOpts != 0:
            headerLabels = None
            headerLabels = COUNTER_HEADER_INIT[:]
            headerLabels.extend(counterOpts)
            self.counterOpts = headerLabels
        else:
            self.counterOpts = COUNTER_HEADER_INIT[:]
            
        dataKeys = scanLabels
        logger.debug ("dataKeys %s" % dataKeys)
        self.beginInsertRows(qtCore.QModelIndex(), 0, len(dataKeys)-1)
        
        self.counterData = [[0 for i in range(len(self.counterOpts))] for j in range(len(scanLabels))]
        for row in range(len( dataKeys)):
            self.setRowName(row, dataKeys[row])
            for col in range(1, len(self.counterOpts)):
                self.setItem(row, col, False)
        self.endInsertRows()
        
        
    def headerData(self, col, orientation, role):
        if orientation == qtCore.Qt.Horizontal and role == qtCore.Qt.DisplayRole:
            return self.counterOpts[col]

    def initializeBlankRow(self):
        if self.counterOpts == None:
            self.counterData = [[],]
        else:
            self.counterData = [[BLANK_ROW_NAME,],]
#             print "counterOpts %s" % self.counterOpts
            if len(self.counterOpts) == 1:
                self.counterData = [[BLANK_ROW_NAME,],]
            elif len(self.counterOpts) > 1 :
                self.counterData = [[BLANK_ROW_NAME,],]
                for item in self.counterOpts[1:]:
                    self.counterData[0].append(BLANK_ROW_VALUE)
        self.insertRow(0)

        
    def setHeaderData(self, counterOpts=None):
        self.counterOpts = counterOpts
        logger.debug("counterOpts %s" % self.counterOpts)
        self.headerDataChanged.emit(qtCore.Qt.Horizontal, 0, len(self.counterOpts))
        
        
    def columnCount(self, parent=qtCore.QModelIndex()):
        return  len(self.counterOpts)
    
    def rowCount(self, parent=qtCore.QModelIndex()):
#         print("rowCount: %d" % len(self.counterData))
        return len(self.counterData)
    
    def data(self, modelIndex, role = qtCore.Qt.DisplayRole):
        if not modelIndex.isValid():
            return qtCore.QVariant()
        elif role != qtCore.Qt.DisplayRole:
            return qtCore.QVariant()
        returnData = qtCore.QVariant()
        try:
            returnData = self.counterData[modelIndex.row()][modelIndex.column()]
        except IndexError as ie:
            logger.debug( "counterData %s " % self.counterData)
            logger.debug( "row, column %d, %d" % (modelIndex.row(), modelIndex.column()))
            logger.debug(  "row values %s" % str(self.counterData[modelIndex.row()]))
            #logger.debug(  "value %s" % str(self.counterData[modelIndex.row()][modelIndex.column()]))
            raise ie
        return returnData

    
    def setCounterOptions(self, counterOpts):
#        self.counterOpts = counterOpts
        logger.debug ("setCounterOpts %s " %  counterOpts)
        if counterOpts is not None:
            numCounterOpts = len(counterOpts)
        else:
            numCounterOpts = 0
        if numCounterOpts != 0:
            headerLabels = None
            headerLabels = COUNTER_HEADER_INIT[:]
            headerLabels.extend(counterOpts)
            self.setHeaderData(headerLabels)
        else:
            #self.counterList.setColumnCount(1)
            self.setHeaderData(COUNTER_HEADER_INIT)

    def setRowName(self, row, name):
        '''
        Sets the counter name in the first coulumn of the table
        '''
        if len(self.counterData) < row+1 :
            raise(IndexError("Wrong row Number %d only %d rows" %(row, len(self.counterData)) ))
        self.counterData[row][0] = name
        self.setData(self.index(row, 0), name)
        self.dataChanged.emit(self.index(row,0), self.index(row,0))
        
    def setItem(self, row, col, value):
        '''
        Sets the item data in the table.
        '''
        if len(self.counterData) < row+1 :
            raise(IndexError(("Wrong row Number %d only %d rows.  " +
                             "Max row number %d") % 
                             (row, self.rowCount(), self.rowCount() -1) ))
        if col == 0:
            raise(IndexError("Using with Column == 1. For Col 0 use set Row Name"))
        if col > (self.columnCount() - 1):
            raise(IndexError(("Using column %d. Nuber of columns is %d. " +
                             "This column is out of bounds")))
        if not isinstance(value, bool):
            raise(ValueError("setItem, only boolean values are excepted as value"))
            
        try:
            self.counterData[row][col] = value
            self.dataChanged.emit(self.index(row,col), self.index(row,col))
        except IndexError as ie:
            print ("Index Error: trying to set self.counterData[%d][%d]" % (row, col))
            print ("len(self.counterData) %d " % len(self.counterData))
            print ("len(self.counterData[row]) %d " % len(self.counterData[row]))
            
        
        