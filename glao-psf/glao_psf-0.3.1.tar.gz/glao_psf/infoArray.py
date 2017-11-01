"""
info_array - define class and methods for the 'Information'-packed
ndarray. it inherits all the metods of the numpy array class
and adds the ability to set other attributes, pretty-print, and smart graphing.
"""
import os
import subprocess
import numpy as np
import dimg
plt = dimg.plt
import img
from units import units
import scipy.ndimage
import h5py
import pyfits

def copyattrs(sobj,dobj):
    d = sobj.__dict__
    keys = d.keys()
    for key in keys:
        setattr(dobj,key,d[key])
    
class InfoArray(np.ndarray):
    """
    A sub class of `numpy.ndarray <http://docs.scipy.org/doc/numpy/reference/arrays.ndarray.html>`_, with useful additional attributes like **name**, **dx**, and **units.**
    
    (See `numpy array subclassing <http://docs.scipy.org/doc/numpy-1.10.1/user/basics.subclassing.html>`_)
    
    to use::
    
        a = InfoArray(np.zeros((2,2)),name='blah')
        a.dx = ...
    
    InfoArrays are containers in that they can contain any number of attributes. Useful ones are:
    
    :ivar str name: The name of the array
    :ivar str units: The units of the values in the array
    :ivar float dx: The physical size of one pixel in the array
    :ivar str dx_units: The units of the pixel size
    :ivar list axis_names: A list of strings containing the axis names
        The first and second are the horizontal and vertical axes correspondingly.
        An optionall third is the radial (for radial average plots).
    :ivar list x0y0: Physical position of the [0,0] pixel (defaults to -shape*dx/2)
    
    """
    def __new__(cls, input_array, name='',**kwargs):
        obj = np.asarray(input_array).view(cls)
        if type(input_array) is InfoArray:
            copyattrs(input_array,obj)
            setattr(obj,'name',name)
                
        else:
            obj.name = name
            obj.units = ''
            obj.dx = 1.0
            obj.dx_units = ''
            obj.plotParams = {
                'fontsize.title':16,
                'fontsize.subtitle':13,
                'fontsize.axis':12,
                'fontsize.tick':10,
                'axislabel.left':True,
                'axislabel.right':True,
                'axislabel.top':True,
                'axislabel.bottom':True,
            }

        obj.__dict__.update(kwargs)
        return obj
    
    def __array_finalize__(self, obj):
        if obj is None: return
        if isinstance(obj,InfoArray):
            copyattrs(obj,self)
        
    def copy(self):
        """Return a deep copy of the InfoArray
        
        :rtype: InfoArray
        """
        obj = InfoArray(self.view(np.ndarray).copy())
        copyattrs(self,obj)
        return obj
    
    def minmax(self):
        """Calculate the miimum and maximum of the array
        
        :return: a list of [minimumm, maximum]

        """
        return (self.min(),self.max())    
    
    def pprint(self,full=False):
        """Pretty-print the object. This consists
        of reporting on the object's attributes.

        :param boolean full: if True, **pprint** also prints out the contents of the array.
            Default is to print only the "header" (attributes) information.

        """
        print self._pprint(full=full)
    
    def oft(self,upsamp=1):
        """Performs the Optical Fourier Transform on the array
        and returns a new InfoArray object. The object data are treated as
        optical path distances (OPD). An InfoArray object representing the aperture
        throughput can be included as an instance object, otherwise a default unit disk is used
        
        The forumla is
            PSF = F { ap exp {i (2 pi / wavelength) OPD } }
        
        OFT assumes that the object has the following instance variables, and if it
        does not, then default ones are set up:
            
            wavelength = wavelength of the light, in microns (default: 0.5)
            ap = an InfoArray object that defines the aperture (default: a circlular disk that assures Nyquist sampling)
            units = the units of the wavefront (default: 'meters')
            dx_units = the units of dx (default: 'meters')
        """
        
        if not hasattr(self,'wavelength'):
            self.wavelength = 0.5
            self.wavelength_units = 'microns'
        n,m = self.shape
        lam = self.wavelength*units[self.wavelength_units]
        k = 2.*np.pi/lam
        if not hasattr(self,'ap'):
            ap = img.circle((n,m),r=min(n,m)/4.)
            self.ap = InfoArray(ap,name='%s.ap'%self.name,
                                units = 'throughput',
                                dx = self.dx,
                                dx_units = self.dx_units,)
        dx = self.dx*units[self.dx_units]
        wf = self.ap*np.exp(1j*k*self*units[self.units])
        dth = lam/(n*dx)/units['arcsec']
        dth_units = 'arcsec'
        if upsamp in [2,4,8]:
            wf = img.zeropad(wf,(n*upsamp,m*upsamp))
            dth = upsamp*dth
        psf = np.abs( np.fft.ifftshift( np.fft.fft2( np.fft.fftshift(wf))))**2
        if upsamp != 1:
            psf = img.crop(psf,np.array(psf.shape)/2,(n,m))
        psf = InfoArray(psf/psf.max(),
                        name='OFT(%s)'%self.name,
                        units = 'normalized to peak',
                        dx = dth,
                        dx_units = dth_units,
                        wavelength = self.wavelength,
                        wavelength_units = self.wavelength_units)
        return psf
    
    def psf(self):
        """Compute the PSF (Point Spread Function) assuming the data are the MTF
        (Modulation Transfer Function). It is assumed that the MTF is symmetric
        so that the PSF is real
        """
        n,m = self.shape
        lam = self.wavelength*units[self.wavelength_units]
        k = 2.*np.pi/lam
        dx = self.dx*units[self.dx_units]
        dth = lam/(n*dx)/units['arcsec']
        dth_units = 'arcsec'
        psf = np.abs(np.fft.ifftshift(np.fft.fft2(np.fft.fftshift(self))))
        psf = InfoArray(psf/psf.max(),
                        name ='PSF(%s)'%self.name,
                        units = 'normalized to peak',
                        dx = dth,
                        dx_units = dth_units,
                        wavelength = self.wavelength,
                        wavelength_units = self.wavelength_units)
        return psf
    
    def mtf(self):
        """Compute the MTF (Modulation Transfer Function) assuming that the data
        are the PSF (Point Spread Function). It is assumed that the PSF is real
        """
        n,m = self.shape
        lam = self.wavelength*units[self.wavelength_units]
        k = 2.*np.pi/lam
        dx = self.dx*units[self.dx_units]
        dth = lam/(n*dx)
        dth_units = 'meters'
        mtf = np.abs(np.fft.ifftshift(np.fft.ifft2(np.fft.fftshift(self))))
        mtf = InfoArray(mtf/mtf.max(),
                        name ='MTF(%s)'%self.name,
                        units = 'normalized to peak',
                        dx = dth,
                        dx_units = dth_units,
                        wavelength = self.wavelength,
                        wavelength_units = self.wavelength_units)
        return mtf
    
    def calc_ena(self):
        """Calculate the Equivalent Noise Area, assuming the data represent
        a point spread function (PSF).
        Reference: King, PASP, v95, 1983
        
        Formula:
            ENA = dA / \sum_i f_i^2
            
        where dA is the area of a pixel (dx^2), and f is the psf normalized to integrate
        to unity.
        The PSF is assumed real.
        """
        f = self/self.sum()
        ena = self.dx**2/np.sum(f**2)
        ena_units = '%s^2'%self.dx_units
        ena_r = np.sqrt(ena/np.pi)
        ena_r_units = '%s'%self.dx_units
        self.ena,self.ena_units = (ena,ena_units)
        self.ena_r,self.ena_r_units = (ena_r,ena_r_units)
        return
    
    def calc_ee(self,p):
        """Calculate the radius containing a given encircled energy (assuming the
        data represent a point spread function)
        
        p = the encircled energy fraction, a number between 0 and 1
        """
        q = img.encircled_energy(self,p,f='nan')*self.dx
        prop = 'EE_%02d'%int(np.round(100.*p))
        self.__dict__[prop] = float(q)
        self.__dict__[prop+'_units'] = self.dx_units + ' radius'

    def resample(self,dx):
        """Resample the image so as to have a different dx.
        This will increase or decrease the dimensions of the data.        
        """
        r = scipy.ndimage.zoom(self,self.dx/dx)
        r = InfoArray(r)
        copyattrs(self,r)
        r.dx = dx
        r.name = r.name+'_zoomed'
        return r
    
    def resize(self,shape):
        """Resize the image by resampling. This will
        change the sampling dx. It is prevented from changing the
        aspect ratio.
        """
        n,m = self.shape
        nr,mr = shape
        fac = float(nr)/float(n)
        mrt = fac*float(m)
        if not np.isclose(mr,mrt,atol=1):
            raise Exception,'<resize> can\'t change aspect ratio'
        return self.resample(self.dx/fac)

    def crop(self,shape,p0=None):
        """Crop the image to a different size than the present image.
        This different size can be larger or smaller than the original image.
        p0 is an optional lower left hand corner for the crop
        """
        center = np.array(self.shape)/2
        if p0 is not None:
            center = np.array(p0) + np.array(shape)/2
        r = img.crop(self,center,shape)
        r = InfoArray(r)
        copyattrs(self,r)
        r.name = r.name+'_cropped'
        return r

    def _pprint(self,print_width=40,aslist=False,rshort=False,full=False):
        cr = '\n'
        bling = 50*'='
        rs = []
        rs.append(bling)
        if hasattr(self,'longName'):
            rs.append(self.longName)
        else:
            if hasattr(self,'name') and self.name is not None:
                rs.append(self.name)
        rs.append(str(type(self)))
        rs.append(bling)
        rs.append('shape: '+str(self.shape))
        if rshort:
            if aslist:
                return rs
            else:
                rs = '\n'.join(rs)
                return rs
        if full:
            rs.append(str(self))
        tab = ' '*4
        d = self.__dict__
        keys = sorted(d.keys())
        for key in keys:
            if key.endswith('_units'): continue
            val = d[key]
            units = None
            if isinstance(val,(str,unicode)): pv = "'"+val+"'"
            else: pv = str(val)
            if len(pv) > print_width:
                pv = str(val.__class__)
                if isinstance(val,(np.ndarray,np.matrix)):
                    pv += ' '+str(val.shape)
            if key+'_units' in keys:
                units = d[key+'_units']
            line = key+':'+tab+pv
            if units is None:
                pass
            else:
                line += ' '+units
            if isinstance(val,InfoArray):
                if (hasattr(val,'longName')):
                    line += " '"+val.longName+"'"
                else:
                    line += " '"+val.name+"'"
            else:
                pass
            rs.append(line)
        rs.append(bling)
        if aslist:
            return rs
        else:
            rs = '\n'.join(rs)
            return rs
       
    def plot(self,kind='image',fontsize=14,grid=False,oplot=False,scale='lin',fuzz=1e-9,**kwargs):
        """Display the InfoArray data as an image or lineout plot
        
        :param str kind: plot kind: 'image','lineout',or 'radial'
        :param int fontsize: for the titles, axis labels, and tick labels
        :param boolean grid: draw axis grid
        :param boolean oplot: whether or not to plot over a prevous graph (only for line plots)
        :param str scale: plot scale: 'lin','sqrt','log','loglog'
        :param float fuzz: a minimum value for log scale 
                    to keep the image contrast reasonable
                    (used only for 'image', scale='log')
        :param **kwargs: is sent on to dimg.show in the kind='image' case
        """
        scales = ['lin','sqrt','log','loglog']
        assert scale in scales,'scale must be one of '+scales
        n,m = self.shape
        if isinstance(self,np.matrix):
            valid_kinds = ['image']
            necessary_keys = set(['name'])
        else:
            valid_kinds = ['image','lineout','radial']
            necessary_keys = set(['units','dx','dx_units','name'])
        assert kind in valid_kinds,'kind must be one of '+valid_kinds
        keys = self.__dict__.keys()
        assert necessary_keys.issubset(set(keys)),'Object must have attributes '+str(list(necessary_keys))
        if hasattr(self,'longName'):
            name = self.longName
        else:
            name = self.name
        if isinstance(self,np.matrix):
            x0,y0 = 0,0
            if (hasattr(self,'axis_names')):
                xlabel = self.axis_names[1]
                ylabel = self.axis_names[0]
            else:
                xlabel = 'column index'
                ylabel = 'row index'
            origin = 'upper'
            xlim = [x0,x0+n]
            ylim = [y0+n,y0]
        else:
            dx = self.dx
            dx_units = self.dx_units
            if hasattr(self,'x0y0'):
                x0,y0 = self.x0y0
            else:
                x0,y0 = -(float(m)/2)*dx-dx/2, -(float(n)/2)*dx-dx/2
            origin = 'lower'
            xlim = [x0,x0+m*dx]
            ylim = [y0,y0+n*dx]
            if 'dy_units' in keys:
                dy_units = self.dy_units
            else:
                dy_units = self.dx_units
            if 'axis_names' in keys:
                xlabel = self.axis_names[0]+'  '+dx_units
                ylabel = self.axis_names[1]+'  '+dy_units
                if len(self.axis_names)>2:
                    rlabel = self.axis_names[2]+'  '+dx_units
                else:
                    rlabel = dx_units
            else:
                xlabel = dx_units
                ylabel = dy_units
                rlabel = dx_units
        
        data = np.array(self)
        if np.iscomplex(data).any():
            print '<Object.plot> data is COMPLEX - showing the absolute value'
            data = np.abs(data)
            name = name+' (ABSOLUTE VALUE)'
        
        if not oplot and kind is not 'image':
            plt.figure()
        
        if len(self.units) > 0:
            name += ', '+self.units
        
        if kind == 'radial':
            name += ' radial average'
            x = np.arange(xlim[0],xlim[1],dx)
            y = np.arange(ylim[0],ylim[1],dx)
            x,y = np.meshgrid(x,y)
            r = np.sqrt(x**2+y**2)
            bins = np.arange(0,(n/2)*dx,dx)
            i = np.digitize(r.flatten(),bins)
            c = np.bincount(i)
            q = np.zeros(n/2+1)
            for j,y in zip(i,data.flatten()):
                q[j] += y
            q /= c
            q = q[:-1]
            plt.plot(bins,q)
            if not oplot:
                ax = plt.gca()
                ax.set_xlabel(rlabel,fontsize=self.plotParams['fontsize.axis'])
                ax.set_ylabel(self.units,fontsize=self.plotParams['fontsize.axis'])
                ax.tick_params(axis='both',which='major',labelsize=self.plotParams['fontsize.tick'],direction='out',length=6,width=1,
                               labeltop=False,labelbottom=True,labelleft=True,labelright=False)
                plt.title(name,y=1.04)
            if scale == 'log':
                ax.set_yscale('log')
            if scale == 'loglog':
                ax.set_xscale('log')
                ax.set_yscale('log')
                
        if kind == 'lineout':
            y = data[n/2,:]
            x = np.arange(xlim[0],xlim[1],dx)
            plt.plot(x,y,**kwargs)
            if not oplot:
                ax = plt.gca()
                ax.set_xlabel(xlabel,fontsize=self.plotParams['fontsize.axis'])
                ax.set_ylabel(self.units,fontsize=self.plotParams['fontsize.axis'])
                ax.tick_params(axis='both',which='major',labelsize=self.plotParams['fontsize.tick'],direction='out',length=6,width=1,
                               labeltop=False,labelbottom=True,labelleft=True,labelright=False)
                plt.title(name,y=1.04)
            if scale == 'log':
                ax.set_yscale('log')

        if kind == 'image':
            if scale == 'log':
                data = np.log10(np.clip(np.abs(data),fuzz,np.inf))
            if scale == 'sqrt':
                data = np.sqrt(np.abs(data))
            dimg.show(data,extent = xlim+ylim,origin=origin,title=name,**kwargs)
            ax = plt.gca()
            if not oplot:
                ax.set_xlabel(xlabel,fontsize=self.plotParams['fontsize.axis'])
                ax.set_ylabel(ylabel,fontsize=self.plotParams['fontsize.axis'])
                ax.tick_params(axis='both',which='major',labelsize=self.plotParams['fontsize.tick'],direction='out',length=6,width=1)
                top,bottom,right,left = self.plotParams['axislabel.top'],self.plotParams['axislabel.bottom'],self.plotParams['axislabel.right'],self.plotParams['axislabel.left']
                ax.tick_params(axis='both',which='both',
                               top=top,bottom=bottom,right=right, left=left,
                               labeltop=top,labelbottom=bottom,labelleft=left,labelright=right)
                if hasattr(self,'sub'):
                    plt.subplots_adjust(top=0.84)
                    plt.suptitle(name, y=0.995, fontsize=self.plotParams['fontsize.title'])
                    plt.title(self.sub, y=1.08, fontsize=self.plotParams['fontsize.subtitle'])
                else:
                    plt.title(name,y=1.08, fontsize=self.plotParams['fontsize.title'])

        if not oplot:
            ax.tick_params(axis='both',which='minor',direction='out',length=4,width=1)
            plt.minorticks_on()
        
        plt.grid(grid)
        plt.draw()
        
    def graph(self,**kwargs):
        kwargs['kind'] = 'lineout'
        self.plot(**kwargs)
        
    def display(self,**kwargs):
        kwargs['kind'] = 'image'
        self.plot(**kwargs)
        
    def show(self,**kwargs):
        self.plot(**kwargs)
    
    def save(self,filename = None, group='/',file_type = None,clobber=False,verbose=False):
        """Write an InfoArray to a disk file. Only hdf5 and FITS file types
        are presently supported. The file type is derived
        from the filename extension (*.hdf5, *.fits); the
        keyword parameter file_type overrides.
        
        HDF5:
        
            Ceate a group within the hdf5 file
            (creating a new file if necessary) and store the
            data and metadata (InfoArray attributes) as datasets in the group,
            named 'data' and 'metadata' respectively.
            The group is named the same as the name of the InfoArray.
            Name uniqueness is checked within an existing group
            and will not overwrite an existing dataset of the same name.

            Storing into a subgroup is possible using the tree structure
            syntax of th group parameter.
        
        FITS:
        
            For FITS files, create the header from the
            InfoArray attributes and store the data as a single primary HDU.
            The filename is an optional parameter. The filename is based on
            the InfoArray's name (<name>.fits) if filename is not specivied.
        """
        assert self.name != ''
        valid_filetypes = {'hdf5':'hdf5','hd5':'hdf5',
                           'fits':'fits','fit':'fits'}
        if filename is None:
            filename = '%s.hdf5'%self.name
        basename,ext = os.path.splitext(filename)
        if ext == '':
            if file_type is not None:
                ext = file_type
            else:
                ext = 'hdf5'
        assert ext[1:] in valid_filetypes.keys()
        if verbose:
            print '<save> saving to file %s in %s format'%(filename,file_type)

        if file_type == 'hdf5':
            #metadata = encode(self.__dict__) # future encoder of dictionaries
            metadata = 'name: %s, dx: %r'%(self.name,self.dx)  # very primative for now
            name = '_'.join(self.name.split()) # replaces whitespace with _
            f = h5py.File(filename)
            if group in f:
                top = f[group]
            else:
                top = f.create_group(group)
            if name in top.keys():
                f.close()
                raise ValueError,'name "%s" not unique in %s'%(name,filename)
            grp = top.create_group(self.name)
            grp.create_dataset('data', data=self)
            grp.create_dataset('metadata',data=metadata)
            f.close()
        if file_type == 'fits':
            hdu = self._hdu()
            hdu.writeto(filename,clobber=clobber)
        else:
            raise ValueError, '%s is not a supported file_type'%file_type
    
    def _hdu(self):
        """Create a fits header data unit from the object
        data and metadata
        """
        hdu = pyfits.PrimaryHDU(self)
        hdr = hdu.header            
        for key in self.__dict__.keys():
            val = self.__dict__[key]
            if not isinstance(val,(str,int,long,float,bool)):
                continue
            if key+'_units' in self.__dict__:
                u = self.__dict__[key+'_units']
                hdr.append((key.upper()[:8],val,u),end=True)
            elif not key.endswith('_units'):
                hdr.append((key.upper()[:8],val),end=True)
        return hdu        
    
