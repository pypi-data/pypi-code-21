#!/usr/bin/env python
"""Dimg is the Display IMaGe package
wrapping some most-used parts of the matplolib library
and pyfits library, and making graphics more interactive.

Author: Don Gavel
"""
import os
import time

try:
    machine = os.environ['HOSTNAME']
except:
    machine = 'not a unix host (probably a mac)'

if (machine != 'rtc.ucolick.org'):
    import matplotlib
    # if (matplotlib.get_backend() != 'TkAgg'):
    #     matplotlib.use('TkAgg',warn = False)
    from mpl_toolkits.mplot3d import Axes3D
    from matplotlib import cm
    from matplotlib.ticker import LinearLocator, FormatStrFormatter
    import matplotlib.pyplot as plt
    plt.ion()

import numpy as np
import readfits as fits
import matplotlib.animation as animation

def surface(z,**kwargs):
    dimg(z,surface=True,**kwargs)
    
def contour(z,**kwargs):
    if 'image' not in kwargs.keys():
        kwargs['image'] = False
    dimg(z,contour=True,**kwargs)
    
def tv(z,grid=True,cmap='bone',origin='lower',dx=1):
    """New simplified version of dimg
    Displays only 2-D images
    X and Y coordinates start at 0,0 lower-left of 0,0 pixel and end at n,n upper right of n-1,n-1 pixel
    Display origin is always lower left
    Always shows a color bar
    
    keyword args:
     cmap: color map
     origin: 'lower' puts 0,0 at the lower left corner
             'center' puts 0,0 at the lower left of pixel n/2 (pixels are numbered 0 to n-1)
     dx: increment of one pixel
    """
    assert type(z) == np.ndarray
    assert len(z.shape) == 2

    n,m = z.shape
    extent = np.array([0,n,0,n])
    if (origin == 'center'):
        extent = extent - n/2
    extent *= dx

    def format_coord(xx, yy):
        col = int(xx+0.5)
        row = int(yy+0.5)
        l,r,b,t = extent
        row = int(((yy-b)/(t-b))*m)
        col = int(((xx-l)/(r-l))*n)
        if col>=0 and col<n and row>=0 and row<m:
            return '%1.2f,%1.2f[%1.0f,%1.0f] %1.2f' % (xx,yy, row,col, z[row,col])
        else:
            return 'x=%1.4f, y=%1.4f' % (xx, yy)
    
    plt.ion()
    plt.figure()
    ax = plt.subplot(111)
    im = ax.imshow(z,interpolation='nearest',origin='lower',extent=extent, cmap=cmap)
    ax.format_coord = format_coord
    plt.colorbar(im)
    if (grid):
        plt.grid('on')
    return im
    
