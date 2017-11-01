"""
img.py

Image processing routines
"""
import numpy as np

try:
    import scipy.special
    import scipy.interpolate
    import scipy.ndimage
    from scipy.special import jn
    no_scipy = False
except ImportError:
    no_scipy = True # but proceed anyway - some functions are disabled

def circle(shape,c=None,r=None):
    """circle(shape,c=None,r=None)
    Generate a 2-d image with a disk of ones inside radius r and centered at c, zero outside
    
    c = a tuple of the x,y center position of the center of the circle, in pixels
    r = a scalar radius of the circle, in pixels
    """
    if (c is None):
        c = np.array(shape)/2.
    y = np.arange(shape[0]).astype('float') - float(c[0])
    x = np.arange(shape[1]).astype('float') - float(c[1])

    if (r is None):
        r = min(np.array(shape))/2.
    x = x/float(r)
    y = y/float(r)
    x,y = np.meshgrid(x,y)
    r = np.sqrt(x**2+y**2)
    result = np.where(r<1,1.,0.)
    return result

def supergauss(shape,rad,c=None,pow=10):
    """Generate a super-gaussian mask:
    e^(-r^10)
    """
    x1 = np.arange(shape[0])
    y1 = np.arange(shape[1])
    x,y = np.meshgrid(x1,y1)
    if (c is None):
        c = (shape[0]/2,shape[1]/2)
    x -= c[0]
    y -= c[1]
    r = np.sqrt(x**2+y**2)/rad
    u = np.exp(-r**pow)
    return u

def gauss2(shape,s,c=None):
    """gauss2(shape,sd,c=None)
    Generate a Gaussian shaped 2-d bump, centered at c and with width (std dev) sd
    
    c = a tuple of the x,y center position of the Gaussian bump, in pixels
    sd = the standard deviation (1/e point) of the Gaussian bump, in pixels
        - sd can be a scalar, in which case it applies to both axes with corellation coeficent zero
        -or- a tuple of 2 elements in which case it indicates widths in each axis woth corellation coefficient zero
        -or- a tuple of 3 elements in which case it represents the elliptical orientation:
            standard deviations in the major axes and the rotation angle in radians
        -or- a 2x2 matrix, in which case it represents the Information matrix
    """
    if (c is None):
        c = np.array(shape)/2.
    x = np.arange(shape[0]).astype('float') - float(c[0])
    y = np.arange(shape[1]).astype('float') - float(c[1])

    x,y = np.meshgrid(x,y)
    F = None
    
    type_s = str(type(s))
    valid_matrix_types = ["<type 'numpy.ndarray'>","<class 'numpy.core.defmatrix.matrix'>","<class 'numpy.matrixlib.defmatrix.matrix'>"]
    if (type(s) in (tuple,list)):
        sx = float(s[0])
        sy = float(s[1])
        if (len(s) == 2):
            theta = 0.
        else:
            theta = s[2]
    elif (type_s in valid_matrix_types):
        if (s.shape == (2,2)):
            F = np.matrix(s)
        else:
            return None
    else: # assume its a scalar
        sx = float(s)
        sy = float(s)
        theta = 0.
    
    # now form the Information matrix
    if (F is None):
        C = np.matrix(np.zeros((2,2)))
        C[0,0] = sx**2
        C[1,1] = sy**2
        R = np.matrix([[np.cos(theta),-np.sin(theta)],[np.sin(theta),np.cos(theta)]])
        F = (R.T*C*R).I
    
    r2 = F[0,0]*x**2 + 2*F[0,1]*x*y + F[1,1]*y**2
    result = np.exp(-r2)
    return result

def circle_backup(shape,center,radius):
    n,m = shape
    x = range(n)
    y = range(m)
    xx,yy = np.meshgrid(x,y,indexing='ij')
    r = np.sqrt((xx-center[0])**2 + (yy-center[1])**2)
    result = (r < radius).astype(float)
    return result