def load(filename,name=None, group='/',file_type = 'hdf5'):
    """Read in an InfoArray from a disk file.
    Type load('?') to get a list of supported file types
    """
    valid_filetypes = ['hdf5','zemax','fits']
    basename,ext = os.path.splitext(filename)
    if ext[1:] in valid_filetypes:
        file_type = ext[1:]
    if filename in ['help','?','file_types?']:
        return valid_filetypes
    if not os.path.isfile(filename):
        raise Exception,'file %s does not exist'%filename
    if name is None and file_type != 'fits':
        raise Exception,'<load> name must be provided'
    if file_type == 'hdf5':
        f = h5py.File(filename,'r')
        top = f[group]
        data = top[name]['data'].value
        meta = top[name]['metadata'].value
        f.close()
        # parse the metadata
        ml = [[y.strip() for y in x.split(':')] for x in meta.split(',')]
        d = {}
        for key,val in ml:
            try:
                val = float(val)
            except:
                val = val
            d[key.strip()] = val
        
        return InfoArray(data,**d)
    elif file_type == 'zemax':
        r = subprocess.call(['dos2unix',filename])
        f = open(filename,'r')
        lines = f.read()
        f.close()
        lines = lines.split('\n')
        
        # build up the header
        hdr = {}
        hdr['name'] = name
        hdr['explanation'] = lines[0]
        hdr['filename'] = lines[2].split(' : ')[1].strip()
        hdr['date'] = lines[4].split(' : ')[1].strip()
        # line 9 has dx
        line = lines[9].split()
        hdr['dx'] = float(line[3])
        hdr['dx_units'] = line[4][:-1].decode('utf8')
        
        # read the data. it starts at line 21 and ends at the second to last line
        rows = []
        for line in lines[21:-1]:
            row = map(float,line.split())
            rows.append(row)
        return InfoArray(rows,**hdr)
    elif file_type == 'fits':
        hdu = pyfits.open(filename)[0]
        data,hdr = hdu.data,hdu.header
        r = InfoArray(data,**hdr)
        keys = hdr.keys()
        for key in ['NAME','UNITS','DX','DX_UNITS']:
            kl = key.lower()
            if kl in r.__dict__:
                if not key.endswith('_UNITS'):
                    r.__dict__[kl] = hdr[key]
                else:
                    key = key[:-6]
                    r.__dict__[kl] = hdr.comments[key]
        if name is not None:
            r.name = name
        return r
    else:
        raise ValueError, '%s is not a supported file_type'%file_type

