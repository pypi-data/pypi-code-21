# Define classes

# Imports
import numpy as np
import matplotlib.pyplot as plt
import scipy.interpolate as spintp
from scipy.optimize import curve_fit
import os
import os.path
import urllib.request
import numba
import pickle
import scipy.misc
import scipy.optimize
from scipy.interpolate import interp1d
import time

from mpl_toolkits.axes_grid1 import make_axes_locatable


# Importing from zsharp is its main else using .
if __name__ == '__main__':
    import os.path
    import sys

    path2therpy = os.path.join(os.path.expanduser('~'), 'Documents', 'My Programs', 'Python Library')
    sys.path.append(path2therpy)
    from zsharp import smooth
    from zsharp import calculus
    from zsharp import imageio
    from zsharp import imagedata
    from zsharp import constants
    from zsharp import functions
    from zsharp import roots1
    from zsharp import atomnumber
    from zsharp import numerical
else:
    from . import smooth
    from . import calculus
    from . import imageio
    from . import imagedata
    from . import constants
    from . import functions
    from . import roots1
    from . import thermodynamics
    from . import numerical
    from . import Virial
    from . import atomnumber


# import smooth
# import calculus


###################################################################################
############################ interp_od ############################################
# Load pre-compiled data
p_ = roots1.getpath('Projects','Data','LookupTable','Lookup_Table_Fast_PreCompData_V2.p')
if not os.path.isfile(p_):
    print("Downloading Database -- Might take some time!")
    url = "https://www.dropbox.com/s/4hklnvawtshjay9/Lookup_Table_Fast_PreCompData_V2.p?dl=1"
    u = urllib.request.urlopen(url)
    data = u.read()
    u.close()
    # Create folder
    os.makedirs(os.path.split(p_)[0], exist_ok=True)
    with open(p_, "wb") as f :
        f.write(data)
precompiled_data_Lookup_Table = pickle.load( open( p_, "rb" ) )

# Jitted interpolation
@numba.jit(nopython=True)
def interp_od_special_jit(IivIn, IfvIn, sim_data):
    # Unload sim_data
    u_si, sf_2d, ocd_2d = sim_data[0], sim_data[1], sim_data[2]
    rows, cols = sf_2d.shape[0], sf_2d.shape[1]
    # Copy inputs and flatten the arrays
    Iiv = IivIn.copy().flatten()  # Flatten so that we can do 1d loop
    Ifv = IfvIn.copy().flatten()  # We will unflatten the arrays when returning
    # Fix low and high OD regions
    bad_low = (Iiv < Ifv)  # For low od (BG), flip Ii and If and make od -> -od
    Iiv[bad_low], Ifv[bad_low] = Ifv[bad_low].copy(), Iiv[bad_low].copy()
    bad_high = (Ifv < 0)   # For high od where If < 0, make If -> -If
    Ifv = np.abs(Ifv)
    # Prepare
    i0v = np.searchsorted(u_si, Iiv)   # Find the indice for closest si
    Pfv = np.zeros_like(Iiv) * np.nan  # Prepare output array, default it with nan
    # Interpolate OD's
    for i in range(Iiv.size):
        Ii, If, i0 = Iiv[i], Ifv[i], i0v[i]
        # Search 4 closest points
        if i0 >= rows or i0 == 0: continue  # If Ii is outside simulation, result is nan
        i1 = np.searchsorted(sf_2d[i0-1,:], If)
        if i1 >= cols: Pfv[i] = 0; continue # If If > max(sf), result is zero atoms
        elif i1 == 0: continue
        i2 = np.searchsorted(sf_2d[i0,:], If)
        if i2 >= cols: Pfv[i] = 0; continue # If If > max(sf), result is zero atoms
        elif i2 == 0: continue
        i0m1 = i0-1
        x1 = u_si[i0m1]
        x2 = u_si[i0]
        dx = x2 - x1
        dx2 = dx**2
        Ary = sf_2d[i0m1, i1-1]
        Bry = sf_2d[i0, i2-1]
        Cry = sf_2d[i0m1, i1]
        Dry = sf_2d[i0, i2]
        Af = ocd_2d[i0m1, i1-1]
        Bf = ocd_2d[i0, i2-1]
        Cf = ocd_2d[i0m1, i1]
        Df = ocd_2d[i0, i2]
        # Interpolate with 4 nearest points
        s = (Ii - x1) / (dx)
        Erx = x1 + (dx) * s
        Ery = Ary + (Bry - Ary) * s
        Frx = x1 + (dx) * s
        Fry = Cry + (Dry - Cry) * s
        Ef = Af + (Bf - Af)  * (((Erx - x1)**2 + (Ery - Ary)**2) / ((dx2 + (Bry - Ary)**2)))**0.5
        Ff = Cf + (Df - Cf)  * (((Frx - x1)**2 + (Fry - Cry)**2) / ((dx2 + (Dry - Cry)**2)))**0.5
        Pfv[i] = Ef + (Ff - Ef) * (((Ii - Erx)**2 + (If - Ery)**2) / (((Frx - Erx)**2 + (Fry - Ery)**2)) )**0.5
    # Make the bad_low od -> -od
    Pfv[bad_low] *= -1
    # Reshape and return
    return Pfv.reshape(*IivIn.shape)

# Wrapper around jitted function to handle passing in pre-compiled data
def interp_od(Ii, If, img_time):
    return interp_od_special_jit(Ii, If, precompiled_data_Lookup_Table[img_time-1])


####################################################################################
########################### Image ##################################################
# Complete Image Class 

Default_Image_Set = dict(name='Not Provided', path='Not Provided',
                        center_x=1, center_y=1, width=1000000, height=1000000,
                        subsample=1, rotate=0, rotate_method='bilinear',
                        prep_order=['rotate','crop','subsample'],
                        fudge=1, bg_width=0, bg_order=1, bad_light=0, 
                        Isat=1, time=1, pixel=1e-6, detuning=0,
                        od_method='log', sigmaf=1, memory_saver=False,
                        lookup_table_version='v1')

Level_Selector_Image = [['name','path','center_x','center_y','center',
                         'width','height','cropset','cropi','subsample',
                         'rotate','rotate_method','prep_order'],
                        ['bg_width','bg_order'],
                        ['bad_light','Isat','time','od_method']]

'''
Speed: total of 350 ms per image
- 200 ms to load image into memory
- 100 ms to crop and subsample image
- 600 ms if rotating an image
- 5 ms to find border gradient
- 20 ms to computer OD using LookupTable (depends on crop size)
'''
cst_LiD2 = constants.cst(atom='LiD2')
cst_Image_Class = constants.cst()

class Image:
    '''Get image name and path, start self.var'''
    def __init__(self, name=None, path=None, od=None, **kwargs):
        # local storage 
        self.var = {**Default_Image_Set, **kwargs}
        self.var['Level_Selector'] = list(Level_Selector_Image)
        self.var['recalc'] = [True]*len(self.var['Level_Selector'])
        
        # Use path if provided, else use name and find path
        if (type(path) is str) and os.path.exists(path): 
            self.var['path'], self.var['name'] = path, os.path.splitext(os.path.split(path)[1])[0] 
        elif type(name) is str: self.var['name'], self.var['path'] = name, imageio.imagename2imagepath(name)
        elif od is not None:
            self.var['od'] = od
            self.var['Level_Selector'][0] = [] # Disable Level, 0 computations
            self.var['Level_Selector'][1] = [] # Disable Level, 1 computations
            self.var['Level_Selector'][2] = [] # Disable Level, 2 computations
            self.var['recalc'] = [False]*len(self.var['Level_Selector'])
        else: raise ValueError('Please provide at least name, path, or od to the Image constructor.')
    
##### Properties -- Atomic Density and Numbers [in progress] 
    @property
    def od(self,):
        if ('od' not in self.var.keys()) or self.recalc[2]:
            self.optical_density()
        return self.var['od'] * self.fudge
    
    @property
    def n_2d(self,): return self.od / self.sigma
    
    @property
    def app(self,): return self.od / self.sigma * self.pixel_binned**2
    
    @property
    def od_raw(self,): return - np.log(self.If_raw / self.Ii_raw)
    
    @property
    def total_atoms(self,): return np.nansum(self.app)
#####
    
##### Properties -- Imaging Intensity [in progress] 
    @property
    def rawdata(self,): return imageio.imagepath2imagedataraw(self.path)
    
    @property
    def alldata(self,):
        if 'alldata' in self.var.keys(): return self.var.get('alldata')
        alldata = imageio.imagedataraw2imagedataall(self.rawdata)
        if self.memory_saver is False: self.var['alldata'] = alldata
        return alldata
    
    @property
    def Ii_raw(self,):
        if ('Ii_raw' not in self.var.keys()) or self.recalc[0]:
            self.prep_image()
        return self.var['Ii_raw']
    
    @property
    def If_raw(self,):
        if ('If_raw' not in self.var.keys()) or self.recalc[0]: 
            self.prep_image()
        return self.var['If_raw']
    
    @property
    def alpha_Ii(self,):
        if ('alpha_Ii' not in self.var.keys()) or self.recalc[1]:
            self.border_gradient()
        return self.var['alpha_Ii']
    
    @property
    def Ii(self,): return (self.Ii_raw * self.alpha_Ii) * (1-self.bad_light) 
    
    @property
    def If(self,): return self.If_raw - (self.Ii_raw * self.alpha_Ii * self.bad_light)
    
    @property
    def si(self,): return self.Ii / self.Nsat
    
    @property
    def sf(self,): return self.If / self.Nsat
    
    @property
    def Ii_avg(self,): return np.nanmean(self.Ii) / self.subsample**2
    
    @property
    def Ii_avg_binned(self,): return np.nanmean(self.Ii)
    
    @property
    def si_avg(self,): return np.nanmean(self.si)
    
#####

##### Properties -- Settings [completed] 
    @property
    def name(self,): return self.var.get('name')
    
    @property
    def path(self,): return self.var.get('path')
    
    @property
    def center_x(self,): return self.var.get('center_x')
    
    @property
    def center_y(self,): return self.var.get('center_y')
    
    @property
    def center(self,): return self.var.get('center', (self.center_x, self.center_y))
    
    @property
    def width(self,): return self.var.get('width')
    
    @property
    def height(self,): return self.var.get('height')
    
    @property
    def cropset(self,): return self.var.get('cropset', dict(center=self.center, width=self.width, height=self.height))
    
    @property
    def cropi(self,): 
        if ('cropi' not in self.var.keys()) or self.recalc[0]: 
            self.prep_image()
        return self.var['cropi']
    
    @property
    def subsample(self,): return self.var.get('subsample')
    
    @property
    def rotate(self,): return self.var.get('rotate')
    
    @property
    def rotate_method(self,): return self.var.get('rotate_method')
    
    @property
    def prep_order(self,): return self.var.get('prep_order')
    
    @property
    def fudge(self,): return self.var.get('fudge')
    
    @property
    def bg_width(self,): return self.var.get('bg_width')
    
    @property
    def bg_order(self,): return self.var.get('bg_order')
    
    @property
    def bad_light(self,): return self.var.get('bad_light')
    
    @property
    def Isat(self,): return self.var.get('Isat')
    
    @property
    def Nsat(self,): return self.Isat * self.time * self.subsample**2
    
    @property
    def time(self,): return self.var.get('time')
    
    @property
    def pixel(self,): return self.var.get('pixel')
    
    @property
    def pixel_binned(self,): return self.pixel * self.subsample
    
    @property
    def detuning(self,): return self.var.get('detuning')
    
    @property
    def od_method(self,): return self.var.get('od_method')
    
    @property
    def sigmaf(self,): return self.var.get('sigmaf')
    
    @property
    def sigma(self,): return self.var.get('sigma', cst_Image_Class.sigma0 * self.sigmaf)
    
    @property
    def memory_saver(self,): return self.var.get('memory_saver')
    
    @property
    def lookup_table_version(self,): return self.var.get('lookup_table_version')
#####    
    
##### Procedures 
    '''Recalc Manager'''
    @property
    def recalc(self,): return self.var.get('recalc')

    '''Main Setter Function'''
    def set(self, **kwargs):
        if kwargs.get('refresh',False):
            self.var['recalc'] = [True] * len(self.recalc)
            return None
        keys = kwargs.keys()
        # recalc[0] is True if any of the keys in level 0 is provided and is different from current value
        recalc = [any([(j in keys) and (kwargs[j] != self.var.get(j,None)) for j in i]) for i in self.var['Level_Selector']]
        # Update self.var
        self.var = {**self.var, **kwargs}
        # If recalc[2] is True, then all that follows must also be true
        for i in range(len(recalc)): 
            if recalc[i]: 
                recalc[i+1:] = [True]*len(recalc[i+1:])
                break
        # self.recalc[0] is True if recalc[0] or self.recalc[0] was already True 
        self.var['recalc'] = [recalc[i] or self.recalc[i] for i in range(len(recalc))]
    
    '''Load Image into Memory == Crop, Subsample, Rotate ==> Store cropi, Ii_raw, If_raw'''
    def prep_image(self,):
        [If, Ii] = self.alldata
        # for task in self.prep_order:
        #     if task == 'crop':
        #         cropi = imagedata.get_cropi(Ii, **self.cropset)  # Need to improve speed here, takes 50 ms, (99% of time spent at [XX, YY] = np.meshgrid(x, y))
        #         Ii = Ii[cropi]
        #         If = If[cropi]
        #     elif (task == 'rotate') and (self.rotate != 0):
        #         # Ii = scipy.misc.imrotate(Ii, angle=self.rotate, interp=self.rotate_method) # Takes 250 ms
        #         # If = scipy.misc.imrotate(If, angle=self.rotate, interp=self.rotate_method) # takes 250 ms
        #
        #
        #         Ii = scipy.ndimage.interpolation.rotate(Ii, angle=4)
        #         center = [round(Ii.shape[1] / 2), round(Ii.shape[0] / 2)]
        #         mask = get_cropi(Ii, center=center, width=self.width*0.8, height=self.height*0.8)
        #         Ii=Ii[mask]
        #
        #         If = scipy.ndimage.interpolation.rotate(If, angle=4)
        #         center = [round(If.shape[1] / 2), round(If.shape[0] / 2)]
        #         mask = get_cropi(If, center=center, width=self.width * 0.8, height=self.height * 0.8)
        #         If = If[mask]
        #
        #     elif (task == 'subsample') and (self.subsample != 1):
        #         Ii = smooth.subsample2D(Ii, bins=[self.subsample, self.subsample]) # 1 ms
        #         If = smooth.subsample2D(If, bins=[self.subsample, self.subsample]) # 1 ms


        if ('rotate' in self.prep_order) and (self.rotate != 0):
            Ii = scipy.ndimage.interpolation.rotate(Ii, angle=self.rotate,order=1)  #roatation takes ~2s
            If = scipy.ndimage.interpolation.rotate(If, angle=self.rotate,order=1)
            end = time.time()
        if 'crop' in self.prep_order:
            cropi = imagedata.get_cropi(Ii, **self.cropset)  # Need to improve speed here, takes 50 ms, (99% of time spent at [XX, YY] = np.meshgrid(x, y))
            Ii = Ii[cropi]
            If = If[cropi]
            self.var['cropi'] = cropi
        if ('subsample' in self.prep_order) and (self.subsample != 1):
            Ii = smooth.subsample2D(Ii, bins=[self.subsample, self.subsample]) # 1 ms
            If = smooth.subsample2D(If, bins=[self.subsample, self.subsample]) # 1 ms
        self.var['If_raw'], self.var['Ii_raw'] = If, Ii
        self.var['recalc'][0] = False



    
    '''Find alpha for background subtraction'''
    def border_gradient(self,):
        # If width is set to 0
        if self.bg_width == 0:
            self.var['alpha_Ii'] = np.ones_like(self.Ii_raw)
            self.var['recalc'][1] = False
            return None
    
        # Get slicer for the border
        data = self.If_raw / self.Ii_raw
        mask = np.ones_like(data)
        w = self.bg_width
        s = data.shape
        mask[w:s[0]-w, w:s[1]-w] = 0
        using = np.logical_and((mask==1) , (np.isfinite(data)) )
        
        # Get Data for fitting
        xx, yy = np.meshgrid(np.arange(s[1]), np.arange(s[0]))
        xx_f, yy_f, zz_f = (xx[using], yy[using], data[using])
        def poly_2d(xy, b, m1=0, m2=0):
            return b + m1*xy[0] + m2*xy[1]
        
        # Fit
        guess = [1e-1]
        if self.bg_order == 1: guess = [1e-1, 1e-5, 1e-5]
        fitres, fiterr = scipy.optimize.curve_fit(poly_2d, (xx_f, yy_f), zz_f, p0=guess)
        self.var['alpha_Ii'] = poly_2d((xx, yy), *fitres)
        self.var['recalc'][1] = False
        
        # Warning for correction larger than 10%
        if abs(np.mean(self.var['alpha_Ii'])-1) >= 0.1:
            print('WARNING! Background correction is larger than 10%. Imagename {}'.format(self.name))
        
    '''Compute Optical Density'''
    def optical_density(self,):
        method = self.od_method
        if method in ['table','dBL']: self.var['od'] = (interp_od(self.si, self.sf, self.time))
        elif method in ['sBL']: self.var['od'] =(- np.log(self.sf / self.si) + self.si - self.sf)
        else: self.var['od'] =(- np.log(self.sf / self.si))
        self.var['recalc'][2] = False
#####