def depiston(image,ap=None):
    """Remove the piston component, or piston component
    within an aperture, from an image
    """
    assert image.ndim >= 2
    if (ap is None):
        ap = np.ones(n,m)
    if image.ndim == 2:
        n,m = image.shape
        piston = np.sum(image*ap)/np.sum(ap)
        result = image - piston
        return result
    else:
        s = image.shape
        ni = np.product(s[:-2])
        image = image.reshape(ni,s[-2],s[-1])
        piston = np.sum(image*ap,axis=0)/np.sum(ap)
        result = image - piston
        result = result.reshape(s)
        return result

def detilt(image,ap=None):
    """Remove the tilt component, or the tilt component
    on an aperture, from an image
    """
    n,m = image.shape
    if (ap is None):
        ap = np.ones(n,m)
    x = np.arange(n)-n/2
    y = np.arange(m)-m/2
    xx,yy = np.meshgrid(x,y)
    xx = xx - np.sum(xx*ap)/np.sum(ap)
    yy = yy - np.sum(yy*ap)/np.sum(ap)
    tx = np.sum(xx*image*ap)/np.sum(xx*xx*ap)
    ty = np.sum(yy*image*ap)/np.sum(yy*yy*ap)
    result = image - (xx*tx + yy*ty)
    return result

def planeFit(image,ap=None):
    """Determine the plane that fits the image, over an aperture
    Returns the plane fit and the piston, tilt-x, and tilt-y components, in a tuple
    """
    n,m = image.shape
    if (ap is None):
        ap = np.ones(n,m)
    piston = np.sum(image*ap)/np.sum(ap)
    x = np.arange(n)-n/2
    y = np.arange(m)-m/2
    xx,yy = np.meshgrid(x,y)
    xx = xx - np.sum(xx*ap)/np.sum(ap)
    yy = yy - np.sum(yy*ap)/np.sum(ap)
    tx = np.sum(xx*(image-piston)*ap)/np.sum(xx*xx*ap)
    ty = np.sum(yy*(image-piston)*ap)/np.sum(yy*yy*ap)
    p = (piston + xx*tx + yy*ty)
    return (p,piston,tx,ty)

def rms(image,ap):
    """Computes the root-mean-square of an image, over an aperture
    """
    n,m = image.shape
    if (ap is None):
        ap = np.ones(n,m)
    u = depiston(image,ap)
    result = np.sqrt(np.sum(u*u*ap)/np.sum(ap))
    return result

def zeropad(u,n=None,pad=None):
    """
    r = zeropad(u,n)
    
    Zero-pad the array by centering it in a larger
    array and padding with zeros
    
    u - original array
    n - size of new array (2-tuple)
    pad - added size of new array, so size of new array is size of
           the original array with a 'pad' size buffer all around
    """
    n0 = np.array(u.shape)
    if n is not None:
        n = np.array(n)
    if pad is not None:
        n = u.shape + 2*np.array(pad)
    broadcast = False
    if (len(n0) > 2):
        broadcast = True
        n0 = n0[-2:]
    assert (n0<=n).all()
    d = (n-n0)/2
    d2 = (n-n0) - d
    p = ((d2[0],d[0]),(d2[1],d[1]))
    if broadcast:
        r = []
        for uu in u:
            r.append(np.pad(uu,p,'constant',constant_values=0))
        r = np.array(r)
    else:
        r = np.pad(u,p,'constant',constant_values=0)
    return r

def shift(im,s):
    """
    shift the 1-d or 2-d image by the amounts in the s tuple,
    s[0] is the shift in 'x' (columns) and s[1] is the shift in 'y' (rows)
    """
    if (isinstance(s, int)):
        s = (s,)
    ndim = len(s)
    assert (ndim > 0 and ndim <= 2)
    if (ndim == 1):
        r = np.roll(im,s[0])
    if (ndim == 2):
        r = np.roll(im,s[0],axis=1)
        r = np.roll(r,s[1],axis=0)
    return r

