'''
Created on Aug 21, 2017

@author: hammonds
'''
import unittest
from specguiutils.model.counterselectortablemodel import CounterSelectorTableModel
from specguiutils.view.counterselectorview import CounterSelectorView
from PyQt5.Qt import QSignalSpy, QApplication
import sys

COUNTER_OPTS_1 = ["X", "Y", "Z"]
COUNTER_NAMES_1 = ["A", "B", "C"]
COUNTER_NAMES_1 = ["A", "B", "C"]
COUNTER_NAMES_2 = ["D", "E", "F"]
app =  QApplication(sys.argv)

class Test(unittest.TestCase):


    def setUp(self):
        self.counterSelectorModel = CounterSelectorTableModel(counterOpts=COUNTER_NAMES_1)
        self.counterSelectorView = CounterSelectorView()
        self.counterSelectorView.setModel(self.counterSelectorModel)
        
        self.spyModelHeaderChanged = QSignalSpy(self.counterSelectorModel.headerDataChanged)

    def testInit(self):
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()