def whatsin(filename):
    """List the directory of an hdf file.
    """
    def printname(name):
        print name
    f = h5py.File(filename,'r')
    f.visit(printname)
    f.close()
    
test_oft = """
import info_array
reload(info_array)
InfoArray = info_array.InfoArray
import numpy as np
n = 256
a = np.zeros((n,n))
a = InfoArray(a,name='a',units='microns',dx=0.1,dx_units='meters',wavelength=0.5,wavelength_units='microns')
p = a.oft(upsamp=2)

psf = a.oft()
mtf = psf.mtf()
ena = psf.ena()
print 'ENA = %0.6f %s'%ena
"""

depth = lambda L: isinstance(L, list) and max(map(depth, L))+1

def show(arg,nmax=4):
    """
    Display a list or grid of InfoArrays all on one figure.
    
    argument:
        arg = and InfoArray, list of InfoArrays, or list of lists of InfoArrays (2d grid)
    
    keyword argument:
        nmax = the maximum number of plots on a figure in each direction
    """
    if isinstance(arg,InfoArray):
        arg.show()
        return
    assert isinstance(arg,list),'argument must be an InfoArray or a list'
    d = depth(arg)
    assert d <= 2
    figSize = np.array(plt.rcParams['figure.figsize'])
    if d==1:
        ncols = min(len(arg),nmax)
        figSize[0] = figSize[0]*ncols
    else:        
        nrows = min(len(arg),nmax)
        ncols = max([len(row) for row in arg])
        ncols = min(ncols,nmax)
        figSize[0] = figSize[0]*ncols
        figSize[1] = figSize[1]*nrows

    fig = plt.figure(figsize=figSize*.8)
    fignum = fig.number
    
    if d==1:
        for k in range(ncols):
            n = k+1
            sub = '1%d%d'%(ncols,n)
            mods = {'fontsize.title':12,
                    'axislabel.right':False,
                    'axislabel.top':False}
            arg[k].plotParams.update(mods)
            arg[k].show(fig=fignum,sub=sub)
        plt.subplots_adjust(top=0.85,bottom=0.1, left=0.10,right=0.95,hspace=0.4,wspace=0.2)
    else:
        for row in range(nrows):
            ncols_this_row = min(len(arg[row]),nmax)
            for col in range(ncols_this_row):
                n = row*ncols + col + 1
                sub = '%d%d%d'%(nrows,ncols,n)
                mods = {'fontsize.title':12,
                        'axislabel.right':False,
                        'axislabel.top':False}
                arg[row][col].plotParams.update(mods)
                arg[row][col].show(fig=fignum,sub=sub)
        plt.subplots_adjust(top=0.92,bottom=0.1, left=0.10,right=0.95,hspace=0.4,wspace=0.)