def blur(a,p,kernelType='block'):
    """blur an image by a PSF or by a kernel block
    kernelType can be 'block', 'circle', 'Gaussian' or 'Airy'
    
    if kernelType is 'PSF' then p must be an image
    and a convolution is performed
    if kernelType is 'block' then p must be an
    integer, and the kernel is then a pxp block
    if kernelType is 'circle' then p
    represents the diameter of a circular kernel
    if kernelType is 'Gaussian' or 'Airy' then the
    appropriate kernel is generated, with p representing
    in the Gaussian case standard deviation,
    and in the Airy case, the distance from center to
    first Airy null.
    'block', 'Gaussian', and 'Airy' blur functions
    are normalized to preserve flux
    """
    n,m = a.shape[-2:]
    assert kernelType in ['PSF','block','Gaussian','Airy','circle']
    if (kernelType == 'PSF'):
        b = p
        nb,mb = b.shape
        assert (nb<=n and mb<=m)
    if (kernelType == 'block'):
        assert isinstance(p,int)
        nb,mb = p,p
        b = np.ones((nb,mb))
        b = b/np.sum(b)
    if (kernelType == 'circle'):
        b = circle((n,m),(n/2,m/2),p)
        b = b/np.sum(b)
    if (kernelType == 'Gaussian'):
        b = gauss2((n,m),p,(n/2,m/2))
        b = b/np.sum(b)
        nb,mb = n,m
    if (kernelType == 'Airy'):
        b = airy(n,m,p)
        b = b/np.sum(b)
        nb,mb = n,m
    c = convolve(a,b)
    return c

def convolve(a,b,is_complex=False):
    """convolve data a with kernel b
    using the Fourier transfomrm method
    Assumes data sets are 2d arrays and (0,0)
    is at the center of the array
    """
    n,m = a.shape[-2:]
    nb,mb = b.shape
    assert nb<=n and mb<=m
    if (nb<n or mb<m):
        b = zeropad(b,(n,m))
    a_f = np.fft.fft2(a)
    b = np.fft.ifftshift(b)
    b_f = np.fft.fft2(b)
    c_f = a_f*b_f
    c = np.fft.ifft2(c_f)#/(float(n)*float(m))
    if not is_complex:
        c = np.real(c)
    return c

def airy(n,m,s,s2=None):
    """
    PSF of a circular aperture
    args:
        n,m = size of array
        s = distance in pixels to the first Airy null
    keyword args:
        s2 = secondary Airy null - used for the case of a secondary obscuration
        
    returns:
        the (annular) airy function, computed analytically, and normalized to peak = 1.
        
    examples:
    
        p = airy(n,n,1.22*(lambda/d)/pixelscale)
        p2 = airy(n,n,1.22*(lamda/dp)/pixelscale, s2 = 1.22*(lambda/ds)/pixelscale)
    """
    xx = np.arange(n) - n/2
    yy = np.arange(m) - m/2
    x,y = np.meshgrid(xx,yy)
    r = np.sqrt(x**2+y**2)
    r = np.clip(r,1.e-12,r.max())
    a = 1.219669891266504 # first zero of j1 is at a*pi
    f = jn(1,a*r/s*np.pi)/r
    norm_factor = 2./(a*np.pi/s) # normalizes to peak = 1.0
    if s2 is not None:
        f -= (s/s2)*jn(1,a*r/s2*np.pi)/r # to subtract the secondary diffraction, it must be normalized by area
        norm_factor *= 1./((s/s2)**2-1.) # and the peak-normalzing factor adjusted
    f *= norm_factor
    ret = f**2
    return ret

def ft(a):
    """2-D centered fast-Fourier transform
    """
    return np.fft.fftshift(np.fft.fft2(np.fft.fftshift(a)))

