import numpy as np

from .. import Operation as opmod 
from ..Operation import Operation

class WindowZip(Operation):
    """
    From input sequences for x and y, 
    produce an n-by-2 array 
    where x is bounded by the specified limits 
    """

    def __init__(self):
        input_names = ['x','y','x_min','x_max']
        output_names = ['x_window','y_window','x_y_window']
        super(WindowZip,self).__init__(input_names,output_names)        
        self.input_type['x'] = opmod.workflow_item
        self.input_type['y'] = opmod.workflow_item
        self.input_doc['x'] = 'array of x values'
        self.input_doc['y'] = 'array of y values'
        self.input_doc['x_min'] = 'inclusive minimum x value of output'
        self.input_doc['x_max'] = 'inclusive maximum x value of output'
        self.output_doc['x_window'] = 'array of x for x_min <= x <= x_max'
        self.output_doc['y_window'] = 'array of y for x_min <= x <= x_max'
        self.output_doc['x_y_window'] = 'n-by-2 array with x, y pairs for x_min <= x <= x_max'

    def run(self):
        xvals = self.inputs['x']
        yvals = self.inputs['y']
        x_min = self.inputs['x_min']
        x_max = self.inputs['x_max']
        idx_keep = ((xvals >= x_min) & (xvals <= x_max))
        x_y_window = np.array(zip(xvals[idx_keep],yvals[idx_keep]))
        self.outputs['x_window'] = x_y_window[:,0]
        self.outputs['y_window'] = x_y_window[:,1]
        self.outputs['x_y_window'] = x_y_window