##### Plots 
    def imshow(self, ax=None):
        if ax is None: _, ax = plt.subplots(figsize=(4,4))
        
        divider = make_axes_locatable(ax)
        ax_cb = divider.new_horizontal(size="8%", pad=0.05)
        fig1 = ax.get_figure()
        fig1.add_axes(ax_cb)
        im = ax.imshow(self.app, origin='lower')
        plt.colorbar(im, cax=ax_cb)
        ax.set_axis_off()
        ax.set(title='Atoms/Pixel')
        
    
    def plot_crop(self, ax=None):
        alldata = self.alldata
        w = self.bg_width
        s = self.Ii_raw.shape
        cropi = self.cropi
        
        # Prepare Box
        x = [cropi[1].start,cropi[1].start,cropi[1].stop,cropi[1].stop,cropi[1].start]
        y = [cropi[0].start,cropi[0].stop,cropi[0].stop,cropi[0].start,cropi[0].start]
        x.extend([x[2],x[3],x[1]])
        y.extend([y[2],y[3],y[1]])
        
        try: ax[1]
        except: ax = plt.subplots(figsize=(10,4), ncols=2)[1]
        
        # Plots
        divider = make_axes_locatable(ax[0])
        ax_cb = divider.new_horizontal(size="8%", pad=0.05)
        fig1 = ax[0].get_figure()
        fig1.add_axes(ax_cb)
        im = ax[0].imshow(np.log(alldata[1] / alldata[0]), clim = [self.od_raw.min(), self.od_raw.max()], origin='lower')
        plt.colorbar(im, cax=ax_cb)
        ax[0].plot(x, y, 'w-', alpha=0.5)
        ax[0].set(title='Bare Image')
        
        divider = make_axes_locatable(ax[1])
        ax_cb = divider.new_horizontal(size="8%", pad=0.05)
        fig1 = ax[1].get_figure()
        fig1.add_axes(ax_cb)
        im = ax[1].imshow(self.od_raw, origin='lower')
        plt.colorbar(im, cax=ax_cb)
        ax[1].set(title='Cropped, Rotated, Subsampled')
        ax[1].plot([w, w, s[1] - w, s[1] - w, w], [w, s[0] - w, s[0] - w, w, w], 'w-')
        ax[1].set(xlim=[0,s[1]], ylim=[0,s[0]])
        fig1.tight_layout()
        
    def plot_border_gradient(self,):
        data = self.If_raw / self.Ii_raw
        s = data.shape
        w = self.bg_width
        alpha_Ii = self.alpha_Ii
        
        fig, ax = plt.subplots(figsize=(8, 5), nrows=2, ncols=3)
        ax[0,0].imshow(self.od_raw, aspect='auto', origin='lower')
        ax[0,0].plot([w, w, s[1] - w, s[1] - w, w], [w, s[0] - w, s[0] - w, w, w], 'w-')
        ax[0,0].set_axis_off()
        ax[0,0].set(title='BG Width Boundary')
        if w != 0:
            ax[0,2].plot(np.nanmean(alpha_Ii[0:w, :], axis=0),'k-')
            ax[0,2].plot(np.nanmean(data[0:w,:], axis=0), '.', markersize=2)
            ax[0,2].set(title='top')
            ax[1,0].plot(np.nanmean(alpha_Ii[:, 0:w], axis=1),'k-')
            ax[1,0].plot(np.nanmean(data[:,0:w], axis=1), '.', markersize=2)
            ax[1,0].set(title='left')
            ax[1,1].plot(np.nanmean(alpha_Ii[:, -w:], axis=1),'k-')
            ax[1,1].plot(np.nanmean(data[:,-w:], axis=1), '.', markersize=2)
            ax[1,1].set(title='right')
            ax[1,2].plot(np.nanmean(alpha_Ii[-w:, :], axis=0),'k-')
            ax[1,2].plot(np.nanmean(data[-w:,:], axis=0), '.', markersize=2)
            ax[1,2].set(title='bottom')
        
        divider = make_axes_locatable(ax[0,1])
        ax_cb = divider.new_horizontal(size="8%", pad=0.05)
        fig.add_axes(ax_cb)
        im = ax[0,1].imshow((self.alpha_Ii - 1)*100, aspect='auto', origin='lower')
        plt.colorbar(im, cax=ax_cb)
        ax[0,1].set_axis_off()
        ax[0,1].set(title='(alpha_Ii - 1) * 100')
        
        fig.tight_layout()
#####


Default_ODT_settings = dict(trap_f_z=23.4, trap_f_r=150,r_TF_fitrange=0.5,Boltzmann_limit=5000)
cst_ODT_Class = constants.cst()
class ODT_Image(Image):
    def __init__(self, name=None, path=None, od=None, **kwargs):
        # Initialize the complete Image Object
        super(ODT_Image, self).__init__(name=name, path=path, od=od, **kwargs)

        # Addons
        self.var = {**self.var, **Default_ODT_settings, **kwargs}

    # New Properties
    @property
    def trap_f_z(self): return self.var.get('trap_f_z')

    @property
    def trap_f_r(self): return self.var.get('trap_f_r')

    @property
    def r_TF_fitrange(self): return self.var.get('r_TF_fitrange')

    @property
    def Boltzmann_limit(self): return self.var.get('Boltzmann_limit')

    @property
    def z_index(self): return np.array(range(0,self.app.shape[0]))

    @property
    def z_center_index(self):
        if ('z_center_index' not in self.var.keys()):
            self.find_center()
        return self.var.get('z_center_index')

    @property
    def z(self): return (self.z_index-self.z_center_index)*self.pixel_binned*1e6

    @property
    def z_TF_index(self):
        if ('z_TF_index' not in self.var.keys()):
            self.find_center()
        return self.var.get('z_TF_index')

    @property
    def z_TF(self):
        return self.z_TF_index*self.pixel_binned*1e6

    @property
    def V_TF(self): return thermodynamics.z2V(self.z_TF,self.trap_f_z)

    @property
    def Vz(self):
        return thermodynamics.z2V(self.z,self.trap_f_z)

    @property
    def x_index(self): return np.array(range(0,self.app.shape[1]))

    @property
    def n_1d_z(self): return np.sum(self.app,1)/(self.pixel_binned*1e6)

    @property
    def P_z(self): return (1/(2*np.pi))*cst_LiD2.mass*(self.trap_f_r*2*np.pi)**2*self.n_1d_z*1e6/(cst_ODT_Class.h)/1e18

    @property
    def T_trap_Boltzmann(self):
        if ('T_trap_Boltzmann' not in self.var.keys()):
            self.HighTemperatureThermo()
        return self.var.get('T_trap_Boltzmann')

    @property
    def P_max(self):
        P_avg=self.P_z[self.Vz<150]
        return np.mean(P_avg)

    @property
    def n0_trap_Boltzmann(self):
        if ('n0_trap_Boltzmann' not in self.var.keys()):
            self.HighTemperatureThermo()
        return self.var.get('n0_trap_Boltzmann')

    @property
    def P0_trap_Boltzmann(self):
        if ('P0_trap_Boltzmann' not in self.var.keys()):
            self.HighTemperatureThermo()
        return self.var.get('P0_trap_Boltzmann')

    @property
    def EF0_trap_Boltzmann(self):
        return thermodynamics.n2EF(self.n0_trap_Boltzmann)
    @property
    def n0_trap_peak(self):
        return self.P_max/self.T_trap_Boltzmann

    @property
    def EF0_trap_peak(self):
        return thermodynamics.n2EF(self.n0_trap_peak)

    def find_center(self, ifplot=False):
        nz_temp=np.sum(self.app,1)
        P, P_jac = thermodynamics.TF_project_z_fit(self.z_index, nz_temp, 100)
        z_center=P[1];
        z_TF=P[2];
        self.var['z_center_index']=z_center
        self.var['z_TF_index']=z_TF

        if ifplot:
            plt.plot(self.z_index,nz_temp)
            plt.plot(self.z_index,thermodynamics.TFfun_project_z(self.z_index,*P))
            plt.show()


        return  z_center

    def find_radial_f(self, ifplot=False):
        mask_fit=np.abs(self.z_index-self.z_center_index)<(self.z_TF_index*self.r_TF_fitrange)
        z_fit=self.z[mask_fit]
        r_TF_fit=z_fit*0
        image_clip=self.app[mask_fit]
        P_list=[]
        for i in range(0,image_clip.shape[0]):
            n_r_fit=image_clip[i]
            P_temp,Pjac_temp=thermodynamics.TF_project_r_fit(self.x_index,n_r_fit,20)
            r_TF_fit[i]=P_temp[2]*self.pixel_binned*1e6
            P_list.append(P_temp)

        self.var['P_list_Radial_TF']=P_list

        Vz_fit=thermodynamics.z2V(z_fit,self.trap_f_z)
        Vr_fit=thermodynamics.z2V(r_TF_fit,1)

        P,V = np.polyfit(Vz_fit, Vr_fit, 1, cov=True)
        omega_r=np.sqrt(1 / -P[0])
        omega_r_err=np.sqrt(V[0,0])/np.abs(P[0])*np.sqrt(1/-P[0])/2

        self.var['omega_r_fit']=omega_r
        self.var['omega_r_fit_err']=omega_r_err


        if ifplot:
            f = plt.figure(figsize=[12, 4])
            ax1 = plt.subplot(1, 2, 1)

            k1 = 0
            k2 = round(image_clip.shape[0]/4)
            k3 = round(image_clip.shape[0]/2)

            V1_plot=Vz_fit[k1]
            P1_plot=P_list[k1]
            n1_plot=image_clip[k1]
            n1_fit_plot=thermodynamics.TFfun_project_r(self.x_index,*P1_plot)
            x1_plot=(self.x_index-P1_plot[1])*self.pixel_binned*1e6


            V2_plot = Vz_fit[k2]
            P2_plot = P_list[k2]
            n2_plot = image_clip[k2]
            n2_fit_plot = thermodynamics.TFfun_project_r(self.x_index, *P2_plot)
            x2_plot = (self.x_index - P2_plot[1]) * self.pixel_binned * 1e6

            V3_plot = Vz_fit[k3]
            P3_plot = P_list[k3]
            n3_plot = image_clip[k3]
            n3_fit_plot = thermodynamics.TFfun_project_r(self.x_index, *P3_plot)
            x3_plot = (self.x_index - P3_plot[1]) * self.pixel_binned * 1e6

            ax1.plot(x1_plot,n1_plot,x1_plot,n1_fit_plot)
            ax1.plot(x2_plot, n2_plot, x2_plot, n2_fit_plot)
            ax1.plot(x3_plot, n3_plot, x3_plot, n3_fit_plot)
            plt.xlabel('x [um]')
            plt.ylabel(r'$n_{2D} [a.u.]$')


            ax2 = plt.subplot(1, 2, 2)

            ax2.plot(Vz_fit, Vr_fit, marker='o', markersize=2, linestyle='None')
            Vz_fit_plot = np.linspace(0, max(Vz_fit), 300)
            Vr_fit_plot = np.polyval(P, Vz_fit_plot)
            ax2.plot(Vz_fit_plot, Vr_fit_plot)
            plt.xlabel(r'$1/2m {\omega_z}^2 z^2$ [Hz]')
            plt.ylabel(r'$1/2m r_{TF}^2 [Hz^{-1}]$')

            f.suptitle(r'Radial TF fit, $\omega_r=2\pi \times {:0.1f} \pm  {:0.1f} s^{{-1}}$'.format(omega_r,omega_r_err))
            plt.tight_layout()
            plt.subplots_adjust(top=0.85)
            plt.show()

        return omega_r,omega_r_err

    def HighTemperatureThermo(self):

        Vth=self.Boltzmann_limit
        V_fit=self.Vz[self.Vz>Vth]
        P_fit=self.P_z[self.Vz>Vth]

        P_B,Pjac_B = thermodynamics.BoltzmannFit(V_fit,P_fit,[np.nanmax(self.P_z),3000])

        self.var['T_trap_Boltzmann']=P_B[1]
        self.var['n0_trap_Boltzmann']=P_B[0]/P_B[1]
        self.var['P0_trap_Boltzmann']=P_B[0]
        return 0

    def plot_Boltzmann(self):

        f = plt.figure(figsize=[7, 4])
        ax1 = plt.subplot(1, 1, 1)

        V_max=np.max([self.V_TF*2,self.T_trap_Boltzmann*3])
        V_fit_plot=np.linspace(0,V_max,500)
        P_fit_plot=thermodynamics.Boltzmann([self.P0_trap_Boltzmann,self.T_trap_Boltzmann],V_fit_plot)


        plt.plot(self.Vz, self.P_z, marker='.',linestyle='none')
        plt.plot(V_fit_plot, P_fit_plot, linewidth=2)
        plt.axvline(self.Boltzmann_limit, linestyle='--', color='k', linewidth=2)
        plt.xlim([0, V_max])

        plt.xlabel(r'$V_z$ [Hz]')
        plt.ylabel(r'P [$Hz \cdot um^{-3}$]')

        f.suptitle(r'Boltzmann Fitting with $k_B T$= {:.0f} Hz'.format(self.T_trap_Boltzmann))
        plt.tight_layout()
        plt.subplots_adjust(top=0.85)
        plt.show()

#####


####################################################################################
############################ XSectionHybrid ########################################

# XSectionHybrid Class Definition
# Compute 1d density from atoms per pixel

# for an ellipse with horizontal length a and vertical length b. Area from -A to A in horizontal
@np.vectorize
def area_partial_ellipse(A, a, b=None):
    if b is None: b = a
    if A >= a: return np.pi*a*b
    return 2*A*b*np.sqrt(1-(A/a)**2) + 2*a*b*np.arcsin(A/a)

'''Cross Section Hybrid'''
class XSectionHybrid:
    '''
    Take od and compute center and radius for each z_pixel

    Inputs :
        1) od
        2) bg_width
        3) ellipticity
        4) xsec_extension_method = 'polyN' or 'linear
        5) xsec_slice_width = 5, number of pixels to average for circle fits
        6) xsec_fit_range = 1, multiplies the fitted gaussian sigma

    Procedure:
        1) Approximate cloud center and fit gaussian
        2) Fit circles in provided region; store left, right, center
        3) Extend the results to entire image
        4) Functions for left, right, center, radius, area, sub_area(l, r)
    '''

    def __init__(self, od, ellipticity=1, extension='default', slice_width=4, fit_range=1.75):
        # Process Inputs
        self.data = od
        self.var = dict(ellipticity=ellipticity, extension=extension,
                        slice_width=slice_width, fit_range=fit_range)
        # Get fitting range
        self.z_edges, self.z_center = self.circle_fitting_range()
        # Fit circles
        self.center_fit, self.radius_fit = self.fit_circles()
        # Extrapolate
        self.z, self.center, self.radius = self.extrapolate()
        
    def circle_fitting_range(self, ):
        '''
        Get approximate center and radius by a Thomas-Fermi fit
        Use region radius*fit_range for circle fitting
        '''
        # Inputs
        slice_width = self.var['slice_width']
        fit_range = self.var['fit_range']
        # Integrate hybrid
        c = Curve(y = np.nanmean(self.data, axis=1))
        c.removenan()
        # Fit Gaussian
        def fitfun(x, x0, sigma, amp, a0):
            return np.exp(- (x-x0)**2 / (2*sigma**2)) * amp + a0
        guess = [c.x.shape[0]/2, 34, np.max(c.y), np.mean(c.y[0:10])]
        fitres = c.fit(fitfun, guess, plot=False)[0]
        center, radius_use = round(fitres[0]), round(fitres[1] * fit_range)
        # z_edges and z_center arrays
        z_edges = np.arange(center - radius_use, center + radius_use, slice_width, dtype=np.int)
        z_center = z_edges[0:-1] + (z_edges[1]-z_edges[0])/2.0 - 0.5 # half because slice doesn't include end point
        return (z_edges, z_center)
        
    def fit_circles(self):
        '''
        Fit circles to the range specified
        Measure center and radius at each point
        '''
        # Inputs
        z_center, z_edges = self.z_center, self.z_edges
        # Prepare arrays
        center, radius = np.zeros_like(z_center), np.zeros_like(z_center)
        # Replace infinities with nan
        use_data = self.data.copy()
        use_data[~np.isfinite(use_data)] = np.nan
        # Fit gaussian to the central slice to get initial guesses for circle fits
        def fitfun(x, x0, sigma, amp, a0):
            return np.exp(- (x-x0)**2 / (2*sigma**2)) * amp + a0
        i = len(z_center) // 2
        c = Curve(y = np.nanmean(use_data[z_edges[i]:z_edges[i+1],:], axis=0))
        c.removenan()
        guess = (c.x.shape[0] / 2, c.x.shape[0] / 5, np.max(c.y), np.mean(c.y[0:10]))
        fitres_gauss = c.fit(fitfun, guess, plot=False)[0]
        # Fit circles to each slices
        for i in range(self.z_center.size):
            c = Curve(y = np.nanmean(use_data[z_edges[i]:z_edges[i+1],:], axis=0))
            c.removenan()
            guess = (fitres_gauss[0], fitres_gauss[1]*1.75, np.max(c.y), fitres_gauss[3])
            fitres = c.fit(self.fitfun_circle, guess, plot=False)[0]
            if fitres[0] == guess[0]:
                center[i], radius[i] = np.nan, np.nan
            else: center[i], radius[i] = fitres[0], fitres[1]
        # return results
        return (center, radius)
    
    def extrapolate(self):
        '''
        Extrapolate the fitted center and radius
        using either polyN or splineN method
        '''
        # Inputs
        method = self.var['extension']
        z_center_fit, center_fit, radius_fit = self.z_center, self.center_fit, self.radius_fit
        # Empty arrays for storage
        z, center, radius = np.arange(self.data.shape[0]), np.arange(self.data.shape[0]), np.arange(self.data.shape[0])
        c_center = Curve(z_center_fit, center_fit)
        c_center.removenan()
        c_radius = Curve(z_center_fit, radius_fit)
        c_radius.removenan()
        # Linearly extend the center
        fitres = np.poly1d(np.polyfit(*c_center.plotdata, deg=1))
        center = fitres(z)
        # polyN
        if method[0:4] == 'poly':
            fitres = np.poly1d(np.polyfit(*c_radius.plotdata, deg=int(method[4:])))
            radius = fitres(z)
            radius[z<z_center_fit[0]] = fitres(z_center_fit[0])
            radius[z>z_center_fit[-1]] = fitres(z_center_fit[-1])
        elif method == 'linear':
            fitres = np.poly1d(np.polyfit(*c_radius.plotdata, deg=1))
            radius = fitres(z)
        else:
            def fitfun(x, a0, a1=0, a2=0): return a0 + a1*x + a2*x**2
            fitres = c_radius.fit(fitfun, [np.mean(c_radius.y), 0, 0], noise=1, plot=False)[0]
            radius = fitfun(z, *fitres)
            radius[z<z_center_fit[0]] = fitfun(z_center_fit[0], *fitres)
            radius[z>z_center_fit[-1]] = fitfun(z_center_fit[-1], *fitres)
        # Return
        return (z, center, radius)
    
    '''
    Useful calls to get center, radius, left, right, area, and sub_area
    '''
    def get_center(self, z):
        z = np.array(z, dtype=np.int32)
        return self.center[z]
    
    def get_radius(self, z):
        z = np.array(z, dtype=np.int32)
        return self.radius[z]
    
    def get_left(self, z):
        return self.get_center(z) - self.get_radius(z)
    
    def get_right(self, z):
        return self.get_center(z) + self.get_radius(z)
    
    def get_area(self, z):
        return np.pi * self.get_radius(z)**2 * self.var['ellipticity']
    
    def get_subarea(self, z, l, r):
        a = self.get_radius(z)
        b = a * self.var['ellipticity']
        Al = self.get_center(z) - l
        Ar = r - self.get_center(z)
        
        # Check for errors
        if np.any(Al <= 0) or np.any(Ar <= 0):
            print("Illegal left and right points given to XSectionHybrid.get_subarea. Returned total area.")
            return self.get_area(z)
        
        return area_partial_ellipse(Al,a,b)/2 + area_partial_ellipse(Ar,a,b)/2
    
    
    def infoplot(self, axs=None, left=None, right=None):
        '''
        Useful information plots: data with fitted center and radius + extrapolation
        Ability to plot on provided axes
        '''
        if axs is None:
            fig, axs = plt.subplots(figsize=(5,5), nrows=2)
        axs[0].imshow(self.data.T, cmap='viridis', aspect='auto', origin='lower')
        axs[0].plot(self.z, self.center,'w--',alpha=0.5)
        axs[0].plot(self.z, self.center - self.radius,'w--',alpha=0.5)
        axs[0].plot(self.z, self.center + self.radius,'w--',alpha=0.5)
        axs[0].scatter(self.z_center, self.center_fit - self.radius_fit,color='white', s=2)
        axs[0].scatter(self.z_center, self.center_fit + self.radius_fit,color='white', s=2)
        axs[0].scatter(self.z_center, self.center_fit,color='white', s=2)
        axs[0].set(xlim=(self.z[0],self.z[-1]))
        axs[0].set_axis_off()
        
        if left is not None and right is not None:
            axs[0].plot(left,'r-',alpha=0.7)
            axs[0].plot(right,'r-',alpha=0.7)
        
        axs[1].scatter(self.z_center, self.radius_fit,color='red')
        axs[1].plot(self.z, self.radius,'k')
        axs[1].set(xlim=(self.z[0],self.z[-1]), ylabel='Radius')
        
    def fitfun_circle(self, x, x0, rad, amp, a0):
        y = 1 - ((x - x0) / rad) ** 2
        y[y <= 0] = 0
        y[y > 0] = np.sqrt(y[y > 0]) * amp
        y += a0
        return y

    
    
