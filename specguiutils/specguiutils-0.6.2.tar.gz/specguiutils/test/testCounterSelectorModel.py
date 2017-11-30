'''
 Copyright (c) 2017, UChicago Argonne, LLC
 See LICENSE file.
'''
import sys
import unittest 
from PyQt5.QtTest import QSignalSpy
from PyQt5.QtWidgets import QApplication
import PyQt5.QtCore as qtCore
import specguiutils.model.counterselectortablemodel as tableModel
from  specguiutils.model.counterselectortablemodel import CounterSelectorTableModel
import logging
logger = logging.getLogger(__name__)

app =  QApplication(sys.argv)
COUNTER_OPTS_1 = ["X", "Y", "Z"]
COUNTER_OPTS_2 = ["W", "X", "Y", "Z"]
COUNTER_NAMES_1 = ["A", "B", "C"]
COUNTER_NAMES_2 = ["D", "E", "F"]

class CounterSelectorTableModelTest(unittest.TestCase):
    def setUp(self):
        self.model = CounterSelectorTableModel(parent=None, counterOpts=COUNTER_OPTS_1)
        
    def testInit(self):
        self.assertEqual(self.model.columnCount(), 4)
        self.assertEqual(self.model.rowCount(), 1)
        self.assertEqual(len(self.model.counterData), 1)
        self.assertEqual(len(self.model.counterData[0]), 4)
        logger.debug("self.model.counterData %s", self.model.counterData)
        index = self.model.index(0, 0)
        self.assertEqual(self.model.data(index), tableModel.BLANK_ROW_NAME)
        index = self.model.index(0, 1)
        self.assertEqual(self.model.data(index), tableModel.BLANK_ROW_VALUE)
        index = self.model.index(0, 2)
        self.assertEqual(self.model.data(index), tableModel.BLANK_ROW_VALUE)
        index = self.model.index(0, 3)
        self.assertEqual(self.model.data(index), tableModel.BLANK_ROW_VALUE)
        index = self.model.index(0, 4)
        data = self.model.data(index)
        self.assertFalse(data.isValid())
        index = self.model.index(1, 4)
        data = self.model.data(index)
        self.assertFalse(data.isValid())
        label = self.model.headerData(0, qtCore.Qt.Horizontal, \
                                      role=qtCore.Qt.DisplayRole)
        self.assertEqual(label, tableModel.COUNTER_HEADER_INIT[0])
    
    def testInitializeRows1(self):
        self.model.initializeDataRows(COUNTER_OPTS_1, COUNTER_NAMES_1)
        index = self.model.index(0, 0)
        self.assertEqual(self.model.data(index), COUNTER_NAMES_1[0])
        index = self.model.index(0, 1)
        self.assertEqual(self.model.data(index), tableModel.BLANK_ROW_VALUE)
        index = self.model.index(0, 2)
        self.assertEqual(self.model.data(index), tableModel.BLANK_ROW_VALUE)
        index = self.model.index(0, 3)
        self.assertEqual(self.model.data(index), tableModel.BLANK_ROW_VALUE)
        index = self.model.index(0, 4)
        data = self.model.data(index)
        self.assertFalse(data.isValid())
        index = self.model.index(1, 0)
        self.assertEqual(self.model.data(index), COUNTER_NAMES_1[1])
        index = self.model.index(1, 1)
        self.assertEqual(self.model.data(index), tableModel.BLANK_ROW_VALUE)
        index = self.model.index(1, 2)
        self.assertEqual(self.model.data(index), tableModel.BLANK_ROW_VALUE)
        index = self.model.index(1, 3)
        self.assertEqual(self.model.data(index), tableModel.BLANK_ROW_VALUE)
        index = self.model.index(1, 4)
        data = self.model.data(index)
        self.assertFalse(data.isValid())
        index = self.model.index(2, 0)
        self.assertEqual(self.model.data(index), COUNTER_NAMES_1[2])
        index = self.model.index(2, 1)
        self.assertEqual(self.model.data(index), tableModel.BLANK_ROW_VALUE)
        index = self.model.index(2, 2)
        self.assertEqual(self.model.data(index), tableModel.BLANK_ROW_VALUE)
        index = self.model.index(2, 3)
        self.assertEqual(self.model.data(index), tableModel.BLANK_ROW_VALUE)
        index = self.model.index(2, 4)
        data = self.model.data(index)
        self.assertFalse(data.isValid())
        index = self.model.index(3, 0)
        data = self.model.data(index)
        self.assertFalse(data.isValid())
        index = self.model.index(3, 1)
        data = self.model.data(index)
        self.assertFalse(data.isValid())
        index = self.model.index(3, 2)
        data = self.model.data(index)
        self.assertFalse(data.isValid())
        index = self.model.index(3, 3)
        data = self.model.data(index)
        self.assertFalse(data.isValid())
        
    def testInitializeRows2(self):
        self.model.initializeDataRows(COUNTER_OPTS_2, COUNTER_NAMES_2)
        index = self.model.index(0, 0)
        self.assertEqual(self.model.data(index), COUNTER_NAMES_2[0])
        index = self.model.index(0, 1)
        self.assertEqual(self.model.data(index), tableModel.BLANK_ROW_VALUE)
        index = self.model.index(0, 2)
        self.assertEqual(self.model.data(index), tableModel.BLANK_ROW_VALUE)
        index = self.model.index(0, 3)
        self.assertEqual(self.model.data(index), tableModel.BLANK_ROW_VALUE)
        index = self.model.index(0, 4)
        self.assertEqual(self.model.data(index), tableModel.BLANK_ROW_VALUE)
        index = self.model.index(0, 5)
        data = self.model.data(index)
        self.assertFalse(data.isValid())
        index = self.model.index(1, 0)
        self.assertEqual(self.model.data(index), COUNTER_NAMES_2[1])
        index = self.model.index(1, 1)
        self.assertEqual(self.model.data(index), tableModel.BLANK_ROW_VALUE)
        index = self.model.index(1, 2)
        self.assertEqual(self.model.data(index), tableModel.BLANK_ROW_VALUE)
        index = self.model.index(1, 3)
        self.assertEqual(self.model.data(index), tableModel.BLANK_ROW_VALUE)
        index = self.model.index(1, 4)
        self.assertEqual(self.model.data(index), tableModel.BLANK_ROW_VALUE)
        index = self.model.index(1, 5)
        data = self.model.data(index)
        self.assertFalse(data.isValid())
        index = self.model.index(2, 0)
        self.assertEqual(self.model.data(index), COUNTER_NAMES_2[2])
        index = self.model.index(2, 1)
        self.assertEqual(self.model.data(index), tableModel.BLANK_ROW_VALUE)
        index = self.model.index(2, 2)
        self.assertEqual(self.model.data(index), tableModel.BLANK_ROW_VALUE)
        index = self.model.index(2, 3)
        self.assertEqual(self.model.data(index), tableModel.BLANK_ROW_VALUE)
        index = self.model.index(2, 4)
        self.assertEqual(self.model.data(index), tableModel.BLANK_ROW_VALUE)
        index = self.model.index(2, 5)
        data = self.model.data(index)
        self.assertFalse(data.isValid())
        index = self.model.index(3, 0)
        data = self.model.data(index)
        self.assertFalse(data.isValid())
        index = self.model.index(3, 1)
        data = self.model.data(index)
        self.assertFalse(data.isValid())
        index = self.model.index(3, 2)
        data = self.model.data(index)
        self.assertFalse(data.isValid())
        index = self.model.index(3, 3)
        data = self.model.data(index)
        self.assertFalse(data.isValid())
        index = self.model.index(3, 4)
        data = self.model.data(index)
        self.assertFalse(data.isValid())
        
    def testSetRowName1(self):
        self.model.initializeDataRows(COUNTER_OPTS_2, COUNTER_NAMES_2)
        spy = QSignalSpy(self.model.dataChanged)
        ROW_NAME_1 = "ISetThis"
        ROW_NAME_2 = "ThisToo"
        ROW_NAME_3 = "CantDoThis"
        self.model.setRowName(0,ROW_NAME_1)
        dataChangedData = spy[0][0]
        with self.assertRaises(IndexError):
            spy[1]
        self.assertEqual(dataChangedData.row(), 0)
        self.assertEqual(dataChangedData.column(), 0)
        self.assertEqual(dataChangedData.data(), ROW_NAME_1)
        logger.debug("Contents of QSignalSpy %s %s %s" % (spy[0][0].row(),spy[0][0].column(),spy[0][0].data()) )
        self.model.setRowName(1,ROW_NAME_2)
        dataChangedData = spy[1][0]
        with self.assertRaises(IndexError):
            spy[2]
        self.assertEqual(dataChangedData.row(), 1)
        self.assertEqual(dataChangedData.column(), 0)
        self.assertEqual(dataChangedData.data(), ROW_NAME_2)
        self.model.setRowName(2,ROW_NAME_2) 
        with self.assertRaises(IndexError):
            self.model.setRowName(3,ROW_NAME_2) 
        with self.assertRaises(IndexError):
            self.model.setRowName(4,ROW_NAME_2) 
        self.assertEqual(len(spy), 3)

    def testSetItem(self):
        self.model.initializeDataRows(COUNTER_OPTS_2, COUNTER_NAMES_2)
        spy = QSignalSpy(self.model.dataChanged)
        self.model.setItem(0,2,True)
        self.assertEqual(len(spy), 1)
        self.model.setItem(1,2,True)
        self.assertEqual(len(spy), 2)
        self.model.setItem(2,2,True)
        self.assertEqual(len(spy), 3)
        with self.assertRaises(IndexError):
            self.model.setItem(3,2,True)
        with self.assertRaises(IndexError):
            self.model.setItem(0,5,True)
        with self.assertRaises(IndexError):
            self.model.setItem(1,0,True)
        with self.assertRaises(ValueError):
            self.model.setItem(1,1,0)
        with self.assertRaises(ValueError):
            self.model.setItem(1,1,"True")
        with self.assertRaises(ValueError):
            self.model.setItem(1,3,3.54)
        with self.assertRaises(ValueError):
            self.model.setItem(1,3,(3,2))
        self.assertEqual(len(spy), 3)
        