def ftinv(a):
    """2-D centered inverse fast-Fourier transform
    """
    return np.fft.ifftshift(np.fft.ifft2(np.fft.ifftshift(a)))

def ftconvolve(a,b,space='sss'):
    """2-D centered fast-Fourier convolve
    
    result = a (*) b
    space - tell the domain of the data or result, 's' = spatial, 'f' = fourier
        It must be 3 characters, refering to a,b, and result
        For exammple: space = 'fss' says a is already transformed, b is not,
        and the returned result should be in the spatial domain
    """
    if space[0] == 's':
        fa = ft(a)
    else:
        fa = a
    if space[1] == 's':
        fb = ft(b)
    else:
        fb = b
    fc = fa*fb
    if space[2] == 's':
        return ftinv(fc)
    else:
        return fc

class units:
    arcsec = np.pi/(180.*3600.)
    nm = 1.e-9 
    micron = 1.e-6 

def nextpow2(n):
    k = 0
    n2 = 2**k
    while n2 < n:
        k += 1
        n2 = 2**k
    return n2

def psfwf(mag,phase,pad=0):
    """compute the PSF for an aberrated wavefront
    given the magnitude (or aperture) and phase
    """
    n,m = phase.shape
    assert (n,m) == mag.shape
    
    if (pad > 0):
        nn = nextpow2(n*2**pad)
    else:
        nn = n
    
    wf = mag*np.exp(1j*phase)
    wf = zeropad(wf,(nn,nn))
    wf = np.fft.fftshift(wf)
    p = np.fft.fft2(wf)/float(nn)
    p = np.fft.fftshift(p)
    if (n < nn):
        p = crop(p,(nn/2,nn/2),(n,n))
    return np.abs(p)**2    

def psf(n,dp,ds,lam,pixelscale,pad=0,center=None):
    """
    PSF of a circular aperture with a secondary obscuration
    
    args:
        n,n = size of array
        dp, ds = diameter of primary and secondary in meters
        lam = wavelength, meters
        pixelscale = size of pixel, in radians
    
    keyword args:
     pad: pad in the aperture domain, which reduces the 'Fourier noise' in the focal domain result,
        at the cost of requiring more compute time to calculate.
        The pad factor is the exponent of two in the padding, i.e. pad=1 implies pad the array
        by a factor of 2, pad=3 pads by a factor of 8, etc.
     center: center the psf at this pixel. can be a fractional pixel. pixels are numbered
        0 to (n-1). pixel k's continuous coordinate range is k to k+1.
        the default center is n/2+0.5, which is the center of pixel n/2

    returns:
        the PSF, normalized so integral = 1.
    
    """
    if (pad > 0): 
        nn = nextpow2(n*2**pad)
    else:
        nn = n
    c0 = np.array([n/2+0.5,n/2+0.5])
    if (center is None):
        center = c0
    s = np.array(center) - c0
    
    # create a pupil
    dx = pixelscale
    du = lam/(nn*dx)
    ap = circle((nn,nn),(nn/2,nn/2),dp/du/2.)
    if (ds > 0):
        ap -= circle((nn,nn),(nn/2,nn/2),ds/du/2.)
    mag = ap/np.sqrt(np.sum(ap*ap))
    
    # incorporate a phase factor on the aperture to do the fractional pixel shift
    u = np.arange(0,nn) - nn/2
    u,v = np.meshgrid(u,u)
    ph = 2*np.pi * (s[0]*u + s[1]*v) * ap / float(nn)
    wf = mag * np.exp(1j*ph)
    
    # transform to get the PSF
    wf = np.fft.fftshift(wf)
    p = np.fft.fft2(wf)/float(nn)
    p = np.fft.fftshift(p)
    if (n < nn):
        p = crop(p,(nn/2,nn/2),(n,n))
    return np.abs(p)**2