test_code = """
import numpy as np
from info_array import InfoArray,show
import matplotlib.pyplot as plt

names = [['a','b'],['c','d'],['e']]
al = []
for row in names:
    sl = []
    for name in row:
        sl.append(InfoArray(np.random.normal(size=(10,10)),name=name))
    al.append(sl)

show(al)
show(al[0])
"""

class InfoMatrix(np.matrix):
    """
    A sub class of `numpy.matrix <http://docs.scipy.org/doc/numpy-1.10.1/reference/generated/numpy.matrix.html>`_, with useful additional attributes like **name** and **units**.

    (See `numpy array subclassing <http://docs.scipy.org/doc/numpy-1.10.1/user/basics.subclassing.html>`_)
        
    to use::
    
        a = InfoMatrix(np.zeros((2,2)),name='blah')
        a.units = ...
    
    InfoArrays are containers in that they can contain any number of attributes. Useful ones are:
    
    :ivar str name: The name of the array
    :ivar str units: The units of the values in the array
    :ivar float dx: The physical size of one pixel in the array
    :ivar str dx_units: The units of the pixel size
    :ivar list axis_names: A list of strings containing the axis names
        The first and second are the horizontal and vertical axes correspondingly.
        An optionall third is the radial (for radial average plots).
    
    """
    def __new__(cls, input_array, name='',**kwargs):
        obj = np.asarray(input_array).view(cls)
        if type(input_array) is InfoArray:
            copyattrs(input_array,obj)
            setattr(obj,'name',name)
                
        else:
            obj.name = name
            obj.units = 'arbitrary'

        obj.__dict__.update(kwargs)
        return obj
    
    def __array_finalize__(self, obj):
        if obj is None: return
        if isinstance(obj,InfoMatrix):
            copyattrs(obj,self)
        
    def copy(self):
        """Make a deep copy of the InfoMatrix
        """
        obj = InfoMatrix(self.view(np.ndarray).copy())
        copyattrs(self,obj)
        return obj
    
    def pprint(self,full=False):
        """Pretty-print the InfoMatrix. This consists
        of reporting on the object's attributes.
        
        :param boolean full: if True, **pprint** also prints out the contents of the array.
            Default is to print only the "header" (attributes) information.

        """
        print self._pprint(full=full)
        
    def _pprint(self,print_width=40,aslist=False,rshort=False,full=False):
        cr = '\n'
        bling = 50*'='
        rs = []
        rs.append(bling)
        if hasattr(self,'longName'):
            rs.append(self.longName)
        else:
            if hasattr(self,'name') and self.name is not None:
                rs.append(self.name)
        rs.append(str(type(self)))
        rs.append(bling)
        rs.append('shape: '+str(self.shape))
        if rshort:
            if aslist:
                return rs
            else:
                rs = '\n'.join(rs)
                return rs
        if full:
            rs.append(str(self))
        tab = ' '*4
        d = self.__dict__
        keys = sorted(d.keys())
        for key in keys:
            if key.endswith('_units'): continue
            val = d[key]
            units = None
            if isinstance(val,(str,unicode)): pv = "'"+val+"'"
            else: pv = str(val)
            if len(pv) > print_width:
                pv = str(val.__class__)
                if isinstance(val,(np.ndarray,np.matrix)):
                    pv += ' '+str(val.shape)
            if key+'_units' in keys:
                units = d[key+'_units']
            line = key+':'+tab+pv
            if units is None:
                pass
            else:
                line += ' '+units
            if isinstance(val,(InfoArray,InfoMatrix)):
                if (hasattr(val,'longName')):
                    line += " '"+val.longName+"'"
                else:
                    line += " '"+val.name+"'"
            else:
                pass
            rs.append(line)
        rs.append(bling)
        if aslist:
            return rs
        else:
            rs = '\n'.join(rs)
            return rs
       
    def plot(self,kind='image',fontsize=14,grid=True,oplot=False,scale='lin',fuzz=1e-9,**kwargs):
        """Display the InfoMatrix data as an image or lineout plot
        
        :param str kind: plot kind: 'image','lineout',or 'radial'
        :param int fontsize: for the titles, axis labels, and tick labels
        :param boolean grid: draw axis grid
        :param boolean oplot: whether or not to plot over a prevous graph (only for line plots)
        :param str scale: plot scale: 'lin','sqrt','log','loglog'
        :param float fuzz: a minimum value for log scale 
                    to keep the image contrast reasonable
                    (used only for 'image', scale='log')
        :param **kwargs: is sent on to dimg.show in the kind='image' case
        """
        scales = ['lin','sqrt','log','loglog']
        assert scale in scales,'scale must be one of '+scales
        n,m = self.shape
        if isinstance(self,np.matrix):
            valid_kinds = ['image']
            necessary_keys = set(['name'])
        else:
            valid_kinds = ['image','lineout','radial']
            necessary_keys = set(['units','dx','dx_units','name'])
        assert kind in valid_kinds,'kind must be one of '+valid_kinds
        keys = self.__dict__.keys()
        assert necessary_keys.issubset(set(keys)),'Object must have attributes '+str(list(necessary_keys))
        if hasattr(self,'longName'):
            name = self.longName
        else:
            name = self.name
        if isinstance(self,np.matrix):
            x0,y0 = 0,0
            if (hasattr(self,'axis_names')):
                xlabel = self.axis_names[1]
                ylabel = self.axis_names[0]
            else:
                xlabel = 'column index'
                ylabel = 'row index'
            origin = 'upper'
            xlim = [x0,x0+n]
            ylim = [y0+n,y0]
        else:
            dx = self.dx
            dx_units = self.dx_units
            x0,y0 = -(float(m)/2)*dx-dx/2, -(float(n)/2)*dx-dx/2
            origin = 'lower'
            xlim = [x0,x0+m*dx]
            ylim = [y0,y0+n*dx]
            if 'dy_units' in keys:
                dy_units = self.dy_units
            else:
                dy_units = self.dx_units
            if 'axis_names' in keys:
                xlabel = self.axis_names[0]+', '+dx_units
                ylabel = self.axis_names[1]+', '+dy_units
                if len(self.axis_names)>2:
                    rlabel = self.axis_names[2]+', '+dx_units
                else:
                    rlabel = dx_units
            else:
                xlabel = dx_units
                ylabel = dy_units
                rlabel = dx_units
        
        data = np.array(self)
        if np.iscomplex(data).any():
            print '<Object.plot> data is COMPLEX - showing the absolute value'
            data = np.abs(data)
            name = name+' (ABSOLUTE VALUE)'
        
        if not oplot and kind is not 'image':
            plt.figure()
        
        if len(self.units) > 0:
            name += ', '+self.units
        
        if kind == 'radial':
            name += ' radial average'
            x = np.arange(xlim[0],xlim[1],dx)
            y = np.arange(ylim[0],ylim[1],dx)
            x,y = np.meshgrid(x,y)
            r = np.sqrt(x**2+y**2)
            bins = np.arange(0,(n/2)*dx,dx)
            i = np.digitize(r.flatten(),bins)
            c = np.bincount(i)
            q = np.zeros(n/2+1)
            for j,y in zip(i,data.flatten()):
                q[j] += y
            q /= c
            q = q[:-1]
            plt.plot(bins,q)
            if not oplot:
                ax = plt.gca()
                ax.set_xlabel(rlabel,fontsize=fontsize)
                ax.set_ylabel(self.units,fontsize=fontsize)
                ax.tick_params(axis='both',which='major',labelsize=fontsize,direction='out',length=6,width=1,
                               labeltop=False,labelbottom=True,labelleft=True,labelright=False)
                plt.title(name,y=1.04)
            if scale == 'log':
                ax.set_yscale('log')
            if scale == 'loglog':
                ax.set_xscale('log')
                ax.set_yscale('log')
                
        if kind == 'lineout':
            y = data[n/2,:]
            x = np.arange(xlim[0],xlim[1],dx)
            plt.plot(x,y)
            if not oplot:
                ax = plt.gca()
                ax.set_xlabel(xlabel,fontsize=fontsize)
                ax.set_ylabel(self.units,fontsize=fontsize)
                ax.tick_params(axis='both',which='major',labelsize=fontsize,direction='out',length=6,width=1,
                               labeltop=False,labelbottom=True,labelleft=True,labelright=False)
                plt.title(name,y=1.04)
            if scale == 'log':
                ax.set_yscale('log')

        if kind == 'image':
            if scale == 'log':
                data = np.log10(np.clip(np.abs(data),fuzz,np.inf))
            if scale == 'sqrt':
                data = np.sqrt(np.abs(data))
            dimg.show(data,extent = xlim+ylim,origin=origin,title=name,**kwargs)
            ax = plt.gca()
            if not oplot:
                ax.set_xlabel(xlabel,fontsize=fontsize)
                ax.set_ylabel(ylabel,fontsize=fontsize)
                ax.tick_params(axis='both',which='major',labelsize=fontsize,direction='out',length=6,width=1,
                               labeltop=True,labelbottom=True,labelleft=True,labelright=True)
                plt.title(name,y=1.08)

        if not oplot:
            ax.tick_params(axis='both',which='minor',direction='out',length=4,width=1)
            plt.minorticks_on()
        
        plt.grid(grid)
        plt.draw()
        
    def graph(self,**kwargs):
        kwargs['kind'] = 'lineout'
        self.plot(**kwargs)
        
    def display(self,**kwargs):
        kwargs['kind'] = 'image'
        self.plot(**kwargs)
        
    def show(self,**kwargs):
        self.plot(**kwargs)

def test():
    a = InfoArray([[1.,2],[3,4]],name='Test',dx=1,dx_units='arbitrary')
    a.units = 'integers'
    a.pprint()
    a.show()
    ac = a.copy()
    ac[0,0] = 2.
    assert ((ac - a) == InfoArray([[1.,0],[0,0]])).all()
    
    b = InfoMatrix([[1.,2],[3,4]],name='TestMatrix')
    b.units = 'integers'
    b.pprint()
    b.show()
    
    