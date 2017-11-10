# -*- coding: utf-8 -*-

from functools import wraps
from quantipy import IS_SPHINX_BUILD

# Decorator/Wrapper for plotting functions to handle in which axes plot should be created
def _axes_decorator(plot_func):
    import matplotlib.pyplot as plt
    
    @wraps(plot_func)
    def _wrapped_plot_func(*args, **kwargs):
        #read axes label 'ax' from kwargs
        axes = None

        for key in kwargs:
            if key=='ax':
                axes = kwargs[key]

        if not axes:
            fig = plt.figure()
            axes = fig.gca()
            kwargs.update({'ax': axes})
        
        was_held = axes.ishold()
        try:
            axes.hold(True)
            return plot_func(*args, **kwargs)
        finally:
            axes.hold(was_held)
            
    # creates correct sphinx signature    
    return plot_func if IS_SPHINX_BUILD else _wrapped_plot_func 


def _axes_decorator_3d(plot_func):
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D
    
    @wraps(plot_func)
    def _wrapped_plot_func(*args, **kwargs):
        #read axes label 'ax' from kwargs
        axes = None

        for key in kwargs:
            if key=='ax':
                axes = kwargs[key]

        if not axes:
            fig = plt.figure()
            axes = fig.gca(projection='3d')
            kwargs.update({'ax': axes})

        return plot_func(*args, **kwargs)

    # creates correct sphinx signature
    return plot_func if IS_SPHINX_BUILD else _wrapped_plot_func