def crop(z,center,size,fill=0.):
    """crop a 2D image to size
    """
    n,m = size
    nn,mm = z.shape
    w = np.zeros((n,m)) + fill
    ll = center[0] - n/2
    rr = ll + n
    bb = center[1] - m/2
    tt = bb + m
    l = 0
    r = n
    b = 0
    t = m
    if ll < 0:
        d = abs(ll)
        l += d
        ll += d
    if rr >= nn:
        d = rr - nn + 1
        r -= d
        rr -= d
    if bb < 0:
        d = abs(bb)
        b += d
        bb += d
    if tt >= mm:
        d = tt - mm + 1
        t -= d
        tt -= d
    w[ l:r, b:t ] = z[ ll:rr, bb:tt ]
    return w

def insert(im,a,p,action='add'):
    """insert a small image im into a larger array a at position p.
    im: small image to insert
    a: bigger image into which to insert the smaller image
    p: center position in a at which to insert im's center
    action can be 'add' or 'replace'
    """
    n,m = im.shape
    na,ma = a.shape
    pll = [p[0]-n/2,p[1]-m/2]
    pur = [pll[0]+n,pll[1]+m]
    qll = [0,0]
    qur = [n,m]
    for k,lim in zip([0,1],[na,ma]):
        if pll[k] < 0:
            d = abs(pll[k])
            pll[k] += d
            qll[k] += d
        if pur[k] >= lim:
            d = pur[k]-lim + 1
            pur[k] -= d
            qur[k] -= d
        if pll[k] >= pur[k]:
            return a
    if action == 'add':
        a[pll[0]:pur[0],pll[1]:pur[1]] += im[qll[0]:qur[0],qll[1]:qur[1]]
    elif action == 'replace':
        a[pll[0]:pur[0],pll[1]:pur[1]] = im[qll[0]:qur[0],qll[1]:qur[1]]

    return a

def rebin(a, shape):
    '''rebin ndarray data into a smaller ndarray of the same rank whose dimensions
    are factors of the original dimensions. eg. An array with 6 columns and 4 rows
    can be reduced to have 6,3,2 or 1 columns and 4,2 or 1 rows.
    example usages:
    >>> a=rand(6,4); b=rebin(a,3,2)
    >>> a=rand(6); b=rebin(a,2)

    Reference: http://wiki.scipy.org/Cookbook/Rebinning
    http://stackoverflow.com/questions/8090229/resize-with-averaging-or-rebin-a-numpy-2d-array
    '''
    sh = shape[0],a.shape[0]//shape[0], shape[1],a.shape[1]//shape[1]
    return a.reshape(sh).mean(-1).mean(1)

global newcoords
global newcoords_dims