def dimg(z,fig=None,sub=None,title=None,ap=None,extent=None,stride=None,image=True,contour=False,levels=None,surface=False,cmap='bone',origin='upper',colorbar=False,geometry=None):
    """Displays an array graphically.
    
    Usage: ret = dimg(theArray,[options])
    options:
        fig (None) - the existing figure window to draw in
        sub (None) - the subplot region to draw in, if any
        image - create a grey-scale image of the 2d data (default)
        contour - draw contour lines. can be combined with image
        surface - create a 3d surface rendering
        cmap ('bone') can be 'hot'
    returns:
        image object, contour object, (image,contour), or surface object
        depending on the option choices
    """
    if surface:
        image = False
        contour = False
    
    if contour:
        origin = 'lower'
    
    if (type(z) == list):
        movie(z,ap=ap)
        return
    
    if (machine == 'rtc.ucolick.org'):
        print '<dimg> not available on ',machine
        print '<dimg> use dimg.movie([arg]) instead to force display using ds9'
        return
    
    assert isinstance(z,np.ndarray),'<dimg> ERROR argument must be a 2d array'
    
    if (len(z.shape) == 3):
        movie(z,ap=ap)
        return
    
    if (ap != None):
        z = z*ap
    
    plt.ion()
    
    try:
        thefig = plt.figure(fig)
    except:
        if (type(fig) == type('string')):
            if (title is None):
                title = fig
            fig = None
    
        thefig = plt.figure(fig)

    if (fig is not None) and (sub is None):
        plt.clf()
    
    if (sub is not None):
        ax = plt.subplot(sub)
    else:
        ax = plt.subplot(111)

    if (title is not None):
        plt.title(str(title))    
    
    def format_coord(xx, yy):
        col = int(xx+0.5)
        row = int(yy+0.5)
        if extent is not None:
            l,r,b,t = extent
            row = int(((yy-b)/(t-b))*numrows)
            col = int(((xx-l)/(r-l))*numcols)
            if (origin != 'lower'):
                row = numrows-row-1
        if col>=0 and col<numcols and row>=0 and row<numrows:
            #return 'x%1.2fy%1.2f[r%1.0fc%1.0f]v%1.2f'%(xx,yy, row,col, z[row,col])
            return 'x%1.2f y%1.2f [r%1.0fc%1.0f] z%1.2f'%(xx,yy, row,col, z[row,col])
        else:
            return 'x=%1.4f, y=%1.4f'%(xx, yy)

    numrows, numcols = z.shape
    if extent is None:
        x = range(numcols)
        y = range(numrows)
    else:
        x = np.linspace(extent[0],extent[1],numcols)
        y = np.linspace(extent[2],extent[3],numrows)
    
    im = None
    if image:
        im = ax.imshow(z,extent=extent,cmap=cmap,interpolation='nearest',origin=origin)
        ax.format_coord = format_coord
        if (colorbar):
            plt.colorbar(im)
        ret = im
    if contour:
        if levels is None:
            if image:
                cs = plt.contour(z,extent=extent,colors='lightgreen')
            else:
                cs = plt.contour(z,extent=extent,colors='black')
        else:
            if image:
                colors = None
            else:
                colors = 'black'
                ax.format_coord = format_coord
            cs = plt.contour(z,extent=extent,levels=levels,colors=colors)
            plt.clabel(cs)
        plt.clabel(cs)
        if image:
            ret = (im,cs)
        else:
            ret = cs
    if surface:
        # set the stride to keep from plotting too many points, unless the stride is overridden
        surface_maxpts = 20
        if stride is None:
            n,m = z.shape
            stride = np.array([n,m])/surface_maxpts
            stride = np.clip(stride,1,np.inf).astype(int)
        ax = plt.gca(projection='3d')
        x2,y2 = np.meshgrid(x,y)
        z2 = z.copy()
        if (isinstance(z,np.ma.core.MaskedArray)):
            x2 = np.ma.array(x2,mask=z.mask).compressed()
            y2 = np.ma.array(y2,mask=z.mask).compressed()
            z2 = z2.compressed()
            surf = ax.plot_trisurf(x2,y2,z2,cmap=cmap)
        else:
            surf = ax.plot_surface(x2,y2, z2, rstride = stride[0], cstride = stride[1], cmap=cmap)
        ret = surf

    if geometry is not None:
        pass
        #mgr = plt.get_current_fig_manager()
        #mgr.window.geometry(geometry)
    
    def _onclick(event):
        #print 'figure = '+thefig.__repr__()
        #print 'button=%d, x=%d, y=%d, xdata=%f, ydata=%f'%(
        #    event.button, event.x, event.y, event.xdata, event.ydata)
        #print 'xlimits: '+str(plt.xlim())+'  ylimits: '+str(plt.ylim())
        if (not image):
            return
        toolstate = thefig.canvas.manager.toolbar._active
        if (toolstate is None and event.button == 3):
            z_range = np.array([z.min(),z.max()])
            x_range = plt.xlim()
            y_range = plt.ylim()
            brightness = (event.ydata - y_range[0])/(y_range[1]-y_range[0])
            contrast = (event.xdata - x_range[0])/(x_range[1]-x_range[0])
            dz = z_range[1]-z_range[0]
            mid = (z_range[0]+z_range[1])/2.
            z1 = z_range[1] - ((brightness - 0.5)/0.5)*dz
            dz = dz*contrast*4
            z0 = z1 - dz
            #print 'brightness = '+str(100*brightness)+' %'
            #print 'contrast = '+str(100*contrast)+' %'
            ax = plt.subplot(111)
            ax.imshow(z,vmin=z0,vmax=z1,extent=extent,cmap=cmap,interpolation='nearest',origin=origin)

    cid = thefig.canvas.mpl_connect('button_press_event', _onclick)
    return ret

show = dimg

def ds9(arr2d,ap=None):
    """
    Displays a 2-d array using ds9
    """
    movie([arr2d],ap)

    
def movie(arr3d,ap=None):
    """
    Displays a 3-d data cube using ds9
    The array can be a 3-dimensional array or a list of 2-d arrays
    ap is an optional aperture window outside of which values are not displayed
    """
    if (type(arr3d) == list):
        movie(np.array(arr3d),ap=ap)
        return
    if (type(arr3d) != np.ndarray):
        print '<movie> ERROR argument must be an array'
        return
    if (len(arr3d.shape) != 3):
        print '<movie> ERROR array argument must have 3 dimensions'
        return
    if (ap != None):
        for i in range(arr3d.shape[0]):
            arr3d[i,:,:] *= ap
    os.system("rm -f temp_ds9_array.fits")
    fits.writefits(arr3d,'temp_ds9_array.fits')
    os.system("ds9 temp_ds9_array.fits &")

