# -*- coding: utf-8 -*-
import os.path

import configparser
import numpy as np
from pyqtgraph import QtCore, QtGui

from skued import baseline_dt


class BatchProcessDialog(QtGui.QDialog):

    processing_update_signal = QtCore.pyqtSignal(int)

    def __init__(self, baseline_params, *args, **kwargs):
        """
        Parameters
        ----------
        baseline_params : dict
            Dictionary of parameters passed to baseline_dt.
        """
        self.files = list()
        self.baseline_params = baseline_params

        super().__init__(**kwargs)
        self.setModal(True)
        self.setWindowTitle('Batch baseline-removal')

        self.file_table = QtGui.QListWidget(parent = self)
        
        self.progress_bar = QtGui.QProgressBar(parent = self)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.processing_update_signal.connect(self.progress_bar.setValue)

        explanation = QtGui.QLabel("""Select files to be baseline-subtracted according to the parameters set in the previous screen. The files will be processed and stored in a directory of your choosing, along with a configuration file (.cfg) specifying the parameters used.""")
        explanation.setWordWrap(True)
        explanation.setAlignment(QtCore.Qt.AlignCenter)

        file_search_btn = QtGui.QPushButton('Add file(s) to batch', self)
        file_search_btn.clicked.connect(self.add_spectra)

        clear_btn = QtGui.QPushButton('Clear files', self)
        clear_btn.clicked.connect(self.clear)

        accept_btn = QtGui.QPushButton('Process', self)
        accept_btn.clicked.connect(self.accept)

        reject_btn = QtGui.QPushButton('Cancel', self)
        reject_btn.clicked.connect(self.reject)
        reject_btn.setDefault(True)

        btns = QtGui.QHBoxLayout()
        btns.addWidget(file_search_btn)
        btns.addWidget(clear_btn)
        
        controls = QtGui.QHBoxLayout()
        controls.addWidget(accept_btn)
        controls.addWidget(reject_btn)

        layout = QtGui.QVBoxLayout()
        layout.addWidget(explanation)
        layout.addLayout(btns)
        layout.addWidget(self.file_table)
        layout.addWidget(self.progress_bar)
        layout.addLayout(controls)
        self.setLayout(layout)
    
    @QtCore.pyqtSlot()
    def add_spectra(self):
        paths = QtGui.QFileDialog.getOpenFileNames(self, caption = 'Select one or more spectra', filter = '*.csv')[0]
        
        if paths:
            self.files.extend(paths)
            self.file_table.addItems(paths)
    
    @QtCore.pyqtSlot()
    def clear(self):
        self.file_table.clear()
        self.files.clear()
    
    @QtCore.pyqtSlot()
    def accept(self):

        directory = QtGui.QFileDialog.getExistingDirectory(self, 'Select a directory in which to save the processed files')
        if not directory:
            return

        self.progress_bar.setRange(0, len(self.files))
            
        for index, file in enumerate(self.files, start = 1):
            wavenumbers, counts = np.loadtxt(file, delimiter = ',', unpack = True)
            baseline = baseline_dt(counts, **self.baseline_params)

            # Assemble the result into two columns: wavenumbers first, then baseline-corrected counts
            arr = np.empty(shape = (wavenumbers.size, 2))
            arr[:,0] = wavenumbers
            arr[:,1] = counts - baseline

            # Determine the location of the processed file
            base = os.path.basename(file)
            processed_fname = os.path.join(directory, 'bs_' + base)
            np.savetxt(processed_fname, arr, delimiter = ',')

            self.processing_update_signal.emit(index)
        
        # Write baseline parameters into a configuration file
        config = configparser.ConfigParser()
        config['BASELINE PARAMETERS'] = self.baseline_params
        with open(os.path.join(directory, 'baseline_parameters.txt'), mode = 'w') as configfile:
            config.write(configfile)

        super().accept()