def congrid(a, newdims, method='linear', centre=False, minusone=False):
    '''Arbitrary resampling of source array to new dimension sizes.
    Currently only supports maintaining the same number of dimensions.
    To use 1-D arrays, first promote them to shape (x,1).
    
    Uses the same parameters and creates the same co-ordinate lookup points
    as IDL''s congrid routine, which apparently originally came from a VAX/VMS
    routine of the same name.

    method:
    neighbour - closest value from original data
    nearest and linear - uses n x 1-D interpolations using
                         scipy.interpolate.interp1d
    (see Numerical Recipes for validity of use of n 1-D interpolations)
    spline - uses ndimage.map_coordinates

    centre:
    True - interpolation points are at the centres of the bins
    False - points are at the front edge of the bin

    minusone:
    For example- inarray.shape = (i,j) & new dimensions = (x,y)
    False - inarray is resampled by factors of (i/x) * (j/y)
    True - inarray is resampled by(i-1)/(x-1) * (j-1)/(y-1)
    This prevents extrapolation one element beyond bounds of input array.
    
    Reference: http://wiki.scipy.org/Cookbook/Rebinning
    '''
    global newcoords
    global newcoords_dims
    if not a.dtype in [np.float64, np.float32]:
        a = np.cast[float](a)

    m1 = np.cast[int](minusone)
    ofs = np.cast[int](centre) * 0.5
    old = np.array( a.shape )
    ndims = len( a.shape )
    if len( newdims ) != ndims:
        print "[congrid] dimensions error. " \
              "This routine currently only support " \
              "rebinning to the same number of dimensions."
        return None
    newdims = np.asarray( newdims, dtype=float )
    dimlist = []

    if method == 'neighbour':
        for i in range( ndims ):
            base = np.indices(newdims)[i]
            dimlist.append( (old[i] - m1) / (newdims[i] - m1) \
                            * (base + ofs) - ofs )
        cd = np.array( dimlist ).round().astype(int)
        newa = a[list( cd )]
        return newa

    elif method in ['nearest','linear']:
        # calculate new dims
        for i in range( ndims ):
            base = np.arange( newdims[i] )
            dimlist.append( (old[i] - m1) / (newdims[i] - m1) \
                            * (base + ofs) - ofs )
        # specify old dims
        olddims = [np.arange(i, dtype = np.float) for i in list( a.shape )]

        # first interpolation - for ndims = any
        mint = scipy.interpolate.interp1d( olddims[-1], a, kind=method )
        newa = mint( dimlist[-1] )

        trorder = [ndims - 1] + range( ndims - 1 )
        for i in range( ndims - 2, -1, -1 ):
            newa = newa.transpose( trorder )

            mint = scipy.interpolate.interp1d( olddims[i], newa, kind=method )
            newa = mint( dimlist[i] )

        if ndims > 1:
            # need one more transpose to return to original dimensions
            newa = newa.transpose( trorder )

        return newa
    elif method in ['spline']:
        oslices = [ slice(0,j) for j in old ]
        oldcoords = np.ogrid[oslices]
        nslices = [ slice(0,j) for j in list(newdims) ]
        newcoords = np.mgrid[nslices]

        newcoords_dims = range(np.ndim(newcoords))
        #make first index last
        newcoords_dims.append(newcoords_dims.pop(0))
        newcoords_tr = newcoords.transpose(newcoords_dims)
        # makes a view that affects newcoords

        newcoords_tr += ofs

        deltas = (np.asarray(old) - m1) / (newdims - m1)
        newcoords_tr *= deltas

        newcoords_tr -= ofs

        newa = scipy.ndimage.map_coordinates(a, newcoords)
        return newa
    else:
        print "Congrid error: Unrecognized interpolation type.\n", \
              "Currently only \'neighbour\', \'nearest\',\'linear\',", \
              "and \'spline\' are supported."
        return None
    
def minmax(a):
    """Return the minimum and maximum of an array as a 2-vector
    """
    return a.min(),a.max()

def centroid(z,ap=None):
    """Find the centroid of data
    
    inputs:
        z - a 2-D array
    
    keyword arguments:
        ap - an aperture over which to compute the centroid
    
    returns:
        the centroid, in pixel units, with 0,0 defined as the lower-left of the 0,0 pixel
        (pixel k spans the continuum range from k to k+1)
    """
    n,m = z.shape
    x = np.arange(n)+0.5 # half-pixel shift. e.g. 0,0 pixel = 1 centroids to position 0.5,0.5
    x,y = np.meshgrid(x,x)
    if (ap is None):
        ap = np.ones((n,m))
    zap = z*ap
    zap /= np.sum(zap)
    cx = np.sum(x*zap)
    cy = np.sum(y*zap)
    return cx,cy