####################################################################################
################################ Density_Generatos #################################
    
    
# Standalone Density Generator 

# Load pre-compiled data
p_ = roots1.getpath('Projects','Data','EoS','Mark_Density_EoS_Extended_Data4Python.p')
if not os.path.isfile(p_):
    print("Downloading Database -- Might take some time!")
    url = "https://www.dropbox.com/s/abxs9yarrgohzy8/Mark_Density_EoS_Extended_Data4Python.p?dl=1"
    u = urllib.request.urlopen(url)
    data = u.read()
    u.close()
    # Create folder
    os.makedirs(os.path.split(p_)[0], exist_ok=True)
    with open(p_, "wb") as f :
        f.write(data)
precompiled_data_EoS_Density_Generator = pickle.load( open( p_, "rb" ) )

# Other needed functions
constants_for_density_ = constants.cst()
constants_for_density_.c1 = ((constants_for_density_.twopi * constants_for_density_.hbar**2)/(constants_for_density_.mass))**(1/2)
constants_for_density_.c2 = 1/(6*constants_for_density_.pi**2) * (2*constants_for_density_.mass/constants_for_density_.hbar**2)**(3/2)
constants_for_density_.xi = 0.37
constants_for_density_.virial_coef = [1, 3*2**(1/2)/8, -0.29095295, 0.065]

def thermal_wavelength(kT):
    return constants_for_density_.c1 / (kT)**(1/2)

@np.vectorize
def density_ideal(kT, mu):
    if kT == 0:
        if mu <= 0:
            print('Density is undefined for negative mu and zero temperature')
            return 0
        return cst_.c2 * (mu)**(3/2)
    return thermal_wavelength(kT)**(-3) * functions.FermiFunction(m=3/2, logz=mu/kT)

@np.vectorize
def density_virial(kT, mu):
    if kT == 0: return 0
    return kT / thermal_wavelength(kT)**3 * (constants_for_density_.virial_coef[0]*1/kT*np.exp(1*mu/kT) + constants_for_density_.virial_coef[1]*2/kT*np.exp(2*mu/kT) + constants_for_density_.virial_coef[2]*3/kT*np.exp(3*mu/kT) + constants_for_density_.virial_coef[3]*4/kT*np.exp(4*mu/kT))

# Setup function
@np.vectorize
def density_unitary(kT, mu):
    # Zero T
    if kT < 0:
        return 0
    if kT == 0:
        return constants_for_density_.EF2n(mu/constants_for_density_.xi, neg=True)
    if mu/kT > 4:
        return constants_for_density_.EF2n(mu / precompiled_data_EoS_Density_Generator[0](kT/mu), neg=True)
    if mu/kT > -0.5:
        return constants_for_density_.EF2n(mu / precompiled_data_EoS_Density_Generator[1](mu/kT), neg=True)
    return density_virial(kT, mu)
    
    
    

####################################################################################
################################ Hybrid_Image ######################################


cst_Hybrid_Image = constants.cst()

class Hybrid_Image(Image):
    def __init__(self, name=None, path=None, od=None, **kwargs):
        # Initialize the complete Image Object
        super(Hybrid_Image, self).__init__(name=name, path=path, od=od, **kwargs)

        Default_Hybrid_Image = dict(ellipticity=1, xsec_extension='default',xsec_slice_width=4,
                                    xsec_fit_range=1.75, xsec_override=False, trap_f=23.9,
                                    radial_selection=0.7, trap_center_override=False, kind='unitary',
                                    Tfit_lim=0.2, Tfit_guess_kT=0.5, Tfit_guess_mu0=1)

        Level_Selector_Hybrid_Image = [['ellipticity','xsec_extension', 'xsec_slice_width','xsec_fit_range', 'xsec_override'],
                                       ['fudge','sigmaf','sigma','pixel','trap_f','radial_selection','trap_center_override'],
                                       ['kind','Tfit_lim', 'Tfit_guess_kT', 'Tfit_guess_mu0']]

        # Addons
        self.var = {**self.var, **Default_Hybrid_Image, **kwargs}
        self.LevelAdder = len(self.var['Level_Selector'])
        self.var['Level_Selector'] = self.var['Level_Selector'] + list(Level_Selector_Hybrid_Image)
        self.var['recalc'] = self.var['recalc'] + [True]*len(Level_Selector_Hybrid_Image)

    # New Properties
    @property
    def ellipticity(self,): return self.var.get('ellipticity')

    @property
    def xsec_extension(self,): return self.var.get('xsec_extension')

    @property
    def xsec_slice_width(self,): return self.var.get('xsec_slice_width')

    @property
    def xsec_fit_range(self,): return self.var.get('xsec_fit_range')

    @property
    def xsec(self,):
        if (self.var['xsec_override'] is not False):
            xsec_override = self.var['xsec_override']
            xsec_override.data = self.od
            return xsec_override
        if self.recalc[0 + self.LevelAdder] or ('xsec' not in self.var.keys()):
            self.compute_xsec()
        return self.var.get('xsec')

    @property
    def trap_f(self,): return self.var.get('trap_f')

    @property
    def trap_w(self,): return 2 * np.pi * self.trap_f

    @property
    def radial_selection(self,): return self.var.get('radial_selection')

    @property
    def trap_center(self,):
        if self.var['trap_center_override'] is not False:
            return self.var['trap_center_override']
        if ('trap_center' not in self.var.keys()) or self.recalc[1 + self.LevelAdder]:
            self.compute_nz()
        return self.var['trap_center']

    @property
    def z(self,): return (np.arange(self.app.shape[0]) - self.trap_center) * self.pixel_binned

    @property
    def u(self,): return 0.5*cst_LiD2.mass*self.trap_w**2*self.z**2

    @property
    def n(self,):
        if ('n' not in self.var.keys()) or self.recalc[1 + self.LevelAdder]:
            self.compute_nz()
        return self.var['n']

    @property
    def N(self,):
        if ('N' not in self.var.keys()) or self.recalc[1 + self.LevelAdder]:
            self.compute_nz()
        return self.var['N']

    @property
    def nz(self,): return Curve(x=self.z, y=self.n, xscale=1e-6, yscale=1e18)

    @property
    def nu(self,): return Curve(x=self.u, y=self.n, xscale=1e3*cst_LiD2.h, yscale=1e18)

    @property
    def EFu(self,): return Curve(x=self.u, y=cst_LiD2.n2EF(self.n, neg=True), xscale=1e3*cst_LiD2.h, yscale=1e3*cst_LiD2.h)

    @property
    def ku(self,):
        EFu = self.EFu.sortbyx().subsample(bins=2)
        ku = EFu.diff(method='poly', order=1, points=4)
        return Curve(x=ku.x, y=-ku.y, xscale=ku.xscale).subsample(bins=2)

    @property
    def kz_u(self,):
        ku = self.ku
        z = (2 * ku.x / cst_LiD2.mass / self.trap_w**2 )**(1/2)
        return Curve(x=np.concatenate([np.flipud(-z), z]), y=np.concatenate([np.flipud(ku.y), ku.y]), xscale=1e-6, yscale=1)

    @property
    def kind(self,): return self.var.get('kind')

    @property
    def Tfit_lim(self,): return self.var.get('Tfit_lim')

    @property
    def Tfit_guess(self,): return [self.var.get('Tfit_guess_kT'), self.var.get('Tfit_guess_mu0')]

    @property
    def T_kHz(self,):
        if ('T_kHz' not in self.var.keys()) or self.recalc[2 + self.LevelAdder]:
            self.compute_temperature()
        return self.var['T_kHz']

    @property
    def mu0_kHz(self,):
        if ('mu0_kHz' not in self.var.keys()) or self.recalc[2 + self.LevelAdder]:
            self.compute_temperature()
        return self.var['mu0_kHz']

    @property
    def TTF(self,):
        return self.T_kHz * 1e3 * cst_LiD2.h / cst_LiD2.n2EF(self.n, neg=True)

    @property
    def TTF_center(self,):
        fitfun, fitres = self.var['Tfit_info']
        n_center = np.max(fitfun(self.nz.x, *fitres))
        return self.T_kHz * 1e3 / cst_LiD2.n2EFHz(n_center)

    @property
    def Tfit_residual(self,):
        return np.nanmean(np.abs(self.var['Tfit_info'][0](self.nz.x, *self.var['Tfit_info'][1]) - self.n))

    # Procedures
    def compute_xsec(self,):
        xsec = XSectionHybrid(self.od, ellipticity=self.ellipticity, extension=self.xsec_extension,
                                   slice_width=self.xsec_slice_width, fit_range=self.xsec_fit_range)
        self.var['recalc'][0 + self.LevelAdder] = False
        self.var['xsec'] = xsec

    def compute_nz(self,):
        # Compute n(i)
        i = np.arange(self.app.shape[0])
        l = i*0
        r = i*0 + self.app.shape[1] - 1

        if (self.radial_selection == 1) or (self.radial_selection==0):
            N = np.nansum(self.app, axis=1)
            n = N / (self.xsec.get_area(i) * self.pixel_binned**3)
        elif self.radial_selection < 1:
            l = np.array(np.round(self.xsec.get_center(i) - self.xsec.get_radius(i) * self.radial_selection), dtype=np.int)
            r = np.array(np.round(self.xsec.get_center(i) + self.xsec.get_radius(i) * self.radial_selection), dtype=np.int)
            N = np.array([np.nansum(self.app[j, l[j]:1+r[j]]) for j in i])
            n = N / (self.xsec.get_subarea(i, l-0.5, r+0.5) * self.pixel_binned**3)
        elif self.radial_selection > 1:
            l = np.array(np.round(self.xsec.get_center(i) - self.radial_selection), dtype=np.int)
            r = np.array(np.round(self.xsec.get_center(i) + self.radial_selection), dtype=np.int)
            N = np.array([np.nansum(self.app[j, l[j]:1+r[j]]) for j in i])
            n = N / (self.xsec.get_subarea(i, l-0.5, r+0.5) * self.pixel_binned**3)
        # Note that l-0.5 and r+0.5 are used because of the way integrals over pixels work out. Has been tested!
        ni = Curve(x=i, y=n)

        # Find Center i0
        def fitfun(x, x0, rad, amp, a0):
            y = np.real((1-((x-x0)/(rad))**2)**(3/2))
            y[~np.isfinite(y)] = 0
            return amp*y + a0
        guess = [ni.x[ni.y==ni.maxy][0], ni.x.size/5, ni.maxy, np.mean(ni.y[0:5])]
        fitres = ni.fit(fitfun, guess, plot=False)[0]

        # Store
        self.var['trap_center'] = fitres[0]
        self.var['n'] = n
        self.var['N'] = N
        self.var['radial_selection_info'] = (l, r)
        self.var['recalc'][1 + self.LevelAdder] = False

    def compute_temperature(self,):
        nz = self.nz
        if (self.kind == 'unitary') or (self.kind == 'balanced'):
            def fitfun(z, kT, mu0, a0=0, z0=0):
                kT *= 1e3*cst_LiD2.h
                mu0 *= 1e3*cst_LiD2.h
                mu = mu0 - 1/2 * cst_LiD2.mass * self.trap_w**2 * (z-z0*1e-6)**2
                return density_unitary(kT, mu) + a0
        elif (self.kind == 'ideal') or (self.kind == 'polarized'):
            def fitfun(z, kT, mu0, a0=0, z0=0):
                kT *= 1e3*cst_LiD2.h
                mu0 *= 1e3*cst_LiD2.h
                mu = mu0 - 1/2 * cst_LiD2.mass * self.trap_w**2 * (z-z0*1e-6)**2
                return density_ideal(kT, mu) + a0
        fitres = nz.fit(fitfun, [self.Tfit_guess[0], self.Tfit_guess[1], np.mean(nz.y[0:5])], plot=False, ylim=(-np.inf, self.Tfit_lim*1e18))[0]

        # Store
        self.var['T_kHz'] = fitres[0]
        self.var['mu0_kHz'] = fitres[1]
        self.var['Tfit_info'] = (fitfun, fitres)
        self.var['recalc'][2 + self.LevelAdder] = False


    # Plots
    def plot_hybrid_info(self,ulim=10, zlim=250, klim=(-0.5,3.5), output=False):
        fig = plt.figure(figsize = (12,7))
        ax1 = fig.add_subplot(4,3,1)
        ax2 = fig.add_subplot(4,3,4)
        ax3 = fig.add_subplot(2,3,2)
        ax4 = fig.add_subplot(2,3,3)
        ax5 = fig.add_subplot(4,3,7)
        ax6 = fig.add_subplot(4,3,10)
        ax7 = fig.add_subplot(2,3,5, sharex=ax3)
        ax8 = fig.add_subplot(2,3,6, sharex=ax4, sharey=ax7)
        # plots
        ax3.plot(*self.nz.plotdata)
        ax3.plot(self.nz.plotdata[0], self.nz.x*0, 'k--', alpha=0.5)
        ax3.plot([0,0], [0, self.nz.maxy/self.nz.yscale], 'k--', alpha=0.5)
        ax4.plot(*self.EFu.plotdata)
        ax4.plot(self.EFu.plotdata[0], self.EFu.x*0, 'k--', alpha=0.5)
        ax3.set(xlabel=r'z [$\mu m$]', ylabel=r'n [$\mu m ^{-3}$]', title='Density', xlim=[-zlim, zlim])
        ax4.set(xlabel=r'u [kHz]', ylabel=r'$E_F$ [kHz]', title='Fermi Energy', xlim=[0, ulim])
        self.xsec.infoplot([ax1, ax2], *self.var['radial_selection_info'])
        ax7.plot(*self.kz_u.plotdata)
        ax7.plot(self.kz_u.plotdata[0], self.kz_u.x*0+1, 'k--', self.kz_u.plotdata[0], self.kz_u.x*0+1/0.37, 'k--', self.kz_u.plotdata[0], self.kz_u.x*0, 'k--', alpha=0.5)
        ax7.set(xlabel=r'z [$\mu$ m]', ylabel=r'$\kappa / \kappa_0$', ylim=klim)
        ax8.plot(*self.ku.plotdata)
        ax8.plot(self.ku.plotdata[0], self.ku.x*0+1, 'k--', self.ku.plotdata[0], self.ku.x*0+1/0.37, 'k--', self.ku.plotdata[0], self.ku.x*0, 'k--', alpha=0.5)
        ax8.set(xlabel=r'u [kHz]', title=self.name)
        axs = (ax1, ax2, ax5, ax6, ax3, ax4, ax7, ax8)
        fig.tight_layout(pad=0.1, h_pad=0, w_pad=0)
        if output: return (fig, axs)

    def plot_hybrid_temp_info(self, ulim=10, zlim=250, klim=(-0.5,3.5), Tlim=None, Tstep = None):
        fig, ax = self.plot_hybrid_info(ulim=ulim, zlim=zlim, klim=klim, output=True)

        nz = self.nz
        TTF = self.TTF
        fitfun, fitres = self.var['Tfit_info']
        nz_fit = Curve(x = nz.x, y = fitfun(nz.x, *fitres), xscale=nz.xscale, yscale=nz.yscale)
        # Plot fitted profile
        ax[4].plot(*nz_fit.plotdata, alpha=0.75)
        if nz.maxy >= self.Tfit_lim*1e18: ax[4].plot(nz.plotdata[0], nz.x*0 + self.Tfit_lim, 'k--', alpha=0.5)
        ax[4].set(title='Density, Center T/TF {:.2f}'.format(self.TTF_center))

        # Plot Residuals
        ax[2].plot(nz.plotdata[0], 100 * (nz.y - nz_fit.y) / nz.yscale)
        ax[2].plot(nz.plotdata[0], nz.x*0, 'k--', alpha=0.5)
        ax[2].set(xlim=[-zlim,zlim], ylabel=r'Res [100 $\times$ $\mu m ^{-3}$]', xlabel=r'z [$\mu$m]')
        ax[2].set(title='Offset {:.2f} [100 x um^-3]'.format(fitres[2]/1e18*100))

        # Information
        ax[6].set(title=r'T = {:.2f} kHz, $\mu_0$ = {:.2f} kHz'.format(fitres[0], fitres[1]))

        # Histogram of N(T/TF)
        if fitres[0] <= 0.02: return None
        if Tlim is None: Tlim = TTF[np.abs(nz.x) == np.abs(nz.x).min()][0] * 3
        if Tstep is None: Tstep = np.round(TTF[np.abs(nz.x) == np.abs(nz.x).min()][0]/10, 3)
        c = Curve(TTF, self.N)
        c.removenan()
        c = c.sortbyx().trim(xlim=[0, Tlim]).binbyx(step=Tstep, sects=[0,Tlim], func=np.nansum, center_x=True)
        ax[3].bar(left = c.x - Tstep/2, height = c.y / np.nansum(c.y * Tstep), width=Tstep)
        ax[3].plot([0.17]*2, [0, 1], 'k--', alpha=0.5)
        ax[3].set(xlabel=r'$T/T_F$', ylabel=r'Fraction of Atoms', xlim=(0, Tlim), ylim=(0, np.nanmax(c.y / np.nansum(c.y * Tstep))*1.1))


