# read and display a fits file
import os
import sys
import numpy as np
import pyfits
import time
import warnings

def readfits(filename,verbose=False,raiseError=True,isHST=False,return_header=False):
    """Reads a FITS file from disk given the file name."""
    if (verbose):
        print '<readfits.readfits> reading file '+filename + '...',
        sys.stdout.flush()
    if (os.path.isfile(filename) == False):
        err_str = "<readfits.readfits> no such file "+filename
        if (raiseError):
            raise IOError(err_str)
            return
        warnings.warn(err_str)
        return np.array([0.])
    hdulist = pyfits.open(filename)
    if (isHST):
        data = hdulist[1].data
        hdr = hdulist[1].header
    else:
        data = hdulist[0].data
        hdr = hdulist[0].header
    hdulist.close()
    if (verbose):
        print 'done'
    if (return_header):
        return data,hdr
    return data

def writefits(data,filename,header=None,protect=False,comment=None,verbose=False):
    """Writes a FITS file given the data.
    arguments:
        data - a numpy array (1, 2 or 3d)
        filename - full name of the file to write to
    keywords:
        hdr - a list of tuples that will be appended as header entries
            these are (keyword,value,[comment]) tuples
        protect - avoid clobering an existing file with the same name
        comment - a single comment to append to the header
        verbose - print progress to the terminal
    """

    if (os.path.isfile(filename) == True):
        if (protect):
            protectFile(filename,verbose=verbose)
        else:
            err_str = "<readfits.writefits> won't over write existing file "+filename + ". Try the protect=True keyword."
            raise IOError(err_str)
            return
    if (verbose):
        print '<readfits.writefits> writing file '+filename + '...',
        sys.stdout.flush()
    tl = time.localtime(time.time())
    day = time.strftime('%Y-%m-%d',tl)
    tim = time.strftime('%H%M%S',tl)
    hdu = pyfits.PrimaryHDU(data)
    if (isinstance(header,pyfits.header.Header)):
        hdu.header = header
    if (isinstance(header,list)):
        for h in header:
            hdu.header.append(h,end=True)
    hdu.header.append(('COMMENT','------ fits writer info -------'),end=True)
    hdu.header.append(('DATE',day,'File generation date'),end=True)
    hdu.header.append(('TIME',tim,'file generation time hhmmss'),end=True)
    hdu.header.append(('GENER','readfits.py','writer code'),end=True)
        
    if (comment is not None):
        hdu.header.append(('comment',str(comment)),end=True)
    hdu.writeto(filename)
    if (verbose):
        print 'done'

def protectFile(filename,verbose=False):
    """Protect an existing file by putting it into an
    archive subdirectory and appending a datetime stamp to the name
    """
    if (os.path.isfile(filename)):
        dirname = os.path.dirname(filename)
        basename = os.path.basename(filename)
        archivedir = os.path.join(dirname,'archive')
        if (not os.path.exists(archivedir)):
            os.mkdir(archivedir)
        protectedName = os.path.join(archivedir,basename)+'.'+time.strftime('%Y%m%d%H%M%S')
        if (verbose):
            print '<readfits.protectFile> protecting file '+filename + ' to '+protectedName,
            sys.stdout.flush()            
        os.rename(filename,protectedName)
        if (verbose):
            print 'done'
