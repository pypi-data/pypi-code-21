# -*- coding: utf-8 -*-

from pyqtgraph import QtCore, QtGui
from pywt import Modes

from skued.baseline import ALL_COMPLEX_WAV, ALL_FIRST_STAGE

from .batch import BatchProcessDialog
from .error_aware import ErrorAware


class ControlBar(QtGui.QWidget, metaclass = ErrorAware):

    baseline_parameters_signal = QtCore.pyqtSignal(dict)
    show_trim_widget = QtCore.pyqtSignal(bool)
    trim_bounds_signal = QtCore.pyqtSignal()

    raw_data_path = QtCore.pyqtSignal(str)
    export_data_path = QtCore.pyqtSignal(str)

    data_available_signal = QtCore.pyqtSignal(bool)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Files controls 
        explanation_label = QtGui.QLabel("""The data fed to dtgui should be comma-separated values files (.csv). The first column is expected to be the abscissa values, while the second column should be the ordinates.""")
        explanation_label.setWordWrap(True)
        explanation_label.setAlignment(QtCore.Qt.AlignJustify)

        load_data_btn = QtGui.QPushButton('Load data (.csv)')
        load_data_btn.clicked.connect(self.load_raw_data)

        export_bs_data_btn = QtGui.QPushButton('Export corrected data')
        export_bs_data_btn.clicked.connect(self.export_bs_data)
        export_bs_data_btn.setEnabled(False)
        self.data_available_signal.connect(export_bs_data_btn.setEnabled)

        batch_process_btn = QtGui.QPushButton('Batch process')
        batch_process_btn.clicked.connect(self.launch_batch_process)
        self.data_available_signal.connect(batch_process_btn.setEnabled)

        # Data trimming controls
        trim_label = QtGui.QLabel("Data can be trimmed. Drag the edges of the overlay. Data outside the bound will be removed.")
        trim_label.setWordWrap(True)
        trim_label.setAlignment(QtCore.Qt.AlignJustify)

        show_trim_bounds_btn = QtGui.QPushButton('Enable trim')
        show_trim_bounds_btn.setCheckable(True)
        show_trim_bounds_btn.toggled.connect(self.show_trim_widget)

        trigger_trim_btn = QtGui.QPushButton('Trim to bounds')
        trigger_trim_btn.clicked.connect(self.trim_bounds_signal)
        trigger_trim_btn.clicked.connect(lambda: show_trim_bounds_btn.setChecked(False))
        show_trim_bounds_btn.toggled.connect(trigger_trim_btn.setEnabled)
        trigger_trim_btn.setEnabled(False)

        self.first_stage_cb = QtGui.QComboBox()
        self.first_stage_cb.addItems(ALL_FIRST_STAGE)
        if 'sym6' in ALL_FIRST_STAGE:
            self.first_stage_cb.setCurrentText('sym6')

        self.wavelet_cb = QtGui.QComboBox()
        self.wavelet_cb.addItems(ALL_COMPLEX_WAV)
        if 'qshift3' in ALL_COMPLEX_WAV:
            self.wavelet_cb.setCurrentText('qshift3')

        self.mode_cb = QtGui.QComboBox()
        self.mode_cb.addItems(Modes.modes)
        if 'smooth' in Modes.modes:
            self.mode_cb.setCurrentText('constant')
        
        self.max_iter_widget = QtGui.QSpinBox()
        self.max_iter_widget.setRange(0, 1000)
        self.max_iter_widget.setValue(100)

        self.level_widget = QtGui.QSpinBox()
        self.level_widget.setMinimum(0)
        self.level_widget.setValue(1)

        self.compute_baseline_btn = QtGui.QPushButton('Compute baseline', parent = self)
        self.compute_baseline_btn.clicked.connect(lambda _: self.baseline_parameters_signal.emit(self.baseline_parameters()))

        file_controls_layout = QtGui.QVBoxLayout()
        file_controls_layout.addWidget(explanation_label)
        file_controls_layout.addWidget(load_data_btn)
        file_controls_layout.addWidget(export_bs_data_btn)
        file_controls_layout.addWidget(batch_process_btn)

        file_controls = QtGui.QGroupBox(title = 'Files', parent = self)
        file_controls.setLayout(file_controls_layout)

        data_controls_layout = QtGui.QVBoxLayout()
        data_controls_layout.addWidget(trim_label)
        btns = QtGui.QHBoxLayout()
        btns.addWidget(show_trim_bounds_btn)
        btns.addWidget(trigger_trim_btn)
        data_controls_layout.addLayout(btns)

        data_controls = QtGui.QGroupBox(title = 'Data massaging', parent = self)
        data_controls.setLayout(data_controls_layout)
        self.data_available_signal.connect(data_controls.setEnabled)

        self.baseline_controls = QtGui.QFormLayout()
        self.baseline_controls.addRow('First stage wavelet: ', self.first_stage_cb)
        self.baseline_controls.addRow('Dual-tree wavelet: ', self.wavelet_cb)
        self.baseline_controls.addRow('Extensions mode: ', self.mode_cb)
        self.baseline_controls.addRow('Iterations: ', self.max_iter_widget)
        self.baseline_controls.addRow('Decomposition level: ', self.level_widget)
        self.baseline_controls.addRow(self.compute_baseline_btn)

        self.baseline_computation = QtGui.QGroupBox(title = 'Baseline parameters', parent = self)
        self.baseline_computation.setLayout(self.baseline_controls)
        self.data_available_signal.connect(self.baseline_computation.setEnabled)

        layout = QtGui.QVBoxLayout()
        layout.addWidget(file_controls)
        layout.addWidget(data_controls)
        layout.addWidget(self.baseline_computation)
        layout.addStretch(1)

        self.setLayout(layout)
        self.resize(self.minimumSize())
        self.data_available_signal.emit(False)

    @QtCore.pyqtSlot()
    def load_raw_data(self):
        fname = QtGui.QFileDialog.getOpenFileName(parent = self, caption = 'Load data', filter = '*.csv')[0]
        if fname:
            self.raw_data_path.emit(fname)
    
    @QtCore.pyqtSlot()
    def export_bs_data(self):
        fname = QtGui.QFileDialog.getSaveFileName(parent = self, caption = 'Export data', filter = '*.csv')[0]
        if fname:
            self.export_data_path.emit(fname)
    
    @QtCore.pyqtSlot()
    def launch_batch_process(self):
        self.dialog = BatchProcessDialog(self.baseline_parameters(), parent = self)
        return self.dialog.exec_()

    def baseline_parameters(self):
        """ Returns a dictionary of baseline-computation parameters """
        return {'first_stage': self.first_stage_cb.currentText(),
                'wavelet': self.wavelet_cb.currentText(),
                'mode': self.mode_cb.currentText(),
                'max_iter': self.max_iter_widget.value(),
                'level': self.level_widget.value()}
