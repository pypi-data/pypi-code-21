#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ExportMarkerCountToXLS.py

# Copyright (c) 2015-2016, Richard Gerum, Sebastian Richter
#
# This file is part of ClickPoints.
#
# ClickPoints is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ClickPoints is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ClickPoints. If not, see <http://www.gnu.org/licenses/>

from __future__ import division, print_function
import xlwt
import clickpoints
from clickpoints.includes.QtShortCuts import AddQComboBox, AddQSaveFileChoose
from qtpy import QtCore, QtGui, QtWidgets
import numpy as np
from clickpoints.includes.matplotlibwidget import MatplotlibWidget

class Addon(clickpoints.Addon):
    def __init__(self, *args, **kwargs):
        clickpoints.Addon.__init__(self, *args, **kwargs)
        # set the title and layout
        self.setWindowTitle("Westernblot - ClickPoints")
        self.layout = QtWidgets.QVBoxLayout(self)

        # add a file chooser for the output
        #self.line_edit_file = AddQSaveFileChoose(layout, "Path", value=self.db._database_filename.replace('.cdb', '.xls'), file_type="Excel Workbook (*.xls)")
        # add a mode selector, which formatting should be used for the output
        #self.combo_style = AddQComboBox(layout, "Mode", values=["Marker Count", "Marker Positions", "Track Positions"])

        self.tableWidget = QtWidgets.QTableWidget(0, 4, self)
        self.layout.addWidget(self.tableWidget)
        self.row_headers = ["Type", "Line", "Value", "Reference"]
        self.tableWidget.setHorizontalHeaderLabels(self.row_headers)
        self.tableWidget.setMinimumHeight(180)
        self.setMinimumWidth(500)
        self.tableWidget.setCurrentCell(0, 0)

        self.my_type = self.db.setMarkerType("bar", "#FFFF00", self.db.TYPE_Rect)

        self.plot = MatplotlibWidget(self)
        self.layout.addWidget(self.plot)

        self.button_run = QtWidgets.QPushButton("Export")
        self.button_run.clicked.connect(self.run)
        self.layout.addWidget(self.button_run)

        self.tableWidget.itemChanged.connect(self.itemChanged)

        self.updateTable()

    def itemChanged(self, item):
        if self.updateing:
            return
        bar = self.bars[item.row()]
        if item.column() == 0:
            bar.extra_data[0] = item.text()
        elif item.column() == 1:
            bar.extra_data[1] = item.text()
        elif item.column() == 3:
            bar.extra_data[2] = int(item.text())
        bar.text = "%s,%s,[%d]" % tuple(bar.extra_data)
        bar.save()

    def setTableText(self, row, column, text):
        if column == -1:
            item = self.tableWidget.verticalHeaderItem(row)
            if item is None:
                item = QtWidgets.QTableWidgetItem("")
                self.tableWidget.setVerticalHeaderItem(row, item)
        else:
            item = self.tableWidget.item(row, column)
            if item is None:
                item = QtWidgets.QTableWidgetItem("")
                self.tableWidget.setItem(row, column, item)
                if column == 2:
                    item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        item.setText(str(text))

    def updateTable(self):
        self.updateing = True
        bars = self.db.getRectangles(type=self.my_type)
        self.bars = [bar for bar in bars]
        self.bar_dict = {}
        self.tableWidget.setRowCount(bars.count())
        self.last_image_id = None
        for idx, bar in enumerate(bars):
            self.updateRow(idx)
            self.bar_dict[bar.id] = idx
        self.updateing = False

    def updateRow(self, idx):
        bar = self.bars[idx]
        if bar.image_id != self.last_image_id:
            self.last_image_id = bar.image_id
            self.image = bar.image.data
        extra = bar.text.split(",") if bar.text else []
        if len(extra) == 3:
            bar.extra_data = extra
            bar.extra_data[2] = int(bar.extra_data[2][1:-1])
        else:
            bar.extra_data = ["", "", 0]
        bar.value = self.calculateBar(self.image[bar.slice_y(), bar.slice_x()])
        self.setTableText(idx, -1, "#%d" % bar.id)
        self.setTableText(idx, 0, bar.extra_data[0])
        self.setTableText(idx, 1, bar.extra_data[1])
        self.setTableText(idx, 2, bar.value)
        self.setTableText(idx, 3, bar.extra_data[2])

    def updatePlot(self):
        rows = []
        columns = []
        data = np.zeros((0, 0))
        for bar in self.bars:
            if bar.extra_data[0] == "" or bar.extra_data[1] == "" or bar.extra_data[2] == 0:
                continue
            try:
                reference = self.bars[self.bar_dict[bar.extra_data[2]]]
            except IndexError:
                continue
            if bar.extra_data[0] not in rows:
                rows.append(bar.extra_data[0])
                data = np.vstack((data, np.zeros((1, data.shape[1]))))
            if bar.extra_data[1] not in columns:
                columns.append(bar.extra_data[1])
                data = np.hstack((data, np.zeros((data.shape[0], 1))))
            i = rows.index(bar.extra_data[0])
            j = columns.index(bar.extra_data[1])
            data[i, j] = bar.value / reference.value
        self.plot.axes.clear()
        width = 1/(len(rows)+1)
        for idx, row in enumerate(rows):
            self.plot.axes.bar(np.arange(len(columns))+width*idx, data[idx, :], label=row, width=width*0.9)
        self.plot.axes.legend()
        self.plot.axes.set_xticks(np.arange(len(columns))+width*len(rows)/2-width/2)
        self.plot.axes.set_xticklabels(columns)
        self.plot.draw()

    def calculateBar(self, data):
        if data.shape[0] == 0 or data.shape[1] == 0:
            return
        return np.sum(data)-np.min(data)

    def markerMoveEvent(self, entry):
        if entry.type == self.my_type:
            row = self.bar_dict[entry.id]
            self.bars[row] = entry
            self.tableWidget.selectRow(row)
            self.updateRow(row)
            #marker.data.text = "%.2f %s" % (marker.data.length()*self.getOption("pixelSize"), self.getOption("unit"))
            #marker.data.save()

    def markerAddEvent(self, entry):
        self.updateTable()

    def markerRemoveEvent(self, entry):
        self.updateTable()

    def buttonPressedEvent(self):
        self.show()

    def run(self, start_frame=0):
        self.updateTable()
        self.updatePlot()
        return
        # prepare write to excel
        wb_name = self.line_edit_file.text()
        wb = xlwt.Workbook()

        # List Marker Count
        if self.combo_style.currentIndex() == 0:
            self.exportMarkerCount(wb)
        # List Marker Positions
        if self.combo_style.currentIndex() == 1:
            self.exportMarkerPositions(wb)
        # List Track Positions
        if self.combo_style.currentIndex() == 2:
            self.exportTrackPositions(wb)

        print("Writing to %s" % wb_name)
        try:
            wb.save(wb_name)
        except PermissionError as err:
            QtWidgets.QMessageBox.critical(self, 'Error - ClickPoints',
                                           '%s\n\nMaybe the file is still open in Excel. Please close it and try again.' % err,
                                           QtWidgets.QMessageBox.Ok)
            raise err
        QtWidgets.QMessageBox.information(self, 'Add-on - ClickPoints',
                                          'Data saved to %s.' % wb_name, QtWidgets.QMessageBox.Ok)
        print("DONE")
