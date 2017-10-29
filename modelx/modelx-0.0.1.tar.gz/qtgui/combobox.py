# -*- coding: utf-8 -*-
"""
Created on Wed Jul 17 10:50:56 2013

@author: cmarshall
"""
import sys

# import sip
# sip.setapi('QString', 1)
# sip.setapi('QVariant', 1)
 
import pandas as pd
# from PyQt5 import QtCore
from PyQt5.QtCore import (Qt,
                          QVariant,
                          QAbstractTableModel,
                          QModelIndex)

from PyQt5.QtWidgets import (QWidget,
                             QVBoxLayout,
                             QApplication,
                             QTableView)


class TabulatedSpace:

    def __init__(self, space):
        self._space = space

    def value_at(self, row, column):
        pass

    def get_params(self):
        pass

    def get_cells(self):
        pass

    @property
    def column_size(self):
        return len(self.get_params()) + len(self.get_cells())

    @property
    def row_size(self):
        pass

    def is_value_column(self, column_index):
        pass

    def is_key_column(self, column_index):
        pass


class SpaceTableModel(QAbstractTableModel):

    def __init__(self, space):
        super(SpaceTableModel, self).__init__()
        self._space = space
        self._cells = []
        self.update()


    def update(self):
        for cell in self._space.cells:
            pass

    def rowCount(self, parent=QModelIndex()):
        pass

    def columnCount(self, parent=QModelIndex()):
        return len(self._space.cells)

    def data(self, index, role=Qt.DisplayRole):

        if role == Qt.DisplayRole:
            i = index.row()
            j = index.column()

            # return QtCore.QVariant(str(self.datatable.iat[i, j]))
            return '{0}'.format(self.datatable.iat[i, j])

        else:
            return QVariant()

    def get_params(self):
        pass



class TableModel(QAbstractTableModel):

    def __init__(self, parent=None, *args): 
        super(TableModel, self).__init__()
        self.datatable = None

    def update(self, dataIn):
        print('Updating Model')
        self.datatable = dataIn
        print('Datatable : {0}'.format(self.datatable))

    def rowCount(self, parent=QModelIndex()):
        return len(self.datatable.index) 
        
    def columnCount(self, parent=QModelIndex()):
        return len(self.datatable.columns.values) 
        
    def data(self, index, role=Qt.DisplayRole):

        if role == Qt.DisplayRole:
            i = index.row()
            j = index.column()

            # return QtCore.QVariant(str(self.datatable.iat[i, j]))
            return '{0}'.format(self.datatable.iat[i, j])

        else:
            return QVariant()
    
    def flags(self, index):
        return Qt.ItemIsEnabled
            

class TableView(QTableView):
    """
    A simple table to demonstrate the QComboBox delegate.
    """
    def __init__(self, *args, **kwargs):
        QTableView.__init__(self, *args, **kwargs)
 
 
if __name__ == "__main__":
    # from sys import argv, exit
    
    class Widget(QWidget):
        """
        A simple test widget to contain and own the model and table.
        """
        def __init__(self, parent=None):
            QWidget.__init__(self, parent)
 
            l= QVBoxLayout(self)
            cdf = self.get_data_frame()
            self._tm=TableModel(self)
            self._tm.update(cdf)
            self._tv=TableView(self)
            self._tv.setModel(self._tm)
            l.addWidget(self._tv)
            
        def get_data_frame(self):
            df = pd.DataFrame({'Name': ['a', 'b', 'c', 'd'],
                               'First': [2.3, 5.4, 3.1, 7.7],
                               'Last': [23.4, 11.2, 65.3, 88.8],
                               'Class': [1, 1, 2, 1],
                               'Valid': [True, True, True, False]})
            return df
 
    a = QApplication(sys.argv)
    w = Widget()
    w.show()
    w.raise_()
    sys.exit(a.exec_())