# Default_Hybrid_Image = dict(ellipticity=1, xsec_extension='default',xsec_slice_width=4,
#                             xsec_fit_range=1.75, xsec_override=False, trap_f=23.9,
#                             radial_selection=0.7, trap_center_override=False, kind='unitary',
#                             Tfit_lim=0.2, Tfit_guess_kT=0.5, Tfit_guess_mu0=1)
#
# Level_Selector_Hybrid_Image = [['ellipticity','xsec_extenstion', 'xsec_slice_width','xsec_fit_range', 'xsec_override'],
#                                ['fudge','sigmaf','sigma','pixel','trap_f','radial_selection','trap_center_override'],
#                                ['kind','Tfit_lim', 'Tfit_guess_kT', 'Tfit_guess_mu0']]

# class Hybrid_Image(Image):
#     def __init__(self, name=None, path=None, od=None, **kwargs):
#         # Initialize the complete Image Object
#         super(Hybrid_Image, self).__init__(name=name, path=path, od=od, **kwargs)
#
#         # Addons
#         self.var = {**self.var, **Default_Hybrid_Image, **kwargs}
#         self.LevelAdder = len(self.var['Level_Selector'])
#         self.var['Level_Selector'] = self.var['Level_Selector'] + list(Level_Selector_Hybrid_Image)
#         self.var['recalc'] = self.var['recalc'] + [True]*len(Level_Selector_Hybrid_Image)
#
#     # New Properties
#     @property
#     def ellipticity(self,): return self.var.get('ellipticity')
#
#     @property
#     def xsec_extension(self,): return self.var.get('xsec_extension')
#
#     @property
#     def xsec_slice_width(self,): return self.var.get('xsec_slice_width')
#
#     @property
#     def xsec_fit_range(self,): return self.var.get('xsec_fit_range')
#
#     @property
#     def xsec(self,):
#         if (self.var['xsec_override'] is not False):
#             xsec_override = self.var['xsec_override']
#             xsec_override.data = self.od
#             return xsec_override
#         if self.recalc[0 + self.LevelAdder] or ('xsec' not in self.var.keys()):
#             self.compute_xsec()
#         return self.var.get('xsec')
#
#
#     @property
#     def trap_f(self,): return self.var.get('trap_f')
#
#     @property
#     def trap_w(self,): return 2 * np.pi * self.trap_f
#
#     @property
#     def radial_selection(self,): return self.var.get('radial_selection')
#
#     @property
#     def trap_center(self,):
#         if self.var['trap_center_override'] is not False:
#             return self.var['trap_center_override']
#         if ('trap_center' not in self.var.keys()) or self.recalc[1 + self.LevelAdder]:
#             self.compute_nz()
#         return self.var['trap_center']
#
#     @property
#     def z(self,): return (np.arange(self.app.shape[0]) - self.trap_center) * self.pixel_binned/1e-6
#
#     @property
#     def u(self,): return (0.5*cst_Hybrid_Image.mass*self.trap_w**2*(self.z*1e-6)**2)/cst_Hybrid_Image.h
#
#     @property
#     def n(self,):
#         if ('n' not in self.var.keys()) or self.recalc[1 + self.LevelAdder]:
#             self.compute_nz()
#         return self.var['n']/1e18
#
#     @property
#     def EF(self): return thermodynamics.n2EF(self.n)
#
#     @property
#     def N(self,):
#         if ('N' not in self.var.keys()) or self.recalc[1 + self.LevelAdder]:
#             self.compute_nz()
#         return self.var['N']
#
#
#     # Procedures
#     def compute_xsec(self,):
#         xsec = XSectionHybrid(self.od, ellipticity=self.ellipticity, extension=self.xsec_extension,
#                                    slice_width=self.xsec_slice_width, fit_range=self.xsec_fit_range)
#         self.var['recalc'][0 + self.LevelAdder] = False
#         self.var['xsec'] = xsec
#
#     def compute_nz(self,):
#         # Compute n(i)
#         i = np.arange(self.app.shape[0])
#         l = i*0
#         r = i*0 + self.app.shape[1] - 1
#
#         if (self.radial_selection == 1) or (self.radial_selection==0):
#             N = np.nansum(self.app, axis=1)
#             n = N / (self.xsec.get_area(i) * self.pixel_binned**3)
#         elif self.radial_selection < 1:
#             l = np.array(np.round(self.xsec.get_center(i) - self.xsec.get_radius(i) * self.radial_selection), dtype=np.int)
#             r = np.array(np.round(self.xsec.get_center(i) + self.xsec.get_radius(i) * self.radial_selection), dtype=np.int)
#             N = np.array([np.nansum(self.app[j, l[j]:1+r[j]]) for j in i])
#             n = N / (self.xsec.get_subarea(i, l-0.5, r+0.5) * self.pixel_binned**3)
#         elif self.radial_selection > 1:
#             l = np.array(np.round(self.xsec.get_center(i) - self.radial_selection), dtype=np.int)
#             r = np.array(np.round(self.xsec.get_center(i) + self.radial_selection), dtype=np.int)
#             N = np.array([np.nansum(self.app[j, l[j]:1+r[j]]) for j in i])
#             n = N / (self.xsec.get_subarea(i, l-0.5, r+0.5) * self.pixel_binned**3)
#         # Note that l-0.5 and r+0.5 are used because of the way integrals over pixels work out. Has been tested!
#         ni = Curve(x=i, y=n)
#
#         # Find Center i0
#         def fitfun(x, x0, rad, amp, a0):
#             y = np.real((1-((x-x0)/(rad))**2)**(3/2))
#             y[~np.isfinite(y)] = 0
#             return amp*y + a0
#         guess = [ni.x[ni.y==ni.maxy][0], ni.x.size/5, ni.maxy, np.mean(ni.y[0:5])]
#         fitres = ni.fit(fitfun, guess, plot=False)[0]
#
#         # Store
#         self.var['trap_center'] = fitres[0]
#         self.var['n'] = n
#         self.var['N'] = N
#         self.var['radial_selection_info'] = (l, r)
#         self.var['recalc'][1 + self.LevelAdder] = False
#
#     def plot_hybrid_info(self,ulim=10, zlim=250, klim=(-0.5,3.5), output=False):
#         fig = plt.figure(figsize = (12,7))
#         ax1 = fig.add_subplot(4,3,1)
#         ax2 = fig.add_subplot(4,3,4)
#         ax3 = fig.add_subplot(2,3,2)
#         ax4 = fig.add_subplot(2,3,3)
#         ax5 = fig.add_subplot(4,3,7)
#         ax6 = fig.add_subplot(4,3,10)
#         ax7 = fig.add_subplot(2,3,5, sharex=ax3)
#         ax8 = fig.add_subplot(2,3,6, sharex=ax4, sharey=ax7)
#         self.compute_nz()
#         self.xsec.infoplot([ax1, ax2], *self.var['radial_selection_info'])
#         ax7.set(xlabel=r'z [$\mu$ m]', ylabel=r'$\kappa / \kappa_0$', ylim=klim)
#         axs = (ax1, ax2, ax5, ax6, ax3, ax4, ax7, ax8)
#         fig.tight_layout(pad=0.1, h_pad=0, w_pad=0)
#         if output: return (fig, axs)


############################################################################
############################ Hybrid_Double #################################

Default_Hybrid_Double = dict(VBinRange=25e3, VBinSize=160,trap_f=23.4,Vfit_min=0,Vfit_max=np.inf,minority_th=0.005,
                             majority_th=0.05, meff=1.25, A_polaron=-0.615, boxlength=95, Viriallimit=0.7,pressure_ref=1.0,
                             pressure_offset=0, imbalance_offset=0)

Default_Hybrid_Image = dict(ellipticity=1, xsec_extension='default',xsec_slice_width=4,
                                    xsec_fit_range=1.75, xsec_override=False, trap_f=23.4,
                                    radial_selection=0.7, trap_center_override=False, kind='unitary',
                                    Tfit_lim=0.2, Tfit_guess_kT=0.5, Tfit_guess_mu0=1)