def azimuthalAverage(image, center=None, stddev=False, returnradii=False, return_nr=False, 
        binsize=3., weights=None, steps=False, interpnan=False, left=None, right=None):
    """
    https://code.google.com/p/agpy/source/browse/trunk/agpy/radialprofile.py?r=317
    
    Calculate the azimuthally averaged radial profile.

    image - The 2D image
    center - The [x,y] pixel coordinates used as the center. The default is 
             None, which then uses the center of the image (including 
             fractional pixels).
    stddev - if specified, return the azimuthal standard deviation instead of the average
    returnradii - if specified, return (radii_array,radial_profile)
    return_nr   - if specified, return number of pixels per radius *and* radius
    binsize - size of the averaging bin.  Can lead to strange results if
        non-binsize factors are used to specify the center and the binsize is
        too large
    weights - can do a weighted average instead of a simple average if this keyword parameter
        is set.  weights.shape must = image.shape.  weighted stddev is undefined, so don't
        set weights and stddev.
    steps - if specified, will return a double-length bin array and radial
        profile so you can plot a step-form radial profile (which more accurately
        represents what's going on)
    interpnan - Interpolate over NAN values, i.e. bins where there is no data?
        left,right - passed to interpnan; they set the extrapolated values

    If a bin contains NO DATA, it will have a NAN value because of the
    divide-by-sum-of-weights component.  I think this is a useful way to denote
    lack of data, but users let me know if an alternative is prefered...
    
    """
    # Calculate the indices from the image
    n,m = image.shape
    y, x = np.indices(image.shape)

    if center is None:
        center = np.array([float(n/2),float(m/2)])
        #center = np.array([(x.max()-x.min())/2.0, (y.max()-y.min())/2.0])

    r = np.hypot(x - center[0], y - center[1])

    if weights is None:
        weights = np.ones(image.shape)
    elif stddev:
        raise ValueError("Weighted standard deviation is not defined.")

    # the 'bins' as initially defined are lower/upper bounds for each bin
    # so that values will be in [lower,upper)  
    nbins = (np.round(r.max() / binsize)+1)
    maxbin = nbins * binsize
    bins = np.linspace(0,maxbin,nbins+1)
    # but we're probably more interested in the bin centers than their left or right sides...
    bin_centers = (bins[1:]+bins[:-1])/2.0
    
    # Find out which radial bin each point in the map belongs to
    whichbin = np.digitize(r.flat,bins)
    
    # how many per bin (i.e., histogram)?
    # there are never any in bin 0, because the lowest index returned by digitize is 1
    nr = np.bincount(whichbin)[1:]

    # recall that bins are from 1 to nbins (which is expressed in array terms by arange(nbins)+1 or xrange(1,nbins+1) )
    # radial_prof.shape = bin_centers.shape
    if stddev:
        radial_prof = np.array([image.flat[whichbin==b].std() for b in (np.arange(nbins)+1)]) #xrange(1,nbins+1)])
    else:
        radial_prof = np.array([(image*weights).flat[whichbin==b].sum() / weights.flat[whichbin==b].sum() for b in (np.arange(nbins)+1)]) #xrange(1,nbins+1)])

    #import pdb; pdb.set_trace()

    if interpnan:
        radial_prof = np.interp(bin_centers,bin_centers[radial_prof==radial_prof],radial_prof[radial_prof==radial_prof],left=left,right=right)

    if steps:
        xarr = np.array(zip(bins[:-1],bins[1:])).ravel() 
        yarr = np.array(zip(radial_prof,radial_prof)).ravel() 
        return xarr,yarr
    elif returnradii: 
        return bin_centers,radial_prof
    elif return_nr:
        return nr,bin_centers,radial_prof
    else:
        return radial_prof

