#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pickle
from PyQt5 import QtCore, QtWidgets
from pyqtgraph.parametertree import ParameterTree, Parameter


default_params = [
    {'name': 'Beamline parameters', 'type': 'group', 'children': [
        {'name': 'mode', 'type': 'list', 'values': ['GISAXS', 'GIWAXS'], 'value': 'GISAXS'},
        {'name': 'lambda_', 'type': 'float', 'value': 1, 'suffix': u' Å', 'step': 0.1, 'title': 'Wavelength'},
        {'name': 'dist', 'type': 'float', 'value': 0.1, 'suffix': 'm', 'step': 0.1, 'siPrefix': True,
         'title': 'Distance'},
        {'name': 'x0', 'type': 'float', 'value': 100, 'suffix': ' px', 'step': 1},
        {'name': 'y0', 'type': 'float', 'value': 100, 'suffix': ' px', 'step': 1},
        {'name': 'alphai', 'type': 'float', 'value': 0, 'suffix': u'°', 'step': 0.1, 'title': u'αi'},
        {'name': 'pixel', 'type': 'float', 'value': 5e-5, 'suffix': 'm', 'step': 1e-6, 'siPrefix': True,
         'title': 'Pixel size'},
        {'name': 'qp', 'type': 'float', 'value': 0.99, 'title': 'Polarization', }
    ],
     },
    {'name': 'Sample parameters', 'type': 'group', 'children': [
        {'name': 'calibration', 'type': 'float', 'value': 1, 'step': 1e1, 'title': 'Calibration'},
        {'name': 'bkgCoef', 'type': 'float', 'value': 1, 'step': 0.1, 'title': 'Background coefficient'},
        {'name': 'thickness', 'type': 'float', 'value': 1, 'suffix': 'm', 'step': 0.1, 'siPrefix': True,
         'title': 'Thickness'},
        {'name': 'concentration', 'type': 'float', 'value': 0, 'suffix': ' g/l', 'step': 0.1, 'title': 'Concentration'},
    ],
     },
    {'name': 'Cut parameters', 'type': 'group', 'children': [
        {'name': 'cutunits', 'title': 'Cut units', 'type': 'list',
         'values': ['pixels', 'calibrated pixels', 'q', 'deg'], 'value': 'deg'},
        {'name': 'vcutsize', 'title': 'Vertical cut size', 'suffix': ' px', 'step': 1, 'type': 'int', 'value': 1,
         'limits': (1, 10000)},
        {'name': 'hcutsize', 'title': 'Horizontal cut size', 'suffix': ' px', 'step': 1, 'type': 'int', 'value': 1,
         'limits': (1, 10000)},
    ]
     }
]


class Params(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.paramtree = ParameterTree()
        layout = QtWidgets.QGridLayout()
        self.setLayout(layout)
        layout.addWidget(self.paramtree)
        self.setWindowTitle('GiuSAS parameters')

    def unpickleParams(self, params):
        if params:
            try:
                return pickle.loads(params)
            except ValueError:  # different pickle versions (usually, when run py2 after py3)
                pass
        return None

    def countParams(self, children):
        n = len(children)
        for c in children:
            n += self.countParams(c.children())
        return n

    def countDefaultParams(self, children):
        n = 0
        if isinstance(children, list):
            n += len(children)
            for c in children:
                n += self.countDefaultParams(c)
        elif isinstance(children, dict):
            if 'children' in children:
                for c in children['children']:
                    n += self.countDefaultParams(c)
            else:
                n += 1
        return n

    def loadSettings(self):
        s = QtCore.QSettings()
        self.restoreGeometry(s.value('WParams/Geometry', b''))
        params = self.unpickleParams(s.value('WParams/params', None))
        if params:
            self.params = Parameter.create(name='params', type='group')
            self.params.restoreState(params)
            if self.countParams(self.params.children()) != self.countDefaultParams(default_params):
                self.params = Parameter.create(name='params', type='group', children=default_params)
        else:
            self.params = Parameter.create(name='params', type='group', children=default_params)
        self.paramtree.setParameters(self.params, showTop=False)
        self.paramtree.setWindowTitle('GiuSAS parameters')

    def saveSettings(self):
        s = QtCore.QSettings()
        s.setValue('WParams/Geometry', self.saveGeometry())
        s.setValue('WParams/params', QtCore.QByteArray(pickle.dumps(self.params.saveState(), pickle.HIGHEST_PROTOCOL)))

    def setBeamCenter(self, x, y):
        for group in self.params:
            for child in group:
                if child.name() == 'x0':
                    child.setValue(x)
                if child.name() == 'y0':
                    child.setValue(y)