class Hybrid_Double:
    def __init__(self, name1=None, name2=None, Hybrid_Settings={}, **kwargs ):
        # Initialize double Image files
        self.Hybrid_Image1 = Hybrid_Image(name=name1)
        self.Hybrid_Image2 = Hybrid_Image(name=name2)
        self.var = {**Default_Hybrid_Double, **kwargs}
        Hybrid_Settings_Final={**Default_Hybrid_Image, **Hybrid_Settings}

        self.Hybrid_Image1.set(**Hybrid_Settings_Final)
        settings2 = Hybrid_Settings.copy()
        settings2['xsec_override'] = self.Hybrid_Image1.xsec
        self.Hybrid_Image2.set(**settings2)
    @property
    def NS1(self): return self.Hybrid_Image1.N

    @property
    def fudge(self): return self.Hybrid_Settings_Final.get('fudge')

    @property
    def trap_f(self): return self.var.get('trap_f')

    @property
    def NS2(self): return self.Hybrid_Image2.N

    @property
    def N_tot_S1(self):
        return self.Hybrid_Image1.total_atoms

    @property
    def N_tot_S2(self):
        return self.Hybrid_Image2.total_atoms

    @property
    def nz_S1(self): return self.Hybrid_Image1.n/1e18

    @property
    def nz_S2(self): return self.Hybrid_Image2.n/1e18

    @property
    def z_S1(self): return self.Hybrid_Image1.z*1e6

    @property
    def z_S2(self): return self.Hybrid_Image2.z*1e6

    @property
    def V_S1(self): return thermodynamics.z2V(self.z_S1,self.trap_f)

    @property
    def V_S2(self): return thermodynamics.z2V(self.z_S2,self.trap_f)

    @property
    def VBinGrid(self): return np.linspace(0,self.var.get('VBinRange'),self.var.get('VBinSize'))

    @property
    def VBinRange(self): return self.var.get('VBinRange')

    @property
    def zBinRange(self): return thermodynamics.V2z(self.VBinRange,self.trap_f)

    @property
    def zBinGrid(self):
        return np.linspace(-self.zBinRange,self.zBinRange,self.var.get('VBinSize'))

    @property
    def VBin(self):
        if ('VBin' not in self.var.keys()):
            self.Bin_Profile()
        return self.var['VBin']

    @property
    def zBin(self):
        if ('zBin' not in self.var.keys()):
            self.Bin_Profile()
        return self.var['zBin']

    @property
    def nS1Binz(self):
        if ('nS1Binz' not in self.var.keys()):
            self.Bin_Profile()
        return self.var['nS1Binz']

    @property
    def nS2Binz(self):
        if ('nS2Binz' not in self.var.keys()):
            self.Bin_Profile()
        return self.var['nS2Binz']

    @property
    def nS1Bin(self):
        if ('nS1Bin' not in self.var.keys()):
            self.Bin_Profile()
        return self.var['nS1Bin']

    @property
    def nS2Bin(self):
        if ('nS2Bin' not in self.var.keys()):
            self.Bin_Profile()
        return self.var['nS2Bin']

    @property
    def zTF_S1(self):
        if ('zTF_S1' not in self.var.keys()):
            self.compute_TF()
        return self.var.get('z_TF_S1')

    @property
    def zTF_S2(self):
        if ('zTF_S2' not in self.var.keys()):
            self.compute_TF()
        return self.var.get('z_TF_S2')

    @property
    def VTF_S1(self): return thermodynamics.z2V(self.zTF_S1,self.trap_f)

    @property
    def VTF_S2(self): return thermodynamics.z2V(self.zTF_S2, self.trap_f)

    @property
    def muS1_rough(self):
        if ('IF_muS1_Trap_rough' not in self.var.keys()):
            self.IFfit_rough()
        return self.var.get('IF_muS1_Trap_rough')

    @property
    def T_rough(self):
        if ('IF_T_Trap_rough' not in self.var.keys()):
            self.IFfit_rough()
        return self.var.get('IF_T_trap_rough')

    @property
    def minority_th(self): return self.var.get('minority_th')

    @property
    def majority_th(self):
        return self.var.get('majority_th')

    @property
    def FitType(self):
        if ('FitType' not in self.var.keys()):
            self.TrapThermodynamic()
        return self.var.get('FitType')

    @property
    def minorityconcentration_V(self):
        x=self.nS2Bin/self.nS1Bin
        mask_S1=self.nS1Bin<0.03
        mask_S2=self.nS2Bin<0
        mask_signal=mask_S1 & mask_S2
        x[mask_signal]=np.nan
        return x

    @property
    def minorityconcentration_z(self):
        x = self.nS2Binz / self.nS1Binz
        mask_S1 = self.nS1Binz < 0.03
        mask_S2 = self.nS2Binz < 0
        mask_signal = mask_S1 & mask_S2
        x[mask_signal] = np.nan
        return x

    @property
    def WingThres(self):
        if 'WingThres' not in self.var.keys():
            self.TrapThermodynamic()
        return self.var.get('WingThres')
    @property
    def meff(self):
        return self.var.get('meff')

    @property
    def A_polaron(self):
        return self.var.get('A_polaron')

    @property
    def boxlength(self):
        return self.var.get('boxlength')

    @property
    def muS1_trap(self):
        if 'muS1_trap' not in self.var.keys():
            self.TrapThermodynamic()
        return self.var.get('muS1_trap')

    @property
    def muS1_trap_err(self):
        if 'muS1_trap_err' not in self.var.keys():
            self.TrapThermodynamic()
        return self.var.get('muS1_trap_err')

    @property
    def T_trap(self):
        if 'T_trap' not in self.var.keys():
            self.TrapThermodynamic()
        return self.var.get('T_trap')

    @property
    def T_trap_err(self):
        if 'T_trap_err' not in self.var.keys():
            self.TrapThermodynamic()
        return self.var.get('T_trap_err')

    @property
    def P_PolarizedWing(self):
        if self.FitType == 'PolarizedWing':
            if 'P_PolarizedWing' not in self.var.keys():
                self.TrapThermodynamic()
            return self.var.get('P_PolarizedWing')
        else:
            return None

    @property
    def P_Polaron_PolarizedWing(self):
        if self.FitType == 'PolarizedWing':
            if 'P_Polaron_PolarizedWing' not in self.var.keys():
                self.TrapThermodynamic()
            return self.var.get('P_Polaron_PolarizedWing')
        else:
            return None

    @property
    def P_VirialWing(self):
        if self.FitType == 'VirialWing':
            if 'P_VirialWing' not in self.var.keys():
                self.TrapThermodynamic()
            return self.var.get('P_VirialWing')
        else:
            return None


    @property
    def exp_EN(self):
        '''For Adiabatic expansion'''
        if 'exp_EN' not in self.var.keys():
            self.TrapThermodynamic()
        return self.var.get('exp_EN')

    @property
    def exp_nS1_insitu(self):
        '''For Adiabatic expansion'''
        if 'exp_nS1_insitu' not in self.var.keys():
            self.TrapThermodynamic()
        return self.var.get('exp_nS1_insitu')

    @property
    def exp_nS2_insitu(self):
        '''For Adiabatic expansion'''
        if 'exp_nS2_insitu' not in self.var.keys():
            self.TrapThermodynamic()
        return self.var.get('exp_nS2_insitu')

    @property
    def exp_P_tot(self):
        '''For Adiabatic expansion'''
        if 'exp_P_tot' not in self.var.keys():
            self.TrapThermodynamic()
        return self.var.get('exp_P_tot')

    @property
    def exp_EFS1_insitu(self):
        '''For Adiabatic expansion'''
        if 'exp_EFS1_insitu' not in self.var.keys():
            self.TrapThermodynamic()
        return self.var.get('exp_EFS1_insitu')

    @property
    def exp_EFS2_insitu(self):
        '''For Adiabatic expansion'''
        if 'exp_EFS2_insitu' not in self.var.keys():
            self.TrapThermodynamic()
        return self.var.get('exp_EFS2_insitu')

    @property
    def P_P0S1(self):
        '''For Adiabatic expansion, the total pressure of the original
        cloud divided by the zero temperature majority pressure'''
        if 'P_P0S1' not in self.var.keys():
            self.TrapThermodynamic()
        return self.var.get('P_P0S1')

    @property
    def Viriallimit(self):  return self.var.get('Viriallimit')

    @property
    def pressure_offset(self): return self.var.get('pressure_offset')

    @property
    def imbalance_offset(self): return self.var.get('imbalance_offset')

    @property
    def pressure_ref(self):
        if self.FitType == 'VirialWing':
            Vth = self.WingThres + self.pressure_offset
            mu_S1_th = self.muS1_trap - Vth
            mu_S2_th = self.var['muS2_virial'] - Vth
            P = Virial.P_Virial_imb_mu(mu_S1_th, mu_S2_th, self.T_trap)
            nS1_ref,nS2_ref=thermodynamics.ImbalancedVirialnV([mu_S1_th,mu_S2_th,self.T_trap],0)
            P_ref_out = dict(V_ref = Vth, P_ref =  P, nS1_ref = nS1_ref, nS2_ref = nS2_ref)

            return P_ref_out
        elif self.FitType == 'PolarizedWing':
            Vth = self.WingThres + self.pressure_offset
            mu_S1_th = self.muS1_trap - Vth
            P = thermodynamics.P_Ideal_mu(mu_S1_th, self.T_trap)
            nS1_ref=thermodynamics.IdealGasnV([mu_S1_th,self.T_trap],0)

            P_ref_out = dict(V_ref = Vth, P_ref = P,nS1_ref = nS1_ref, nS2_ref = 0*nS1_ref)
            return P_ref_out
    @property
    def PBin(self):
        if 'PBin' not in self.var.keys():
            self.compute_P()
        return self.var.get('PBin')

    def  P_V(self,V=0):
        P_intp = interp1d(x=self.VBin,y=self.PBin,fill_value='extrapolate')
        return P_intp(V)

    def nS1_V(self,V=0):
        nS1_intp = interp1d(x=self.VBin,y=self.nS1Bin,fill_value='extrapolate')
        return nS1_intp(V)

    def nS2_V(self, V=0):
        nS2_intp = interp1d(x=self.VBin, y=self.nS2Bin, fill_value='extrapolate')
        return nS2_intp(V)

    def PTilde_V(self,V=0):
        return self.P_V(V=V)/(2/5*self.nS1_V(V=V)*thermodynamics.n2EF(self.nS1_V(V=V)))

    def TTilde_V(self,V=0):
        return self.T_trap/thermodynamics.n2EF(self.nS1_V(V=V))

    def compute_TF(self):
        '''Calculate the Thomas Fermi radius and potential of the cloud'''

        # fit the minority
        R0_S2=max(np.concatenate((self.z_S2[self.nz_S2>0.01],np.array([50]))))
        P_TF_S2=thermodynamics.TFfit(self.z_S2, self.nz_S2, R0_S2)
        z_TF_S2=P_TF_S2[0][2]

        # fit the majority
        R0_S1=max(np.concatenate((self.z_S2[self.nz_S1>0.02],np.array([100]))))
        P_TF_S1 = thermodynamics.TFfit(self.z_S1, self.nz_S1, R0_S1)
        z_TF_S1 = P_TF_S1[0][2]

        V_TF_S1=thermodynamics.z2V(z_TF_S1,self.trap_f)
        V_TF_S2 = thermodynamics.z2V(z_TF_S2, self.trap_f)

        self.var['P_TF_S1'] = P_TF_S1
        self.var['P_TF_S2'] = P_TF_S2
        self.var['z_TF_S1'] = z_TF_S1
        self.var['z_TF_S2'] = z_TF_S2
        self.var['V_TF_S1'] = V_TF_S1
        self.var['V_TF_S2'] = V_TF_S2


    def plot_crop(self):
        self.Hybrid_Image1.plot_crop()
        self.Hybrid_Image2.plot_crop()

    def plot_profile(self):
        f = plt.figure(figsize=[12,4])

        f.suptitle('Raw density profile')

        ax1 = plt.subplot(1, 2, 1)
        ax1.plot(self.z_S1,self.nz_S1,'o',markersize=2)
        ax1.plot(self.z_S2,self.nz_S2,'o',markersize=2)
        plt.axvline(self.zTF_S2, linewidth=2, color='k', linestyle='--')
        plt.axvline(-self.zTF_S2, linewidth=2, color='k', linestyle='--')
        plt.xlim([-self.zTF_S1 * 2, self.zTF_S1 * 2])
        plt.xlabel('z [um]')
        plt.ylabel(r'n [$\mathrm{um}^{-3}$]')

        ax2 = plt.subplot(1, 2, 2,sharey=ax1)
        ax2.plot(self.V_S1,self.nz_S1,'o',markersize=2)
        ax2.plot(self.V_S2,self.nz_S2,'o',markersize=2)
        plt.axvline(self.VTF_S2, linewidth=2, color='k', linestyle='--')
        plt.xlabel('U [Hz]')
        plt.ylabel(r'n [$\mathrm{um}^{-3}$]')
        plt.xlim([0, self.VTF_S1 * 2])

        plt.tight_layout()
        plt.subplots_adjust(top=0.85)
        plt.show()
        return f

    def Bin_Profile(self):
        '''Bin the profile'''
        BinS1_z = numerical.BinGrid(self.z_S1,self.nz_S1,self.zBinGrid,0)
        BinS2_z = numerical.BinGrid(self.z_S2, self.nz_S2, self.zBinGrid, 0)

        nS2_z_int=interp1d(BinS2_z['xmean'],BinS2_z['ymean'],bounds_error=False)
        nS2_z_err_int = interp1d(BinS2_z['xmean'], BinS2_z['ystd'], bounds_error=False)

        nS2_zBinzS1=nS2_z_int(BinS1_z['xmean'])
        nS2_z_err_BinzS1 = nS2_z_err_int(BinS1_z['xmean'])

        output=numerical.clean_nan([BinS1_z['xmean'],BinS1_z['xstd'],BinS1_z['ymean'],BinS1_z['ystd'],nS2_zBinzS1,nS2_z_err_BinzS1])

        self.var['zBin'] = output[0]
        self.var['zBin_err'] = output[1]
        self.var['zBinzS1'] = BinS1_z['xmean']
        self.var['zBinzS2'] = BinS2_z['xmean']
        self.var['nS1BinzS1'] = BinS1_z['ymean']
        self.var['nS1BinzS1_err'] = BinS1_z['ystd']
        self.var['nS2BinzS2'] = BinS2_z['ymean']
        self.var['nS2BinzS2_err'] = BinS2_z['ystd']
        self.var['nS1Binz'] = output[2]
        self.var['nS1Binz_err'] = output[3]
        self.var['nS2Binz'] = output[4]
        self.var['nS2_Binz_err'] = output[5]

        BinS1 = numerical.BinGrid(self.V_S1, self.nz_S1, self.VBinGrid, 0)
        BinS2 = numerical.BinGrid(self.V_S2, self.nz_S2, self.VBinGrid, 0)

        # interpolate S2 profile on the Binned S1 grid:
        nS2_int=interp1d(BinS2['xmean'],BinS2['ymean'],bounds_error=False)
        nS2_VBinVS1=nS2_int(BinS1['xmean'])
        nS2_err_int=interp1d(BinS2['xmean'],BinS2['ystd'],bounds_error=False)
        nS2_err_VBinVS1=nS2_err_int(BinS1['xmean'])

        output = numerical.clean_nan(
            [BinS1['xmean'], BinS1['xstd'], BinS1['ymean'], BinS1['ystd'],nS2_VBinVS1,nS2_err_VBinVS1])

        self.var['VBin'] = output[0]
        self.var['VBin_err'] = output[1]
        self.var['VBinVS1'] = BinS1['xmean']
        self.var['VBinVS2'] = BinS2['xmean']
        self.var['nS1BinVS1'] = BinS1['ymean']
        self.var['nS1BinVS1_err'] = BinS1['ystd']
        self.var['nS2BinVS2'] = BinS2['ymean']
        self.var['nS2BinVS2_err'] = BinS2['ystd']
        self.var['nS1Bin'] = output[2]
        self.var['nS1Bin_err'] = output[3]
        self.var['nS2Bin'] = output[4]
        self.var['nS2_Bin_err']= output[5]


    def plot_profile_Bin(self):
        '''plot the profile binned'''
        f = plt.figure(figsize=[12,4])
        ax1 = plt.subplot(1, 2, 1)
        ax1.plot(self.zBin, self.nS1Binz, 'o', markersize=2)
        ax1.plot(self.zBin, self.nS2Binz, 'o', markersize=2)
        plt.axvline(self.zTF_S2, linewidth=2, color='k', linestyle='--')
        plt.axvline(-self.zTF_S2, linewidth=2, color='k', linestyle='--')
        plt.xlim([-self.zTF_S1*2,self.zTF_S1*2])
        plt.xlabel('z [um]')
        plt.ylabel(r'n [$\mathrm{um}^{-3}$]')

        ax2 = plt.subplot(1, 2, 2,sharey=ax1)
        ax2.plot(self.VBin, self.nS1Bin, 'o', markersize=2)
        ax2.plot(self.VBin, self.nS2Bin, 'o', markersize=2)
        plt.axvline(-self.VTF_S2, linewidth=2, color='k', linestyle='--')
        plt.xlabel('U [Hz]')
        plt.ylabel(r'n [$\mathrm{um}^{-3}$]')
        plt.xlim([0, self.VTF_S1 * 2])

        f.suptitle('Binned density profile')

        plt.tight_layout()
        plt.subplots_adjust(top=0.85)
        plt.show()
        return f

    def IFfit_rough(self):
        ''' fit the majority wing outside the minority thomas Fermi radius with the ideal fermi gas eos, to get a rough
        estimate on temperature and majority chemcial potantial'''

        Vth1=self.VTF_S2
        if max(self.nS1Bin) > 0.03:
            Vth2 = max(self.VBin[self.nS1Bin>0.03])
            Vth = min(Vth1,Vth2)
        else:
            Vth = Vth1

        Vfit = self.VBin[self.VBin > Vth]
        nfit = self.nS1Bin[self.VBin > Vth]

        P_rough, Pjac_rough = thermodynamics.IdealGasFit(Vfit, nfit, [2000, 500])
        mu_trap = P_rough[0]
        mu_trap_err = (np.sqrt(Pjac_rough[0][0]))
        T_trap = P_rough[1]
        T_trap_err = (np.sqrt(Pjac_rough[1][1]))

        self.var['IF_P_rough']=P_rough
        self.var['IF_Pjac_rough']=Pjac_rough
        self.var['IF_muS1_Trap_rough'] = mu_trap
        self.var['IF_T_trap_rough'] = T_trap
        self.var['IF_muS1_err_trap_rough'] = mu_trap_err
        self.var['IF_T_err_trap_rough'] = T_trap_err
        return

    def plot_profile_roughfit(self):
        '''plot the profile with the rough ideal Fermi gas fit from VTF_S2'''

        zplot=self.zBin
        Vplot=self.VBin

        nzplot = thermodynamics.IdealGasnV([self.muS1_rough, self.T_rough], thermodynamics.z2V(zplot,self.trap_f))
        nVplot = thermodynamics.IdealGasnV([self.muS1_rough, self.T_rough], Vplot)

        f = plt.figure(figsize=[12,4])
        ax1 = plt.subplot(1, 2, 1)
        ax1.plot(self.zBin, self.nS1Binz, 'o', markersize=2)
        ax1.plot(self.zBin, self.nS2Binz, 'o', markersize=2)

        p1,=ax1.plot(zplot, nzplot,'-',linewidth=2,label='Rough Ideal EoS fit')
        p2, = ax1.plot(zplot, nzplot + 0.615 * self.nS2Binz, '-', linewidth=2, label='FL Pressure Ansatz')

        plt.axvline(self.zTF_S2, linewidth=2, color='k', linestyle='--')
        plt.axvline(-self.zTF_S2, linewidth=2, color='k', linestyle='--')
        plt.legend(handles=[p1,p2])
        plt.xlim([-self.zTF_S1*2,self.zTF_S1*2])
        plt.xlabel('z [um]')
        plt.ylabel(r'n [$\mathrm{um}^{-3}$]')

        ax2 = plt.subplot(1, 2, 2,sharey=ax1)
        ax2.plot(self.VBin, self.nS1Bin, 'o', markersize=2)
        ax2.plot(self.VBin, self.nS2Bin, 'o', markersize=2)
        p3, = ax2.plot(Vplot, nVplot, '-', linewidth=2, label='Rough Ideal EoS fit')
        p4, = ax2.plot(Vplot, nVplot+0.615*self.nS2Bin, '-', linewidth=2, label='FL Pressure Ansatz')

        plt.axvline(-self.VTF_S2, linewidth=2, color='k', linestyle='--')
        plt.legend(handles=[p3,p4])
        plt.xlabel('U [Hz]')
        plt.ylabel(r'n [$\mathrm{um}^{-3}$]')
        plt.xlim([0, self.VTF_S1 * 2])

        f.suptitle('Density profile with Ideal EoS Fit')
        plt.tight_layout()
        plt.subplots_adjust(top=0.85)
        plt.show()
        return f

    def TrapThermodynamic(self):
        '''Calculate the thermodynamic infomation of the hybrid trap'''
        V_Virial_th = np.max([self.muS1_rough+self.Viriallimit*self.T_rough, 0])
        nS2_flag = np.max(self.nS2Bin[self.VBin > V_Virial_th])
        nS1_flag = np.max(self.nS1Bin[self.VBin > V_Virial_th])
        if (nS2_flag>self.minority_th) & (nS1_flag>self.majority_th):
            self.var['FitType']='VirialWing'
            self.var['WingThres']=V_Virial_th
            self.TrapThermodynamic_VirialWing()
        else:
            self.var['FitType']='PolarizedWing'
            x=self.minorityconcentration_V
            V_sel=self.VBin[x<0.02]
            if len(V_sel)>0:
                self.var['WingThres']=np.nanmin(V_sel)
            else:
                self.var['WingThres'] = self.VTF_S2*1.25
            self.TrapThermodynamic_PolarizedWing()



    def TrapThermodynamic_PolarizedWing(self):
        '''Calculate the thermodynamic by fitting a fully polarized EoS to the wing of the cloud'''

        # first fit the wing with ideal Fermi gas EoS
        Vfit = self.VBin.copy() [self.VBin > self.WingThres]
        nfit = self.nS1Bin.copy() [self.VBin > self.WingThres]

        P, Pjac = thermodynamics.IdealGasFit(Vfit, nfit, [2000, 500])
        muS1_trap = P[0]
        mu_trap_err = (np.sqrt(Pjac[0][0]))
        T_trap = P[1]
        T_trap_err = (np.sqrt(Pjac[1][1]))


        self.var['muS1_trap'] = muS1_trap
        self.var['muS1_trap_err']=mu_trap_err
        self.var['T_trap'] = T_trap
        self.var['T_trap_err'] = T_trap_err
        self.var['P_PolarizedWing']=P
        self.var['Pjac_PolarizedWing']=Pjac

        #then fit the minority with polaron EoS
        P_polaron, P_polaron_jac = thermodynamics.PolaronFit(self.VBin, self.nS2Bin , [2000, 400],meff=self.meff, A=self.A_polaron)
        self.var['P_Polaron_PolarizedWing'] = P_polaron
        self.var['Pjac_Polaron_PolarizedWing'] = P_polaron_jac

        #compute the energy per particle of the cloud
        nS2_fitted = thermodynamics.PolaronGasnV(P_polaron, thermodynamics.z2V(self.zBin,self.trap_f) ,meff=self.meff, A=self.A_polaron)
        nS1_fitted = thermodynamics.IdealGasnV(P, thermodynamics.z2V(self.zBin,self.trap_f))

        nS2_int = nS2_fitted.copy()
        nS1_int = self.nS1Binz.copy()
        nS1_int[thermodynamics.z2V(self.zBin,self.trap_f)>self.WingThres]=nS1_fitted[thermodynamics.z2V(self.zBin,self.trap_f)>self.WingThres]
        z_int = self.zBin
        V_int = thermodynamics.z2V(z_int,self.trap_f)

        # Calculate Energy per particle
        EN = (4 * np.trapz(nS1_int * V_int, z_int) + 4 * np.trapz(nS2_int * V_int, z_int)) / (np.trapz(nS1_int, z_int) + np.trapz(nS2_int, z_int))
        nS1_insitu = np.trapz(nS1_int, z_int) / self.boxlength
        nS2_insitu = np.trapz(nS2_int, z_int) / self.boxlength

        P_tot = 2 / 3 * EN * (nS1_insitu+nS2_insitu)

        EFS1_insitu = thermodynamics.n2EF(nS1_insitu)
        EFS2_insitu = thermodynamics.n2EF(nS2_insitu)
        # P normalized by majority zero temperature pressure
        P_P0S1 = P_tot/(2/5*nS1_insitu*EFS1_insitu)

        self.var['exp_EN'] = EN
        self.var['exp_nS1_insitu'] = nS1_insitu
        self.var['exp_nS2_insitu'] = nS2_insitu
        self.var['exp_P_tot'] = P_tot
        self.var['exp_EFS1_insitu'] = EFS1_insitu
        self.var['exp_EFS2_insitu'] = EFS2_insitu
        self.var['P_P0S1'] = P_P0S1



    def TrapThermodynamic_VirialWing(self):
        '''Calculate the thermodynamic by fitting a Virial EoS to the wing of the cloud'''
        # first fit the virial
        Vth=self.WingThres
        mask_fit=self.VBin>Vth

        nS1_fit = self.nS1Bin.copy()[mask_fit]
        nS2_fit = self.nS2Bin.copy()[mask_fit]
        V_fit = self.VBin.copy()[mask_fit]

        mu_down_0=self.T_rough*np.log(abs(max(nS2_fit)/max(nS1_fit)))+self.muS1_rough

        P_virial, Pjac_virial = thermodynamics.ImbalancedVirialFit(V_fit, nS1_fit, nS2_fit, [self.muS1_rough, mu_down_0, self.T_rough])
        muS1_trap = P_virial[0]
        muS1_trap_err = (np.sqrt(Pjac_virial[0][0]))
        T_trap = P_virial[2]
        T_trap_err = (np.sqrt(Pjac_virial[2][2]))
        muS2_trap=P_virial[1]
        muS2_trap_err = (np.sqrt(Pjac_virial[1][1]))

        self.var['muS1_trap'] = muS1_trap
        self.var['muS1_trap_err'] = muS1_trap_err
        self.var['T_trap'] = T_trap
        self.var['T_trap_err'] = T_trap_err
        self.var['P_VirialWing'] = P_virial
        self.var['Pjac_VirialWing'] = Pjac_virial
        self.var['muS2_virial'] = muS2_trap

        # compute the energy per particle of the cloud
        z_int = self.zBin
        V_int = thermodynamics.z2V(z_int, self.trap_f)
        nS1_fitted, nS2_fitted = thermodynamics.ImbalancedVirialnV(P_virial, V_int)
        nS2_int = self.nS2Binz.copy()
        nS1_int = self.nS1Binz.copy()
        mask=V_int>Vth
        nS2_int[mask] = nS2_fitted[mask]
        nS1_int[mask] = nS1_fitted[mask]

        # Calculate Energy per particle
        EN = (4 * np.trapz(nS1_int * V_int, z_int) + 4 * np.trapz(nS2_int * V_int, z_int)) / (
        np.trapz(nS1_int, z_int) + np.trapz(nS2_int, z_int))
        nS1_insitu = np.trapz(nS1_int, z_int) / self.boxlength
        nS2_insitu = np.trapz(nS2_int, z_int) / self.boxlength

        P_tot = 2 / 3 * EN * (nS1_insitu + nS2_insitu)

        EFS1_insitu = thermodynamics.n2EF(nS1_insitu)
        EFS2_insitu = thermodynamics.n2EF(nS2_insitu)
        # P normalized by majority zero temperature pressure
        P_P0S1 = P_tot / (2 / 5 * nS1_insitu * EFS1_insitu)

        self.var['exp_EN'] = EN
        self.var['exp_nS1_insitu'] = nS1_insitu
        self.var['exp_nS2_insitu'] = nS2_insitu
        self.var['exp_P_tot'] = P_tot
        self.var['exp_EFS1_insitu'] = EFS1_insitu
        self.var['exp_EFS2_insitu'] = EFS2_insitu
        self.var['P_P0S1'] = P_P0S1


    def expansion_info(self):
        if self.FitType == 'PolarizedWing':
            self.plot_wingfit_polarizedwing()
        elif self.FitType == 'VirialWing':
            self.plot_wingfit_Virialwing()
        return 0

    def plot_profile_fit(self):
        if self.FitType == 'PolarizedWing':
            return self.plot_wingfit_polarizedwing()
        elif self.FitType == 'VirialWing':
            return self.plot_wingfit_Virialwing()
        return 0


    def plot_wingfit_polarizedwing(self):
        if self.FitType=='PolarizedWing':

            P_PolarizedWing=self.P_PolarizedWing
            P_Polaron_PolarizedWing=self.P_Polaron_PolarizedWing

            z_plot=np.linspace(-self.zTF_S1 * 2, self.zTF_S1 * 2,300)
            V_plot=thermodynamics.z2V(z_plot,self.trap_f)

            nS1_fitted_z=thermodynamics.IdealGasnV(P_PolarizedWing, V_plot)
            nS2_fitted_z=thermodynamics.PolaronGasnV(P_Polaron_PolarizedWing, V_plot,meff=self.meff,A=self.A_polaron)

            f = plt.figure(figsize=[12,4])
            ax1 = plt.subplot(1, 2, 1)
            ax1.plot(self.zBin, self.nS1Binz, 'o', markersize=2)
            ax1.plot(self.zBin, self.nS2Binz, 'o', markersize=2)
            plt.axvline(thermodynamics.V2z(self.WingThres,self.trap_f), linewidth=2, color='k', linestyle='--')
            plt.axvline(-thermodynamics.V2z(self.WingThres,self.trap_f), linewidth=2, color='k', linestyle='--')

            p1, = ax1.plot(z_plot, nS1_fitted_z, '-', linewidth=2, label='Ideal EoS fit from wing')
            p2, = ax1.plot(z_plot, nS1_fitted_z - self.A_polaron * nS2_fitted_z, '-', linewidth=2, label='FL Pressure Ansatz')
            p3, = ax1.plot(z_plot, nS2_fitted_z, '-', linewidth=2, label='FL Polaron')

            plt.legend(handles=[p1, p2, p3])
            plt.xlim([-self.zTF_S1 * 2, self.zTF_S1 * 2])
            plt.ylim([-0.03,np.nanmax(self.nS1Binz)*1.5])
            plt.xlabel('z [um]')
            plt.ylabel(r'n [$\mathrm{um}^{-3}$]')

            ax2 = plt.subplot(1, 2, 2, sharey=ax1)
            ax2.plot(self.VBin, self.nS1Bin, 'o', markersize=2)
            ax2.plot(self.VBin, self.nS2Bin, 'o', markersize=2)
            plt.axvline(self.WingThres, linewidth=2, color='k', linestyle='--')
            p4, = ax2.plot(V_plot, nS1_fitted_z, '-', linewidth=2, label='Ideal EoS fit from wing')
            p5, = ax2.plot(V_plot, nS1_fitted_z - self.A_polaron * nS2_fitted_z, '-', linewidth=2,
                           label='FL Pressure Ansatz')
            p6, = ax2.plot(V_plot, nS2_fitted_z, '-', linewidth=2, label='FL Polaron')
            plt.xlabel('U [Hz]')
            plt.ylabel(r'n [$\mathrm{um}^{-3}$]')
            plt.xlim([0, self.VTF_S1 * 2])
            plt.ylim([-0.03, np.nanmax(self.nS1Bin) * 1.5])
            plt.legend(handles=[p4, p5, p6])
            f.suptitle('Binned density profile')

            plt.tight_layout()
            plt.subplots_adjust(top=0.85)
            plt.show()


            return f
        else:
            return None

    def plot_wingfit_Virialwing(self):
        if self.FitType=='VirialWing':

            P_Virial=self.P_VirialWing

            z_plot = np.linspace(-self.zTF_S1 * 2, self.zTF_S1 * 2, 300)
            V_plot = thermodynamics.z2V(z_plot, self.trap_f)

            mask=V_plot>self.WingThres

            V_fit=V_plot[mask]

            nS1_fitted_z, nS2_fitted_z = thermodynamics.ImbalancedVirialnV(P_Virial, V_fit)

            nS1_plot = z_plot * 0
            nS2_plot = z_plot * 0

            nS1_plot[mask]=nS1_fitted_z
            nS2_plot[mask]=nS2_fitted_z

            nS1_plot[~mask] = np.nan
            nS2_plot[~mask] = np.nan


            f = plt.figure(figsize=[12, 4])
            ax1 = plt.subplot(1, 2, 1)
            ax1.plot(self.zBin, self.nS1Binz, 'o', markersize=2)
            ax1.plot(self.zBin, self.nS2Binz, 'o', markersize=2)
            plt.axvline(thermodynamics.V2z(self.WingThres,self.trap_f), linewidth=2, color='k', linestyle='--')
            plt.axvline(-thermodynamics.V2z(self.WingThres,self.trap_f), linewidth=2, color='k', linestyle='--')

            p1, = ax1.plot(z_plot, nS1_plot, '-', linewidth=2, label='Virial Majority')
            p3, = ax1.plot(z_plot, nS2_plot, '-', linewidth=2, label='Virial Minority')

            plt.legend(handles=[p1, p3])
            plt.xlim([-self.zTF_S1 * 2, self.zTF_S1 * 2])
            plt.ylim([-0.03, np.nanmax(self.nS1Binz) * 1.5])
            plt.xlabel('z [um]')
            plt.ylabel(r'n [$\mathrm{um}^{-3}$]')

            ax2 = plt.subplot(1, 2, 2, sharey=ax1)
            ax2.plot(self.VBin, self.nS1Bin, 'o', markersize=2)
            ax2.plot(self.VBin, self.nS2Bin, 'o', markersize=2)
            plt.axvline(self.WingThres, linewidth=2, color='k', linestyle='--')
            p4, = ax2.plot(V_plot, nS1_plot, '-', linewidth=2, label='Virial Majority')
            p6, = ax2.plot(V_plot, nS2_plot, '-', linewidth=2, label='Virial Minority')
            plt.xlabel('U [Hz]')
            plt.ylabel(r'n [$\mathrm{um}^{-3}$]')
            plt.xlim([0, self.VTF_S1 * 2])
            plt.ylim([-0.03, np.nanmax(self.nS1Bin) * 1.5])
            plt.legend(handles=[p4, p6])
            f.suptitle('Binned density profile')

            plt.tight_layout()
            plt.subplots_adjust(top=0.85)
            plt.show()

            return f

        else:
            return None

    def find_imbalance(self,x):

        # find the trapping potential at centain minority concentration x

        x_mc=self.nS2Bin/self.nS1Bin

        mask1=self.nS1Bin>self.majority_th
        mask2=self.nS2Bin>self.minority_th
        masktemp=mask1 & mask2

        Vth=min(self.VBin[~masktemp])+self.imbalance_offset
        mask=self.VBin<Vth

        x_mc_fit=x_mc[mask]
        V_fit=self.VBin[mask]

        x_int=interp1d(x_mc_fit,V_fit,fill_value=np.nan,bounds_error=False)

        if (x != np.nan) & (x <= 1) & (x >= 0):
            return x_int(x)
        else:
            return np.nan


    def plot_imbalance(self,x_cursor=np.nan):
        # plot the minority concentration vs trapping potential V and trap position z
        # cursor: put a cursor on the figure
        # minority cocentration vs V

        x_mc_V = self.nS2Bin / self.nS1Bin
        mask1 = self.nS1Bin > self.majority_th
        mask2 = self.nS2Bin > self.minority_th
        masktemp = mask1 & mask2
        Vth = min(self.VBin[~masktemp])+self.imbalance_offset
        mask = self.VBin < Vth
        x_mc_V[~mask] = np.nan

        x_mc_z=self.nS2Binz/self.nS1Binz
        mask1 = self.nS1Binz > self.majority_th
        mask2 = self.nS2Binz > self.minority_th
        masktemp = mask1 & mask2
        Vth=min(thermodynamics.z2V(self.zBin,self.trap_f)[~masktemp])+self.imbalance_offset
        mask = thermodynamics.z2V(self.zBin,self.trap_f) < Vth
        x_mc_z[~mask]=np.nan

        V_cursor=self.find_imbalance(x=x_cursor)
        z_cursor=thermodynamics.V2z(V_cursor,self.trap_f)

        f = plt.figure(figsize=[12, 4])
        ax1 = plt.subplot(1, 2, 1)
        ax1.plot(self.zBin, x_mc_z, 'o', markersize=2)
        if V_cursor != np.nan:
            p1=plt.axvline(z_cursor, linewidth=1, color='k', linestyle='--',label='x={:.2f}'.format(x_cursor))
            plt.axvline(-z_cursor, linewidth=1, color='k', linestyle='--')
            plt.axhline(x_cursor, linewidth=1, color='k', linestyle='--')
            plt.legend(handles=[p1])

        plt.xlim([-self.zTF_S1 * 2, self.zTF_S1 * 2])
        plt.ylim([-0.02, np.nanmax(x_mc_V) * 1.5])
        plt.xlabel('z [um]')
        plt.ylabel(r'n [$\mathrm{um}^{-3}$]')

        ax2 = plt.subplot(1, 2, 2, sharey=ax1)
        ax2.plot(self.VBin, x_mc_V, 'o', markersize=2)
        if (V_cursor != np.nan) :
            p2=plt.axvline(V_cursor, linewidth=1, color='k', linestyle='--',label='x={:.2f}'.format(x_cursor))
            plt.axhline(x_cursor, linewidth=1, color='k', linestyle='--')
            plt.legend(handles=[p2])

        plt.xlabel('U [Hz]')
        plt.ylabel(r'n [$\mathrm{um}^{-3}$]')
        plt.xlim([0, self.VTF_S1 * 2])
        plt.ylim([-0.02, np.nanmax(x_mc_V) * 1.5])

        f.suptitle('Minority concentration')
        plt.tight_layout()
        plt.subplots_adjust(top=0.85)
        plt.show()
        return f

    def compute_P(self):
        P_ref=self.pressure_ref
        V0=P_ref.get('V_ref')
        P0=P_ref.get('P_ref')
        n0=(P_ref.get('nS1_ref')+P_ref.get('nS2_ref'))
        PBin=self.VBin*0
        for i in range(0,len(self.VBin)):
            if self.VBin[i]<V0:
                mask1=self.VBin<V0
                mask2=self.VBin>=self.VBin[i]
                mask=mask1 & mask2
                V_int=np.concatenate([self.VBin[mask],np.array([V0])])
                # n_int=self.nS1Bin[mask]+self.nS2Bin[mask]
                n_int = np.concatenate([self.nS1Bin[mask] + self.nS2Bin[mask],np.array([n0])])
                delta_P=np.trapz(y=n_int,x=V_int)
            else:
                mask1 = self.VBin > V0
                mask2 = self.VBin <= self.VBin[i]
                mask = mask1 & mask2
                V_int = np.concatenate([np.array([V0]),self.VBin[mask]])
                n_int = np.concatenate([np.array([n0]),self.nS1Bin[mask] + self.nS2Bin[mask]])
                delta_P = -np.trapz(y=n_int, x=V_int)
            PBin[i]=P0+delta_P
        self.var['PBin']=PBin


    def P_plot(self):
        plt.plot(self.VBin,self.PBin, 'o', markersize=2)
        plt.xlim([0, self.VTF_S1 * 2])
        plt.axvline(self.pressure_ref['V_ref'],linestyle='--',color='k')
        plt.xlabel('V [Hz]')
        plt.ylabel(r'P [Hz $\times$ $\mathrm{\mu m}^{-3}$]')
        plt.show()