def zoom(a,zoom_factor,shape=None,order=3,center=None):
    """Zoom the image by resampling to a different pixel scale.
    The routine wraps the scipy.ndimage.interpolation.zoom function
    but also allows for specifying the shape of the result image,
    which is either cropped or zeropadded to fit.
    
    Argument:
        a = the image
        zoom_factor = the ratio of the old dx to the new dx,
                      i.e. a 2:1 zoom takes old dx=1 to new dx=0.5
    
    Keyword:
        shape = None: return a reshaped array that fits the data (default)
                'same': returns an array the same shape as a
                2-tuple: a desired shape
    
    """
    n,m = a.shape
    nr,mr = [int(float(x)*zoom_factor) for x in a.shape] # this is the resulting shape
    if shape is None:
        shape = nr,mr
    elif shape is 'same':
        shape = n,m

    if center is None:
        center = (n/2,m/2)
    else: # imbed the image in a zero-padded enclosing rectangle centered on the new center
        nb,mb = [ 2*max(c,(nn-c)) for (nn,c) in zip(a.shape,center) ]
        x,y = [ max(0,nn-2*c) for (nn,c) in zip(a.shape,center) ]
        aa = np.zeros((nb,mb))
        aa[x:x+n,y:y+m] = a
        a = aa
        n,m = a.shape
    
    if shape[0] < nr or shape[1] < mr :  #zooming in to a desired shape that is smaller than the resulting shape
        subshape = [int(float(x)/zoom_factor) for x in shape]
        a = crop(a,(n/2,m/2),subshape)
    r = scipy.ndimage.zoom(a,zoom_factor,order=order)
    return r

def encircled_energy(a,pc,center=None,f='stop'):
    """Determined the radius of encircled energy for a PSF
    
    args:
        a - 2-D image
        pc - percentage (expreassed as a fraction, between 0 and 1)
        center - a 2-tuple or 2-list denoting the center pixel. If None, then the middle of the image is used
        f - failure flag - what to do if the encircled energy is not in the radius of the largest circle
            inscribed in the a array. Choices are:
                'stop' - raise an exception (ValueError)
                'nan' - return a NaN
                'max' - return the maximum radius = min(n,m)/2
                'zero' - return 0
                
    """
    n,m = a.shape
    icenter = np.array([n/2,m/2])
    if center is None:
        center = icenter
    else:
        center = np.array(center)
    sx,sy = icenter - center
    a = np.roll(np.roll(a,sx,1),sy,0)
    a = a/a.sum()
    x = np.arange(n)-n/2
    y = np.arange(m)-m/2
    x,y = np.meshgrid(x,y)
    r = np.sqrt(x**2+y**2)
    rv = None
    ee=[]
    for j in range(min(n,m)/2):
        e = np.sum(a*(r<j))
        ee.append(e)
        if pc is not 'all' and e > pc:
            rv = j-1 + (pc - ee[j-1])/(ee[j]-ee[j-1])
            break
    if pc is 'all':
        return np.array(ee)
    if rv is None:
        if f == 'stop':
            raise ValueError,'encircled energy radius not found'
        elif f == 'nan':
            return float('NaN')
        elif f == 'max':
            return min(n,m)/2.
        elif f == 'zero':
            return 0.
    return rv

# -------------------- Tests ---------------------------
def test():
    """Test the airy and psf routines
    """
    n = 256
    dp = 3.
    ds = 0.8
    lam = 1.6e-6
    pixelscale = 0.033*units.arcsec
    s = 1.219669891266504*(lam/dp)/pixelscale
    print '<test> computing a numerical PSF'
    u = psf(n,dp,0,lam,pixelscale,pad=4)
    u = u/u.max()
    print '<test> computing an analytic PSF'
    v = airy(n,n,s)
    print '<text> max difference: '+str(np.abs(u-v).max()) + ' (compare to 1.0 peak)'
    
def test2():
    """Test of crop and insert routines
    """
    global z,zc,zc2
    n = 4
    z = np.zeros((n,n))
    z[1:3,1:3] = 1.
    print z
    zc = crop(z,(2,2),(2,2))
    print zc
    a = np.zeros((n,n))
    a = insert(zc,a,(2,2),action='replace')
    print a
    #
    zc = np.ones((33,33))
    z = np.zeros((200,200))
    z = insert(zc,z,(100,100),action='replace')
    zc2 = crop(z,(100,100),(33,33))
    