def play(arr3d,dt_ms=50,ap=None,cmap='bone',label = 'time',times=None,tunits='',**kwargs):
    """play(arr3d,ap=None,rate=1000,loop=False)
    Displays a 3-d data cube using matplotlib
    The array can be a 3-dimensional numpy array or a list of 2-d numpy arrays
    ap is an optional aperture window outside of which values are not displayed
    """
    #global k,frames,ani,pause, step
    
    arr3d = np.array(arr3d)
    if ap is not None:
        arr3d = arr3d*ap
    
    vmin = arr3d.min()
    vmax = arr3d.max()
    
    shape = arr3d.shape
    if (len(shape) == 3):
        nt,nr,nc = shape
        frames = arr3d
    if (len(shape) == 4): # this is a block display
        na,nt,nr,nc = shape
        frames = arr3d.transpose([1,2,0,3]).reshape((nt,nr,na*nc))
    if (len(shape) == 5):
        na,nb,nt,nr,nc = shape
        frames = arr3d.transpose([2,0,3,1,4]).reshape((nt,na*nr,nb*nc))

    numrows, numcols = frames[0].shape
    
    fig = plt.figure()
    ax = fig.gca()

    im = plt.imshow(frames[0],vmin=vmin,vmax=vmax,cmap=cmap,interpolation='nearest',animated=True,**kwargs)
    n = len(frames)
    if times is None:
        times = np.arange(float(n))
    tstr = '{:8.4f}'.format(float(times[0]))
    plt.title(label+' '+tstr+' '+tunits)
    
    k = 0
    z = frames[0]
    n = len(frames)
    step = +1
    
    def updatefig(*args):
        #global k
        #print '<updatefig> ---------------'
        #print args
        c = args[1]
        fig = c.figure
        plt.figure(fig.number)
        #print c
        #print '---------------------------'

        z = c.frames[c.k]
        im.set_array(z)
        tstr = '{:8.4f}'.format(float(times[c.k]))
        plt.title(label+' '+tstr+' '+tunits)
        if not c.pause:
            if c.report_time:
                if (c.k == 0):
                    c.t0 = time.time()
                if (c.k+c.step) >= n:
                    t1 = time.time()
                    print 'display rate:',float(n)/(t1-c.t0),'Hz'
                    c.report_time = False
            c.k = (c.k+c.step) % n
        return im,
    
    def onClick(event):
        #global pause
        c = event.canvas
        c.pause ^= True
    
    def onKey(event):
        #global pause, step
        #print event.key
        c = event.canvas
        if event.key == 'escape':
            c.frames = 0
            plt.close()
        if event.key == 'right':
            c.pause = False
            c.step = +1
            updatefig(0,c)
            c.pause = True
        if event.key == 'left':
            c.pause = False
            c.step = -1
            updatefig(0,c)
            c.pause = True
            c.step = +1
        if event.key == ' ':
            c.pause ^= True        
    
    pause = False
    fig.canvas.mpl_connect('button_press_event',onClick)
    fig.canvas.mpl_connect('key_press_event',onKey)
    fig.canvas.k = k
    fig.canvas.frames = frames
    fig.canvas.pause = pause
    fig.canvas.step = step
    fig.canvas.report_time = True
    fig.canvas.t0 = 0.
    ani = animation.FuncAnimation(fig,updatefig,fargs = [fig.canvas],interval=33,blit=False)
    fig.canvas.ani = ani
    plt.show()
    print 'instructions:'
    print '  space or left mouse click: pause'
    print '  right arrow: advance one frame forward'
    print '  left arrow: go back one frame'
    print '  escape: exit'

def play_test():
    global frames
    frames = np.random.normal(size=(100,100,100))
    play(frames)

def clearwins():
    """Close all the dimg display windows
    """
    plt.close('all')

def example(surface=False):
    """Run a simple example with generated dummy data
    """
    global x,y,z,extent
    
    npts = 100
    stride = [1,1]
    if surface:
        stride = np.fix(np.array([1,1])*(npts/20.)).astype('int')
    x = np.linspace(-2*np.pi,2*np.pi,npts)
    x,y = np.meshgrid(x,x)
    z = x**2*y**3
    extent = np.array([-1,1,-1,1])*2*np.pi
    dimg(z,origin='lower',extent=extent,surface=surface,stride=stride,colorbar=True)

def test():
    """Regression-test the dimg package
    """
    f = '(x^2)*(y^2)'
    example(); plt.title('image '+f)
    example(surface=True); plt.title('surface '+f)
    levels = np.logspace(0,5,num=6)
    levels = np.hstack([-levels[::-1],0,levels])
    img,cs = dimg(z,contour=True,origin='lower',extent=extent,levels=levels); plt.title('image & contour '+f)
    cs = dimg(z,image=False,contour=True,extent=extent,levels=levels); plt.title('contour '+f)
    plt.grid('on')
    
__version__ = "1.2 Aug 8, 2015"

if __name__ == '__main__':
    test()
    plt.show(block=False)
    u = raw_input('hit return to exit')
    print 'done'