####################################################################################
############################ Momentum Distribution #################################
cst_MD_Class = constants.cst()


class Momentum_Distribution(Image):
    def __init__(self, name=None, path=None, od=None, **kwargs):
        # Initialize the complete Image Object
        super(Momentum_Distribution, self).__init__(name=name, path=path, od=od, **kwargs)

        # Addons
        self.var = {**self.var, **Default_Hybrid_Image, **kwargs}
        self.LevelAdder = len(self.var['Level_Selector'])
        self.var['Level_Selector'] = self.var['Level_Selector'] + list(Level_Selector_Hybrid_Image)
        self.var['recalc'] = self.var['recalc'] + [True] * len(Level_Selector_Hybrid_Image)

    @property
    def Nz_raw(self, ): return np.sum(self.app,1)

    @property
    def z_pc(self, ): return np.arange(0,len(self.Nz_raw))

    @property
    def z_um_raw(self, ): return self.z_pc*self.pixel_binned*1e6

    @property
    def z_pc_min(self): return (self.var.get('zmin')-(self.center_y-self.height/2))/self.subsample

    @property
    def z_pc_max(self): return (self.var.get('zmax')-(self.center_y-self.height/2))/self.subsample

    @property
    def Nz(self):
        if 'Nz' not in self.var.keys():
            self.var['Nz']=numerical.TailTailor(self.z_pc,self.Nz_raw,self.z_pc_min,self.z_pc_max)
        return self.var.get('Nz')

    @property
    def N_tot(self): return np.sum(self.Nz)

    @property
    def n1dz(self): return self.Nz/(self.pixel_binned*1e6)

    @property
    def z0(self):
        if 'z0' not in self.var.keys():
            self.Fit1dProfile()
        return self.var.get('z0')

    @property
    def z(self):
        if 'z' not in self.var.keys():
            self.Fit1dProfile()
        return self.var.get('z')

    @property
    def P_1D(self):
        if 'P_1D' not in self.var.keys():
            self.Fit1dProfile()
        return self.var.get('P_1D')

    @property
    def P_1D_jac(self):
        if 'P_1D_jac' not in self.var.keys():
            self.Fit1dProfile()
        return self.var.get('P_1D_jac')
    @property
    def kz_mu(self): return np.sqrt(self.P_1D[2])*1e-6*cst_MD_Class.mass*(2*np.pi*self.trap_f)/cst_MD_Class.hbar*1e-6

    @property
    def trap_f(self):
        if 'trap_f' not in self.var.keys():
            self.var['trap_f']=23.9
        return self.var.get('trap_f')
    @property

    def Volume(self):
        # box volume in unit of um^3
        if 'Volume' not in self.var.keys():
            self.var['Volume']=1.2e6
        return self.var.get('Volume')

    @property
    def n1dk(self):
        # 1D momentum distribution in unit of um^{-2}
        return (self.n1dz*1e6/(self.Volume*1e-18))*cst_MD_Class.hbar/(cst_MD_Class.mass*(2*np.pi*self.trap_f))*1e-12

    @property
    def kz(self):
        # momentum in unit of um^{-1}
        cst_MD_Class.LiD2
        return self.z*1e-6*cst_MD_Class.mass*(2*np.pi*self.trap_f)/cst_MD_Class.hbar*1e-6

    @property
    def Ngrid(self):
        if 'Ngrid' not in self.var.keys():
            self.var['Ngrid']=200
        return self.var.get('Ngrid')
    @property
    def n1dkBin(self):
        xdata=self.kz **2
        ydata=self.n1dk
        Ngrid=self.Ngrid
        Xgrid=np.linspace(0,np.max(xdata),Ngrid+1)
        return numerical.BinGrid(xdata,ydata,Xgrid,0)
    @property
    def SD(self):
        if 'SD' not in self.var:
            self.var['SD']=4
        return self.var.get('SD')


    @property
    def fk(self):
        if 'fk' not in self.var:
            mask = ~np.isnan(self.n1dkBin['ymean'])
            fk, fkerr = numerical.FiniteD(self.n1dkBin['xmean'][mask], -8 * np.pi ** 2 * self.n1dkBin['ymean'][mask], self.SD,
                                          self.n1dkBin['xstd'][mask],
                                          8 * np.pi ** 2 * self.n1dkBin['ystd'][mask])
            self.var['fk'] = fk
            self.var['fk_err'] = fkerr
        return self.var.get('fk')

    @property
    def fk_err(self):
        if 'fk_err' not in self.var:
            mask = ~np.isnan(self.n1dkBin['ymean'])
            fk, fkerr = numerical.FiniteD(self.n1dkBin['xmean'][mask], -8 * np.pi ** 2 * self.n1dkBin['ymean'][mask], self.SD,
                                          self.n1dkBin['xstd'][mask],
                                          8 * np.pi ** 2 * self.n1dkBin['ystd'][mask])
            self.var['fk'] = fk
            self.var['fk_err'] = fkerr
        return self.var.get('fk_err')
    @property
    def kzBin(self):
        xdata=self.n1dkBin['xmean']
        mask = ~np.isnan(self.n1dkBin['ymean'])
        return np.sqrt(xdata[mask])

    @property
    def mu(self): return self.var.get('P_FD')[1]*1e12*(cst_MD_Class.hbar**2/(2*cst_MD_Class.mass))/cst_MD_Class.h
    @property
    def mu_err(self): return np.sqrt(self.var.get('P_FD_jac')[1][1])*1e12*(cst_MD_Class.hbar**2/(2*cst_MD_Class.mass))/cst_MD_Class.h

    @property
    def T(self): return self.mu/self.var.get('P_FD')[0]

    @property
    def T_err(self):
        Rel_err_mu=np.sqrt(self.var.get('P_FD_jac')[1][1])/self.var.get('P_FD')[1]
        Rel_err_betamu = np.sqrt(self.var.get('P_FD_jac')[0][0]) / self.var.get('P_FD')[0]
        Rel_err_T= np.sqrt(Rel_err_mu**2+Rel_err_betamu**2)
        return Rel_err_T*self.T



    @property
    def EF_fit(self): return thermodynamics.GetEF_Ideal(self.mu,self.T)

    @property
    def EF_fit_err(self): return np.abs(thermodynamics.GetEF_Ideal(self.mu+self.mu_err,self.T+self.T_err)-thermodynamics.GetEF_Ideal(self.mu-self.mu_err,self.T-self.T_err))

    @property
    def EF_N_tot(self): return cst_MD_Class.hbar**2*(6* np.pi**2 * self.N_tot/(self.Volume/1e18))**(2/3)/(2*cst_MD_Class.mass)




    def show_result(self):
        fig, ax = plt.subplots(ncols=2, nrows=2, figsize=[12, 9])
        plt.subplot(2, 2, 1)
        plt.imshow(self.app)
        plt.xlabel('x')
        plt.ylabel('z')
        plt.title('Raw Image')
        plt.subplot(2, 2, 2)
        plt.plot(self.z_um_raw,self.n1dz)
        plt.title('1D Density Distribution')
        plt.xlabel('z [um]')
        plt.ylabel(r'$n_{1d} [um^{-1}]$')
        plt.show()

    def show_1d(self):
        n1d_fitted = thermodynamics.FD1d_au(self.P_1D,self.z_um_raw)
        plt.plot(self.z,self.n1dz,'.')
        plt.plot(self.z,n1d_fitted,linewidth=2)
        plt.xlabel('z [um]')
        plt.ylabel(r'$n_{1d}$ [$um^{-1}$]')
        plt.title('1D Density Profile')
        plt.show()
        print(r'''k_B T/ mu  =   {:.2f}'''.format(1/(self.P_1D[1]*self.P_1D[2])))

    def show_1d_kzsq(self):
        plt.plot(self.kz**2,self.n1dk,'.')
        plt.plot(self.n1dkBin['xmean'],self.n1dkBin['ymean'],marker=None,linestyle='-',linewidth=2)
        plt.xlabel(r'${k_z}^2$ [$um^{-2}$]')
        plt.ylabel(r'$f_{1d}$ [$um^{-2}$]')
        plt.xlim([0,4*self.kz_mu**2])

    def Fit1dProfile(self):
        z0=self.z_um_raw[np.argmax(self.n1dz)]
        offset0=0
        mu0=10000
        beta0=5/mu0
        A0=np.max(self.n1dz)/np.log(1+np.exp(mu0*beta0))

        # P[0]: overall amplitude P[1]:beta, P[2]:mu P[3]: z0 P[4]: offset
        def fitfun(z,P0,P1,P2,P3,P4):
            return thermodynamics.FD1d_au([P0,P1,P2,P3,P4],z)

        P_1D_fit,P_1D_jac=curve_fit(fitfun, self.z_um_raw, self.n1dz, [A0,beta0,mu0,z0,offset0])

        self.var['P_1D']=P_1D_fit
        self.var['P_1D_jac']=P_1D_jac
        self.var['z0']=P_1D_fit[3]
        self.var['z']=self.z_um_raw-P_1D_fit[3]

        return 0


    def FitFD(self):
        #fit the momentum distribution without addition fudge
        def fitfun1(x,P0,P1):
            return thermodynamics.FermiDirac([P0,P1],x)
        P_FD,P_FD_jac=curve_fit(fitfun1,self.kzBin,self.fk,[5,self.kz_mu**2])
        self.var['P_FD']=P_FD
        self.var['P_FD_jac']=P_FD_jac

        def fitfun2(x,P0,P1,P2):
            return thermodynamics.FermiDirac([P0,P1],x)*P2

        P_FD_exf,P_FD_exf_jac=curve_fit(fitfun2,self.kzBin,self.fk,[5,self.kz_mu**2,1])
        self.var['P_FD_exf']=P_FD_exf
        self.var['P_FD_exf_jac']=P_FD_exf_jac

        return 0

    def show_FDfit(self):
        self.FitFD()

        fk_fitted = thermodynamics.FermiDirac(self.var['P_FD'], self.kzBin)
        fk_fitted_exf= thermodynamics.FermiDirac(self.var['P_FD_exf'][0:2], self.kzBin)*self.var['P_FD_exf'][2]


        plt.errorbar(self.kzBin, self.fk, yerr=self.fk_err, linestyle='None', marker='.')
        line1,=plt.plot(self.kzBin,fk_fitted,linewidth=2,label='FD fit')
        line2,=plt.plot(self.kzBin, fk_fitted_exf, linewidth=2,label='FD fit with extra fudge')
        plt.legend(handles=[line1,line2],loc=1)
        plt.xlabel('$k_z$ [$um^{-1}$]')
        plt.ylabel('f(k)')
        plt.xlim([0,self.kz_mu*2.5])
        plt.show()
        return 0


