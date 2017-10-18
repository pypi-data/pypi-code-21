import numpy as np

from ... import Operation as opmod 
from ...Operation import Operation

class CSVToXYData(Operation):
    """
    Read a csv-formatted file as floats, 
    package into arrays of x values and y values.
    """

    def __init__(self):
        input_names = ['file_path']
        output_names = ['x','y','x_y']
        super(CSVToXYData, self).__init__(input_names, output_names)
        self.input_doc['file_path'] = 'path to .csv file'
        self.output_doc['x'] = 'numpy array built from first column of csv data'
        self.output_doc['y'] = 'numpy array built from second column of csv data'
        self.output_doc['x_y'] = 'n-by-2 numpy array with x and y values'

    def run(self):
        p = self.inputs['file_path']
        if p is None:
            return
        x = np.loadtxt(p, dtype=float, delimiter=',', usecols=[0])
        y = np.loadtxt(p, dtype=float, delimiter=',', usecols=[1])
        self.outputs['x'] = x
        self.outputs['y'] = y
        x_y = np.array([x,y]).T
        self.outputs['x_y'] = x_y 
        


