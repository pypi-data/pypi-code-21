# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes
Email: danaukes<at>gmail.com
Please see LICENSE for full license.
"""
import numpy
import pynamics

import logging
logger = logging.getLogger('pynamics.output')

class Output(object):
    def __init__(self,y_exp, system=None, constant_values = None):
        import sympy
        system = system or pynamics.get_system()

        constant_values = constant_values or system.constant_values
        self.y_expression = sympy.Matrix(y_exp)
        cons_s = list(constant_values.keys())
        self.cons_v = [constant_values[key] for key in cons_s]
        self.fy_expression = sympy.lambdify(system.get_state_variables()+cons_s,self.y_expression)

    def calc(self,x):
        logger.info('calculating outputs')
        self.y = numpy.array([self.fy_expression(*(item.tolist()+self.cons_v)) for item in x]).squeeze()
        logger.info('done calculating outputs')
        return self.y

    def plot_time(self,t=None):
        import matplotlib.pyplot as plt
        plt.figure()
        try:
            self.y
        except AttributeError:
            self.calc()
        if t is None:
            plt.plot(self.y)
        else:
            plt.plot(t,self.y)

class PointsOutput(Output):
    def __init__(self,y_exp, system=None, constant_values = None):
        system = system or pynamics.get_system()
        y_exp = [item for item2 in y_exp for item in [item2.dot(system.newtonian.x),item2.dot(system.newtonian.y)]]
        Output.__init__(self,y_exp, system, constant_values)

    def calc(self,x):
        Output.calc(self,x)
        self.y.resize(self.y.shape[0],int(self.y.shape[1]/2),2)
        return self.y
    
    def make_gif(self,stepsize = 1):
        import os
        import idealab_tools.makemovie
        import matplotlib.pyplot as plt
        y = self.y
        
        folder = 'render'
        idealab_tools.makemovie.clear_folder(folder)
        idealab_tools.makemovie.prep_folder(folder)
        f = plt.figure()
        ax = f.add_subplot(1,1,1)
        ax.axis('equal')
        ax.set_xlim((y[:,:,0].min(),y[:,:,0].max()))
        ax.set_ylim((y[:,:,1].min(),y[:,:,1].max()))
        
        for ii,item in enumerate(y[::stepsize]):
            [item.remove() for item in ax.lines]
            ax.plot(item[:,0],item[:,1],'ro-')
            plt.savefig(os.path.join(folder,'{0:04d}.png'.format(ii)))
        
        idealab_tools.makemovie.make_gif()
        idealab_tools.makemovie.clear_folder(folder)

    def render_movie(self,stepsize = 1):
        import os
        import idealab_tools.makemovie
        import matplotlib.pyplot as plt
        y = self.y
        
        folder = 'render'
        idealab_tools.makemovie.clear_folder(folder)
        idealab_tools.makemovie.prep_folder(folder)
        f = plt.figure()
        ax = f.add_subplot(1,1,1)
        ax.axis('equal')
        ax.set_xlim((y[:,:,0].min(),y[:,:,0].max()))
        ax.set_ylim((y[:,:,1].min(),y[:,:,1].max()))
        
        for ii,item in enumerate(y[::stepsize]):
            [item.remove() for item in ax.lines]
            ax.plot(item[:,0],item[:,1],'ro-')
            plt.savefig(os.path.join(folder,'img_{0:04d}.png'.format(ii)))
        
        idealab_tools.makemovie.render()
        idealab_tools.makemovie.clear_folder(folder)    

    def animate(self,fps = 30,stepsize=1, movie_name = None):
        import numpy as np
        import matplotlib.pyplot as plt
        
        from matplotlib import animation, rc

        y = self.y

        f = plt.figure()
        ax = f.add_subplot(1,1,1,aspect = 'equal',autoscale_on=False)
#        ax.axis('equal')
        limits   = [y[:,:,0].min(),y[:,:,0].max(),y[:,:,1].min(),y[:,:,1].max()]
        ax.axis(limits)

#        y = self.y[::stepsize]
        
        line, = ax.plot([], [], lw=2)
        
        def init():
            line.set_data([], [])
            return (line,)
        
        def run(item):
            line.set_data(*(item.T))
#            ax.axis('equal')
#            ax.axis(limits)
            return (line,)

        self.anim = animation.FuncAnimation(f, run, init_func=init,frames=y[::stepsize], interval=1/fps*1000, blit=True,repeat = True,repeat_delay=3000)        
        if movie_name is not None:
            self.anim.save(movie_name, fps=fps,writer='ffmpeg')