####################################################################################
################################ Double Image ######################################

#properties:
#density porfiles of both states

class Double_Image:
    def __init__(self,imgA,imgB):
        na=np.sum(imgA.n)
        nb=np.sum(imgB.n)
        if nb>(1.2*na):
            self.ImgS1=imgB;
            self.ImgS2=imgA;
        else:
            self.ImgS1 = imgA;
            self.ImgS2 = imgB;


####################################################################################
################################ Curve #############################################

# Curve class for 1D functions
class Curve:
    """
    class for generic function f(xi) = yi

    Properties:
        x, y, data, dx, sorti

    Methods:
        __call__
        inverse (in progress)
        loc (in progress)
        sortbyx : returns sorted (x,y)
        binbyx : returns binned (x,y)
        subsample : returns sub sampled (x,y)
        diff (in progress)
        int (in progress)
    """

    def __init__(self, x=None, y=np.array([]), **kwargs):
        if x is None: x = np.arange(y.size)
        self.var = kwargs
        self.var['x'] = x.copy()
        self.var['y'] = y.copy()

    ### Properties ###

    @property
    def x(self):
        return self.var.get('x', np.array([]))

    @property
    def y(self):
        return self.var.get('y', np.array([]))

    @property
    def yfit(self):
        return self.var.get('yfit', None)

    @property
    def fitusing(self):
        return self.var.get('fitusing', None)

    @property
    def xyfitplot(self):
        return self.var.get('xyfitplot', None)

    @property
    def sorti(self):
        sorti = self.var.get('sorti', None)
        if sorti is None:
            sorti = np.argsort(self.x)
            self.var['sorti'] = sorti
        return sorti

    @property
    def dx(self):
        return (self.x[1] - self.x[0])

    @property
    def data(self):
        return (self.x, self.y)

    @property
    def plotdata(self):
        return (self.x / self.xscale, self.y / self.yscale)

    @property
    def xscale(self):
        return self.var.get('xscale',1)

    @property
    def yscale(self):
        return self.var.get('yscale', 1)

    @property
    def miny(self): return np.min(self.y)

    @property
    def maxy(self): return np.max(self.y)

    @property
    def minx(self): return np.min(self.x)

    @property
    def maxx(self): return np.max(self.x)

    ### High level methods ###
    def __call__(self, xi):
        return np.interp(xi, self.x[self.sorti], self.y[self.sorti])

    def __str__(self):
        des = 'A curve with ' + str(self.x.size) + ' data points.'
        return des

    def inverse(self, yi):
        pass

    def loc(self, x=None, y=None):
        if x != None:
            return self.locx(x)
        elif y != None:
            return self.locy(y)
        else:
            print('ERROR: Please provide x or y')
        return 0

    def chop(self,xlim=None,ylim=None):
        return self.trim(xlim, ylim)

    def subset(self, xlim=None, ylim=None):
        return self.trim(xlim, ylim)

    def trim(self,xlim=None,ylim=None):
        # Prepare using
        using = np.array(np.ones_like(self.x), np.bool)
        if xlim is not None:
            using[self.x < xlim[0]] = False
            using[self.x > xlim[1]] = False
        if ylim is not None:
            using[self.y < ylim[0]] = False
            using[self.y > ylim[1]] = False
        if np.sum(using) <= 2:
            using = np.array(np.ones_like(self.x), np.bool)
            print("X and Y limits given leads to too little points. All are being used")
        return self.copy(self.x[using], self.y[using])

    def sortbyx(self):
        return self.copy(self.x[self.sorti], self.y[self.sorti])

    def binbyx(self, **kwargs):
        return self.copy(*smooth.binbyx(self.x, self.y, **kwargs))

    def subsample(self, bins=2):
        return self.copy(*smooth.subsampleavg(self.x, self.y, bins=bins))

    def diff(self, **kwargs):
        method = kwargs.get('method', 'poly')
        if method == 'poly':
            dydx = calculus.numder_poly(self.x, self.y, order=kwargs.get('order', 1), points=kwargs.get('points', 1))
        elif method == 'central2':
            dydx = np.gradient(self.y, self.dx, edge_order=2)
        return self.copy(self.x, dydx)

    def removenan(self):
        self.var['x'] = self.x[np.isfinite(self.y)]
        self.var['y'] = self.y[np.isfinite(self.y)]

    def copy(self, x=None, y=None):
        if x is None: x = self.x
        if y is None: y = self.y
        return Curve(x=x, y=y, xscale=self.xscale, yscale=self.yscale)

    def fit(self, fitfun, guess, plot=False, pts=1000, noise=None, loss='cauchy', bounds=(-np.inf, np.inf), xlim=None, ylim=None):
        # Prepare using
        using = np.array(np.ones_like(self.x), np.bool)
        if xlim is not None:
            using[self.x<xlim[0]] = False
            using[self.x>xlim[1]] = False
        if ylim is not None:
            using[self.y<ylim[0]] = False
            using[self.y>ylim[1]] = False
        if np.sum(using) <= len(guess):
            using = np.array(np.ones_like(self.x), np.bool)
            print("X and Y limits given leads to too little points. All are being used")

        # Fit
        if noise is None:
            from scipy.optimize import curve_fit
            try:
                fitres, fiterr = curve_fit(fitfun, self.x[using], self.y[using], p0=guess, bounds=bounds)
                fiterr = np.sqrt(np.diag(fiterr))
            except RuntimeError as err:
                fitres = guess
                fiterr = guess
                print("CAN'T FIT, Returning Original Guess: Details of Error {}".format(err))
        else:
            from scipy.optimize import least_squares
            try:
                fitfun_ = lambda p: fitfun(self.x[using], *p) - self.y[using]
                fitres_ = least_squares(fun=fitfun_, x0=guess, loss=loss, f_scale=noise, bounds=bounds)
                fitres = fitres_.x
                fiterr = np.zeros_like(guess) * np.nan
            except RuntimeError as err:
                fitres = guess
                fiterr = np.zeros_like(guess) * np.nan
                print("CAN'T FIT, Returning Original Guess: Details of Error {}".format(err))

        yfit = fitfun(self.x, *fitres)
        xfitplot = np.linspace(np.min(self.x), np.max(self.x), pts)
        yfitplot = fitfun(xfitplot, *fitres)
        # Save results in var
        self.var['fitusing'] = using
        self.var['yfit'] = yfit
        self.var['xyfitplot'] = (xfitplot, yfitplot)
        self.var['fitres'] = fitres
        self.var['fiterr'] = fiterr
        # Plot and display
        if plot:
            # Plot
            plt.figure(figsize=(5, 5))
            ax1 = plt.subplot2grid((3, 1), (0, 0), rowspan=2)
            ax2 = plt.subplot2grid((3, 1), (2, 0))
            ax1.plot(*self.xyfitplot,'k-')
            ax1.plot(self.x, self.y, 'g.')
            ax1.plot(self.x[using], self.y[using],'r.')
            ax2.plot(self.x, self.y-self.yfit,'g.')
            ax2.plot(self.x[using], self.y[using] - self.yfit[using], 'r.')
            ax2.vlines(self.x, self.x*0, self.y-self.yfit)
            plt.xlabel('x')
            plt.ylabel('Difference')
            # Print
            print("##______Fit Value______Error______")
            for i,val in enumerate(fitres):
                print("{:2d} ==> {:9.4} (+-) {:9.4}".format(i, fitres[i], fiterr[i]))
        # return fitresults
        return (fitres, fiterr)

    ### Low level methods ###
    def locx(self, xi):
        x = self.x[self.sorti]
        iloc = np.argwhere(x <= xi)
        if len(iloc) == 0:
            return 0
        elif len(iloc) == x.size:
            return x.size - 1
        else:
            iloc = iloc[-1, 0]
        if (xi - x[iloc]) >= (x[iloc + 1] - xi): iloc += 1
        return iloc

    def locy(self, yi):
        pass

    def int(self, **kwargs):
        method = kwargs.get('method', 'sum')
        self.xInt = self.xLatest
        self.yInt = self.yLatest
        if method == 'sum':
            self.Int = np.sum(self.y) * self.dx
        return self.Int

    
###################################################################################

# Absorption Image Class
class AbsImage():
    '''
    Absorption Image Class

    Inputs:
        one of the three ways to define an image
        constants object (default is Li 6 Top Imaging)


    Inputs (Three ways to define an image):
        1) name (image filename with date prefix)
        2) wa and woa (numpy arrays)
        3) od (numpy array)
    cst object
    '''

    def __init__(self, *args, **kwargs):
        # Create a dict var to store all information
        self.var = kwargs
        self.cst = kwargs.get('cst', constants.cst())
        # Check the args
        if len(args) > 0 and type(args[0]) is str: self.var['name'] = args[0]

    # Universal Properties
    @property
    def wa(self):
        if 'wa' not in self.var.keys():
            alldata = self.alldata
            self.var['wa'] = alldata[0]
            self.var['woa'] = alldata[1]
        return self.var.get('wa')

    @property
    def woa(self):
        if 'woa' not in self.var.keys():
            alldata = self.alldata
            self.var['wa'] = alldata[0]
            self.var['woa'] = alldata[1]
        return self.var.get('woa')

    @property
    def od(self):
        if 'od' not in self.var.keys():
            self.var['od'] = (self.rawod * self.cst.ODf) + ((self.woa - self.wa) / self.cst.Nsat)
        return self.var['od']

    @property
    def rawod(self):
        if 'rawod' not in self.var.keys():
            self.var['rawod'] = imagedata.get_od(self.wa, self.woa, rawod=True)
        return self.var['rawod']

    @property
    def fixod(self):
        if 'fixod' not in self.var.keys():
            rawod = imagedata.get_od(self.wa, self.woa, width=self.var.get('trouble_pts_width', 5), rawod=False)
            self.var['fixod'] = (rawod * self.cst.ODf) + ((self.woa - self.wa) / self.cst.Nsat)
        return self.var['fixod']

    @property
    def ncol(self):
        return self.od / self.cst.sigma

    @property
    def atoms(self):
        return self.ncol * self.cst.pixel ** 2

    @property
    def total_atoms(self):
        return np.sum(self.atoms)

    @property
    def xy(self):
        x = np.arange(self.wa.shape[1])
        y = np.arange(self.wa.shape[0])
        return np.meshgrid(x, y)

    # Properties special for fits images
    @property
    def name(self):
        return self.var.get('name', 'NotGiven')

    @property
    def path(self):
        return imageio.imagename2imagepath(self.name)

    @property
    def rawdata(self):
        return imageio.imagepath2imagedataraw(self.path)

    @property
    def alldata(self):
        return imageio.imagedataraw2imagedataall(self.rawdata)

    # Crop index function
    def cropi(self, **kwargs):
        cropi = imagedata.get_cropi(self.od, **kwargs)
        if kwargs.get('plot',False):
            x = [cropi[1].start,cropi[1].start,cropi[1].stop,cropi[1].stop,cropi[1].start]
            y = [cropi[0].start,cropi[0].stop,cropi[0].stop,cropi[0].start,cropi[0].start]
            fig, ax = plt.subplots(figsize=(7,3),ncols=2)
            ax[0].imshow(self.od, cmap='viridis', clim=kwargs.get('odlim',(0,2)), origin='lower')
            ax[0].plot(x, y,'w-')
            ax[0].set(xlim=[0,self.od.shape[1]], ylim=[0,self.od.shape[0]])
            ax[1].imshow(self.od[cropi], cmap='viridis', clim=kwargs.get('odlim',(0,2)), origin='lower')
            ax[1].set(xlim=[0, self.od[cropi].shape[1]], ylim=[0, self.od[cropi].shape[0]])
        return cropi

    # fix intensities
    def fixVaryingIntensities_AllOutside(self, xmin, xmax, ymin, ymax):
        # Define a crop region and find factor*woa
        (x,y) = self.xy
        cropi = np.logical_and.reduce((x>=xmin, x<=xmax, y>=ymin, y<=ymax))
        factor = np.sum(self.alldata[0][cropi==0]) / np.sum(self.alldata[1][cropi==0])
        self.var['factor_woa'] = factor
        # Recalculate wa, woa, od, fixod
        self.var['wa'] = self.alldata[0]
        self.var['woa'] = self.alldata[1] * self.var['factor_woa']
        if 'od' in self.var.keys(): del self.var['od']
        if 'fixod' in self.var.keys(): del self.var['fixod']
        if 'rawod' in self.var.keys(): del self.var['rawod']

    def fixVaryingIntensities_Box(self, cropi=None, **kwargs):
        # Define a crop region and find factor*woa
        (x,y) = self.xy
        if cropi is None: cropi = self.cropi(**kwargs)
        factor = np.sum(self.alldata[0][cropi]) / np.sum(self.alldata[1][cropi])
        self.var['factor_woa'] = factor
        # Recalculate wa, woa, od, fixod
        self.var['wa'] = self.alldata[0]
        self.var['woa'] = self.alldata[1] * self.var['factor_woa']
        if 'od' in self.var.keys(): del self.var['od']
        if 'fixod' in self.var.keys(): del self.var['fixod']
        if 'rawod' in self.var.keys(): del self.var['rawod']

    # Auto crop hybrid
    def autocrop_hybrid(self, plot=False, odlim=(0,2), border = 50):
        # along y
        c = Curve(y=np.nansum(self.od, axis=1))
        max_y = np.max(c.y[c.y.shape[0]//4:3*c.y.shape[0]//4])
        ind = np.argwhere(c.y == max_y)[0][0]
        guess = [c.x[ind], c.x.shape[0]/10, c.y[ind], c.y[ind]/10, c.y[ind]/100]
        fy = c.fit(functions.fitfun_TF_harmonic, guess, plot=False)[0]
        # along x
        c = Curve(y=np.nansum(self.od, axis=0))
        max_y = np.max(c.y[c.y.shape[0] // 4:3 * c.y.shape[0] // 4])
        ind = np.argwhere(c.y == max_y)[0][0]
        guess = [c.x[ind], c.x.shape[0] / 10, c.y[ind], c.y[ind] / 10, c.y[ind] / 100]
        fx = c.fit(functions.fitfun_TF_harmonic, guess, plot=False)[0]
        # Generate cropi
        center = (int(fx[0]),int(fy[0]))
        width = 2 * int(min(fx[1] * 2, center[0] - border, self.od.shape[1] - center[0] - border))
        height = 2 * int(min(fy[1] * 2, center[1] - border, self.od.shape[0] - center[1] - border))
        return self.cropi(center=center, width=width, height=height, plot=plot, odlim=odlim)

    # Averaging multiple images together
    def avgod(self, *args):
        avg = self.od
        for im in args: avg += im.od
        return avg / (1 + len(args))

    # pixels that are not usable are defined by:
    def usable(self, threshold=25):
        return imagedata.get_usable_pixels(self.wa, self.woa, threshold=threshold)

    # Fixing nan and inf
    # Example
    # indices = np.where(np.isnan(a)) #returns an array of rows and column indices
    # for row, col in zip(*indices):
    # a[row,col] = np.mean(a[~np.isnan(a[:,col]), col]) need to modify this

    # def interpolate_nans(X):
    # """Overwrite NaNs with column value interpolations."""
    # for j in range(X.shape[1]):
    # 	mask_j = np.isnan(X[:,j])
    # 	X[mask_j,j] = np.interp(np.flatnonzero(mask_j), np.flatnonzero(~mask_j), X[~mask_j,j])
    # return X


#################################################################################


class XSectionTop:
    '''
    Compute Cross sectional area for a hybrid image using circular fits

    Inputs:
        od     --  cropped od image (od is recommanded because i know that amplitude is in range 0 to ~3)
        yuse   --  the range of y indices to use for fitting circles. Use np.arange(start, stop, step).
                   use None (or don't provide) to auto generate it
        method --  method for extending fitted radii: linead (default), poly4, spline
        plot   --  True or False, a sample plot with analysis, default False
        odlim  --  clim for imshow for the od, default (0,2)
        yset   --  settings for auto yuse: (y step, fraction of R_TF to use), default (10,0.75)
        guess  --  guess for circle fit: (x_center, radius, amplitude, m, b), default (xlen/2, xlen/5, max)

    Useful properties and calls:
        self(y_indices) returns area for provided y_indices. (must be within od size range)
        self.rad
        self.area
        self.yall
    '''
    def __init__(self, od, yuse = None, method='linear', plot=False, odlim=(0,2), yset = (10, 0.75), guess = None):
        self.prepare(od, yuse, odlim, yset, guess)
        self.fitall()
        if method == 'spline': self.extend_spline()
        elif method == 'poly4': self.extend_poly4()
        else: self.extend_linear()

        if plot: self.infoplot()

    def __call__(self, y):
        # Make it an integer
        y = np.int32(np.round(y))
        return self.area[y]

    def prepare(self, od, yuse, odlim, yset, guess):
        # General things
        self.yuse = yuse
        self.od = od
        self.odlim = odlim
        self.guess = guess
        self.yset_ = yset
        if yuse is None: yuse = self.get_yuse()
        self.dy = yuse[1] - yuse[0]
        # ycen_ vs. xc_, r_, xl_, xr_, c_
        self.ycen_ = yuse[0:-1] + self.dy / 2
        self.xc_, self.r_ = np.zeros_like(self.ycen_), np.zeros_like(self.ycen_)
        self.c_ = [None] * self.xc_.shape[0]
        self.fitres_ = [None] * self.xc_.shape[0]
        self.fiterr_ = [None] * self.xc_.shape[0]
        # yall vs rad, area
        self.yall = np.arange(od.shape[0])

    def fitall(self):
        if self.guess is None:
            c = Curve(y=np.nanmean(self.od[self.yuse[0]:self.yuse[0 + 1], :], axis=0))
            self.guess = [c.x.shape[0] / 2, c.x.shape[0] / 5, np.max(c.y), 0, 0]
        for i, yc in enumerate(self.ycen_):
            c = Curve(y=np.nanmean(self.od[self.yuse[i]:self.yuse[i + 1], :], axis=0))
            c.removenan()
            fitres, fiterr = c.fit(self.fitfun, self.guess, plot=False)
            self.xc_[i] = fitres[0]
            self.r_[i] = fitres[1]
            self.c_[i] = c
            self.fitres_[i] = fitres
            self.fiterr_[i] = fiterr

        self.xl_ = self.xc_ - self.r_
        self.xr_ = self.xc_ + self.r_

    def get_yuse(self):
        c = Curve(y = np.nanmean(self.od,axis=1))
        c.removenan()
        # fit TF profile to this
        fitres, fiterr = c.fit(self.fitfun_TF, [c.x.shape[0] / 2, c.x.shape[0] / 4, np.max(c.y), np.max(c.y)/100, np.max(c.y)/100], plot=False)
        fitres[1] = fitres[1] * self.yset_[1]
        self.yuse = np.arange(int(fitres[0]-fitres[1]), int(fitres[0]+fitres[1]), self.yset_[0])
        return self.yuse

    def extend_linear(self):
        fitres = np.polyfit(self.ycen_, self.r_, deg=1)
        self.radfit = np.poly1d(fitres)
        self.rad = self.radfit(self.yall)
        self.area = np.pi * self.rad ** 2

    def extend_poly4(self):
        fitres = np.polyfit(self.ycen_, self.r_, deg=4)
        self.radfit = np.poly1d(fitres)
        self.rad = self.radfit(self.yall)
        self.rad[self.yall < self.ycen_[0]] = self.radfit(self.ycen_[0])
        self.rad[self.yall > self.ycen_[-1]] = self.radfit(self.ycen_[-1])
        self.area = np.pi * self.rad ** 2

    def extend_spline(self):
        tck = spintp.splrep(self.ycen_, self.r_, s=100)
        self.rad = spintp.splev(self.yall, tck, der=0)
        self.rad[self.yall < self.ycen_[0]] = spintp.splev(self.ycen_[0], tck, der=0)
        self.rad[self.yall > self.ycen_[-1]] = spintp.splev(self.ycen_[-1], tck, der=0)
        self.area = np.pi * self.rad ** 2

    def fitfun(self, x, x0, rad, amp, m, b):
        y = 1 - ((x - x0) / rad) ** 2
        y[y <= 0] = 0
        y[y > 0] = np.sqrt(y[y > 0]) * amp
        y += m * x + b
        return y

    def infoplot(self):
        # Figure
        fig = plt.figure(figsize=(8, 5))
        # Setup axes
        ax1 = plt.subplot2grid((3, 3), (0, 0), colspan=2)
        ax2 = plt.subplot2grid((3, 3), (1, 0), rowspan=2, colspan=2)
        axc = [None] * 3
        axc[0] = plt.subplot2grid((3, 3), (0, 2))
        axc[1] = plt.subplot2grid((3, 3), (1, 2))
        axc[2] = plt.subplot2grid((3, 3), (2, 2))
        # Plot od and measured edges
        ax1.scatter(self.ycen_, self.xl_, s=1, color='white')
        ax1.scatter(self.ycen_, self.xr_, s=1, color='white')
        ax1.scatter(self.ycen_, self.xc_, s=1, color='k')
        ax1.imshow(self.od.T, clim=self.odlim, aspect='auto', cmap='viridis', origin='lower')
        ax1.set(xlim=[self.yall[0], self.yall[-1]], title='OD and radius')
        ax1.set_axis_off()
        # Plot measured and fitted radius
        ax2.plot(self.yall, self.rad, 'k-')
        ax2.scatter(self.ycen_, self.r_, color='red')
        ax2.set(xlim=[self.yall[0], self.yall[-1]])
        # Plot 3 smaple fits
        for i, j in zip([0, 1, 2], [0, self.r_.shape[0] // 2, -1]):
            axc[i].plot(*self.c_[j].xyfitplot, 'k-')
            axc[i].scatter(*self.c_[j].data, color='red', s=1, alpha=0.5)
            axc[i].set_axis_off()
            axc[i].set(title='Cut @ y = {}'.format(self.ycen_[j]))
        # Adjust layout information
        fig.subplots_adjust(hspace=0.1, wspace=-0.1)
        self.fig = fig

    def fitfun_TF(self, x, x0, rad, amp, m=None, b=None):
        y = amp * (1 - ((x - x0) / rad) ** 2) ** (3 / 2)
        y = np.real(y)
        y[np.isnan(y)] = 0
        if m is not None: y += m * x + b
        return y

# Removing OD gradients in cropped image
class ODFix2D:
    def __init__(self, od, cropi, width=20, odlim=(0, 2), plot=False):
        self.prepare(od, cropi, width, odlim)
        self.nanFix()
        self.fit()
        if plot: self.infoplot()

    def prepare(self, od, cropi, width, odlim):
        self.w = width
        self.odlim = odlim
        self.cropi = tuple([slice(x.start - width, x.stop + width, x.step) for x in cropi])
        # Get od and od bg
        self.od_ = od[self.cropi]
        self.odbg = self.od_.copy()
        self.odbg[width:-width, width:-width] = np.nan
        # Generate z = f(x, y), convert grid to 1d
        self.x, self.y = np.meshgrid(np.arange(self.od_.shape[1]), np.arange(self.od_.shape[0]))
        self.z = self.od_[np.isfinite(self.odbg)]
        self.xy = np.array([self.x[np.isfinite(self.odbg)], self.y[np.isfinite(self.odbg)]])

    def nanFix(self):
        # Bad Points
        x, y = np.meshgrid(np.arange(self.od_.shape[1]), np.arange(self.od_.shape[0]))
        self.odx1 = x[np.logical_not(np.isfinite(self.od_))]
        self.ody1 = y[np.logical_not(np.isfinite(self.od_))]
        # Fix OD
        self.od_ = imagedata.fix_od(self.od_, width=5)

    def fit(self):
        from scipy.optimize import curve_fit
        guess = [0, 0, 0]
        self.fitres, self.fiterr = curve_fit(self.fitfun_2DPoly, self.xy, self.z, p0=guess)
        # Plotting items
        self.bg = self.fitfun_2DPoly_2D(self.x, self.y, *self.fitres)
        self.od = self.od_ - self.bg
        self.od = self.od[self.w:-self.w, self.w:-self.w]

    def fitfun_2DPoly(self, xy, b, m1, m2):
        return b + m1 * xy[0] + m2 * xy[1]

    def fitfun_2DPoly_2D(self, x, y, b, m1, m2):
        return b + m1 * x + m2 * y

    def infoplot(self):
        fig = plt.figure(figsize=(8, 5))
        ax = plt.subplot2grid((2, 3), (0, 0), colspan=2)
        ax1 = plt.subplot2grid((2, 3), (0, 2))
        ax2 = plt.subplot2grid((2, 3), (1, 0))
        ax3 = plt.subplot2grid((2, 3), (1, 1))
        ax4 = plt.subplot2grid((2, 3), (1, 2))

        ax.imshow(self.od_.T, clim=self.odlim, cmap='viridis', aspect='auto', origin='lower')
        ax.scatter(self.ody1, self.odx1, color='red', alpha=0.2, marker='.', s=3)
        ax.plot([self.w, self.w, self.od_.shape[0] - self.w, self.od_.shape[0] - self.w, self.w],
                [self.w, self.od_.shape[1] - self.w, self.od_.shape[1] - self.w, self.w, self.w], 'w-')
        ax.set(xlim=[0, self.od_.shape[0]], ylim=[0, self.od_.shape[1]], title='OD: {} points fixed'.format(self.odx1.size))
        ax.set_axis_off()
        ax1.plot(np.nanmean(self.bg[0:self.w, :], axis=0))
        ax1.plot(np.nanmean(self.odbg[0:self.w, :], axis=0), 'r.', markersize=2)
        ax1.set(title='left')
        ax2.plot(np.nanmean(self.bg[:, 0:self.w], axis=1))
        ax2.plot(np.nanmean(self.odbg[:, 0:self.w], axis=1), 'r.', markersize=2)
        ax2.set(title='bottom')
        ax3.plot(np.nanmean(self.bg[:, -self.w:], axis=1))
        ax3.plot(np.nanmean(self.odbg[:, -self.w:], axis=1), 'r.', markersize=2)
        ax3.set(title='top')
        ax4.plot(np.nanmean(self.bg[-self.w:, :], axis=0))
        ax4.plot(np.nanmean(self.odbg[-self.w:, :], axis=0), 'r.', markersize=2)
        ax4.set(title='right')
        self.fig = fig

###################################################################################


# Convert OD to Density
class OD2Density:
    def __init__(self, od, xsec, pixel, sigma, nmax=np.inf, Ncor=1, plot=False, center=None):
        self.prepare(od, xsec, pixel, sigma, nmax, Ncor, center)
        self.extract_density_all()
        self.find_center_TF()
        if plot: self.infoplot()

    def prepare(self, od, xsec, pixel, sigma, nmax, Ncor, center):
        self.od = od.copy()
        self.xsec = xsec
        self.pixel = pixel
        self.sigma = sigma
        self.nmax = nmax
        self.Ncor = Ncor
        self.center = center

    def extract_density_all(self):
        atomNumber = np.nansum(self.od, axis=1) * self.pixel ** 2 / self.sigma
        atomDensity = atomNumber / (self.xsec.area * self.pixel ** 3) * self.Ncor
        self.atomDensity = atomDensity

    def find_center_TF(self):
        use = self.atomDensity < self.nmax
        c = Curve(x=np.arange(self.atomDensity.shape[0])[use], y=self.atomDensity[use])
        guess = [c.x.shape[0] / 2, c.x.shape[0] / 4, np.max(c.y), np.max(c.y) / 10, np.max(c.y) / 100]
        fitres, fiterr = c.fit(functions.fitfun_TF_harmonic, guess, plot=False)
        y = c.y - (functions.fitfun_TF_harmonic(c.x, fitres[0], fitres[1], 0, fitres[3], fitres[4]))
        if self.center is None: self.center = fitres[0]
        self.nz = Curve(x=(c.x - self.center) * self.pixel, y=y, xscale=1e-6)
        guess = [self.pixel, fitres[1]*self.pixel, fitres[2], fitres[3], fitres[4]/self.pixel]
        self.nz.fit(functions.fitfun_TF_harmonic, guess, plot=False)

    def infoplot(self):
        fig, ax1 = plt.subplots(figsize=(4, 3))
        ax1.scatter(self.nz.x * 1e6, self.nz.y,color='red',alpha=0.5,marker='.',s=7)
        ax1.plot(self.nz.xyfitplot[0]*1e6,self.nz.xyfitplot[1],'k-')


###################################################################################


# Main
def main():
    # # Tests of Curve
    # xi = np.linspace(0,3,100)
    # yi = np.sin(xi**2)
    # dydx = np.cos(xi**2) * 2 * xi
    # yin = yi + np.random.normal(scale=0.1,size=xi.shape)
    # curve0 = Curve(xi,yi)
    # curve1 = Curve(xi, yin)

    # plt.plot(*curve0.plotdata,'b-')
    # plt.plot(*curve1.subsample(bins=4),'r.')
    # plt.plot(xi, dydx,'b-')
    # plt.plot(*curve1.diff(method='poly'),'ko')
    # plt.plot(*curve1.diff(method='gaussian filter'),'gs')
    # plt.show()

    # print(curve0.int())
    # print(curve0.dx)

    wa = np.ones((512, 512))
    woa = np.ones_like(wa) + 0.1

    img1 = AbsImage(wa=wa, woa=woa)
    print(img1.name)
    img2 = AbsImage(name='03-24-2016_21_04_12_top')
    print(img2.rawdata.shape)
    print(img2)


if __name__ == '__main__':
    main()
