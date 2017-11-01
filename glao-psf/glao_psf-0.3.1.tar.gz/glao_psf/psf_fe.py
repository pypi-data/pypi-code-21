"""GLAO PSF generator front end

The front end acts to translate a run config file, or a run specification dictionary,
into a form that can drive a 'run'. The run involves calling the PSF generator
multiple times and saving each resulting PSF into a FITS file.
A pandas database is returned, and a csv file is written, that summarizes
the results of the run.

"""
import os
import sys
import argparse
import time
flush = sys.stdout.flush
import ConfigParser as cp
import psf as p
import numpy as np
import infoArray
import warnings
import platform
import matplotlib.pylab as plt
from matplotlib.backends.backend_pdf import PdfPages
import itertools
import flog
import pandas as pd
import shutil
from _version import __version__

default_args = {
    'ngs':3,
    'geom':'circle',
    'rot': 45.,
    'radius':6.,
    'profile':'Maunakea 13N median',
    'outer_scale':30.,
    'r0': '',
    'DM_conjugate': -280.,
    'actuator_spacing': 0.,
    'wavelength':0.5,
    'field_point': [(0.,0.), (2.5,0.), (4.,0.), (5.,0.)],
    'run_name':'rdata',
    'filename':'psf',
    'seeing_psf_filename':'psf0',
}    

def run(configFile=None,verbose=True,args=None,save_result=True):
    """ Generate a PSF using either the config file or a dictionary of args
    
    configFile = name of the config file. If it is None and args is None, then the
                 default config file distributed with the package is used
    args = a dictionary of arguments, containing parameters instead of looking in the config file.
            Only valid if configFile is None
    """
    global a
    
    t0 = time.time()
    
    #---------- get run parameters ------------

    param_tuples = [()]
    if args is not None: # get arguments from the passed-in dictionary, args
        assert configFile is None
        largs = default_args
        largs.update(args)
        iters = {}
        for key in largs:
            if isinstance(largs[key],list):
                iters[key] = largs[key]
            else:
                exec('%s = largs["%s"]'%(key,key))
        param_tuples = list(itertools.product(*iters.values()))
        param_names = iters.keys()
    
    else: # get arguments from the config file
        args = get_config(configFile,verbose=verbose)
        db = run(None,verbose,args,save_result)
        return db
            
    valid_profiles = p.available(show=False)
    profiles = args['profile']
    if not isinstance(profiles,list):
        profiles = [profiles]
    for profile in profiles:
        assert profile in valid_profiles, 'profile=%s not valid. profile must be one of %r'%(profile,valid_profiles)
    
    t1 = time.time()
    
    if save_result:
        run_name = args['run_name']
        can = Canister(run_name,filename,seeing_psf_filename)
    
    k,count = 0,len(param_tuples)
    if not verbose:
        progress_bar(k,count)
        
    if verbose:
        print '(%.3f sec)'%(t1-t0); t0=t1
        
    #---------- do PSF calculation -------
    
        print 'doing PSF calculation...',; flush()
    
    for param_tuple in param_tuples:  # loop over all the parameters specified as lists
        d = dict(zip(param_names,param_tuple))
        if len(d) > 0:
            if verbose:
                print d
            for key in d:
                exec('%s = d["%s"]'%(key,key))
        if isinstance(args['radius'],dict):  # radius follows field point
            fac,minradius = args['radius'].values()
            radius = np.sqrt(field_point[0]**2 + field_point[1]**2)
            radius = max( radius*fac, minradius)

        N = ngs
        kwargs = {'L0':outer_scale,'lam':wavelength,'sf_method':'new'}
        if r0 != '':
            kwargs['r0'] = r0
        a = p.Cn2_Profile(profile,**kwargs)
        n = 256
        c = p.Constellation(N,radius,'circle',rot=rot,field_point = field_point)
        r_lim = a.r0*n/8.
        a.make_S(c,r_lim=r_lim,n=n,dm_conjugate=DM_conjugate,wfs_conjugate=DM_conjugate, act_spacing = actuator_spacing)
        w = np.zeros(N+1)
        w[0] = -1
        w[1:] = np.ones(N)/float(N)
        a.make_PSF(w)
        
        speedup = a.PSF_seeing.ena / a.PSF.ena
        a.PSF.speedup = speedup

        #------------- save results --------------
        
        a.configFile = configFile
        if save_result:
            can.save(a,verbose=verbose)
        
        k += 1
        if not verbose:
            progress_bar(k,count)
    
    if not verbose:
        print 'done'
    
    if save_result:
        pwd = os.getcwd()
        os.chdir(os.path.join(pwd,can.run_name))
        flog.mkLog(keys='all')
        db = pd.read_csv('log.csv',';')
        os.chdir(pwd)
        shutil.copy(configFile,can.run_name)
    else:
        db = None
        
    t1 = time.time()
    if verbose:
        print '(%.3f sec)'%(t1-t0); t0=t1
    
    return db

class Canister(object):
    """A Canister object coordinates the storage of results data into a directory
    """
    
    def __init__(self,run_name,psf_basename,seeing_psf_basename):
        '''Create a directory to store results as fits files
        '''
        self.run_name = run_name
        emsg = "Sorry, a directory named %s already exists. For safety, it won't be overwritten"%run_name
        assert not os.path.exists(run_name), emsg
        os.mkdir(run_name)
        self.index = 0
        self.basename = psf_basename
        self.seeing_basename = seeing_psf_basename
        self.filetype = 'fits'
    
    def save(self,a,verbose=True):
        '''Save the results of a run()
        
        a = the Cn2_Profile containing the PSF results
        
        '''
        t0 = time.time()
        
        filename = os.path.join(self.run_name,'%s_%0.4d.fits'%(self.basename,self.index))
        seeing_psf_filename = os.path.join(self.run_name,'%s_%0.4d.fits'%(self.seeing_basename,self.index))
        
        if verbose:
            print 'saving results:'; flush()
            
        # keys from the profile object
        keys_a = ['name','site','tile','Cn2','Cn2_units','Cn2_bar',
                'databaseFile','databaseMetadata',
                'r0','r0_units','r00','r00_units','spatialFilter',
                'theta0','theta0_units',
                'L0','L0_units',
                'dm_conjugate','dm_conjugate_units',
                'wfs_conjugate','wfs_conjugate_units']
        transkey_a = {'name':'profile','databaseFile':'dbFile','databaseMetadata':'dbMeta'}
        
        # keys from the constellation object
        keys_c = ['N','field_point','geometry','radius','radius_units',
                  'rotation','rotation_units']
        
        # keys from the PSF_seeing object
        keys_p = ['ena','ena_r','ena_units','ena_r_units']
        transkey_p = {'ena':'ena_see','ena_r':'ena_r_se'}
        
        if a.spatialFilter is not False:
            keys_a += ['act_spacing']
        
        a.PSF.configFile = a.configFile
        a.PSF.configFile_units = 'config file for this run'
        a.PSF.version = __version__
        a.PSF.version_units = 'code version'
        
        hdu = a.PSF._hdu()
        hdr = hdu.header

        d = a.PSF_seeing.__dict__
        for key in keys_p:
            if not key.endswith('_units'):
                if key in transkey_p:
                    kwd = transkey_p[key]
                else:
                    kwd = key.upper()[:8]
                val = d[key]
                if key == 'spatialFilter' and not isinstance(val,bool):
                    val = True
                if isinstance(val,(tuple,list,np.ndarray)):
                    val = str(list(val))
                if isinstance(val,dict):
                    val = str(val)
                if isinstance(val,float):
                    val = ['Infinity',val][np.isfinite(val)]
                card = (kwd,val)
                if key+'_units' in keys_p:
                    cmt = d[key+'_units']+' (seeing)'
                    card = card + (cmt,)
                hdr.append(card,end=True)

        hdr.append(('COMMENT','--- Guide Star Constellation ---'),end=True)
        d = a.constellation.__dict__
        for key in keys_c:
            if not key.endswith('_units'):
                kwd = key.upper()[:8]
                val = d[key]
                if isinstance(val,(tuple,list,np.ndarray)):
                    val = str(str(val))
                if isinstance(val,dict):
                    val = str(val)
                if isinstance(val,float):
                    val = ['Infinity',val][np.isfinite(val)]
                card = (kwd,val)
                if key+'_units' in keys_c:
                    cmt = d[key+'_units']
                    card = card + (cmt,)
                hdr.append(card,end=True)
        d = a.__dict__
        hdr.append(('COMMENT','--- Atmosphere characteristics ---'),end=True)
        for key in keys_a:
            if not key.endswith('_units'):
                if key in transkey_a:
                    kwd = transkey_a[key]
                else:
                    kwd = key.upper()[:8]
                val = d[key]
                if key == 'spatialFilter' and not isinstance(val,bool):
                    val = True
                if isinstance(val,(tuple,list,np.ndarray)):
                    val = str(list(val))
                if isinstance(val,dict):
                    val = str(val)
                if isinstance(val,float):
                    val = ['Infinity',val][np.isfinite(val)]
                card = (kwd,val)
                if key+'_units' in keys_a:
                    cmt = d[key+'_units']
                    card = card + (cmt,)
                hdr.append(card,end=True)
            
        if verbose:
            print '    %s'%filename
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore',module='pyfits')
            hdu.writeto(filename,clobber=True)
        
        a.PSF_seeing.configFile = a.configFile
        a.PSF_seeing.configFile_units = 'config file for this run'
        a.PSF_seeing.version = __version__
        a.PSF_seeing.version_units = 'code version'

        a.PSF_seeing.profile = a.profile
        a.PSF_seeing.Cn2 = str(list(a.Cn2))
        a.PSF_seeing.L0 = ['Infinity',a.L0][np.isfinite(a.L0)]
        a.PSF_seeing.L0_units = a.L0_units
        hdu = a.PSF_seeing._hdu()
        if verbose:
            print '    %s'%seeing_psf_filename
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore',module='pyfits')
            hdu.writeto(seeing_psf_filename,clobber=True)
        
        self.index += 1
        
        t1 = time.time()
        if verbose:
            print '(%.3f sec)'%(t1-t0); t0=t1
            print 'done'; flush()

def summary(pdf=False):
    print 'GLAO PSF ENA = %0.4f %s'%(a.PSF.ena,a.PSF.ena_units)
    print 'Seeing PSF ENA = %0.4f %s'%(a.PSF_seeing.ena,a.PSF_seeing.ena_units)
    print 'GLAO PSF ENA_r = %0.4f %s'%(a.PSF.ena_r,'arcsec')
    print 'Seeing PSF ENA_r = %0.4f %s'%(a.PSF_seeing.ena_r,'arcsec')
    assert pdf in [True,False]
    if platform.system() == 'Darwin' and 'VIRTUAL_ENV' in os.environ:
        pdf = True
    if pdf:
        gfile = 'glao_psf_summary.pdf'
        pp = PdfPages(gfile)
    plt.figure()
    a.constellation.graph()
    plt.grid('off')
    if pdf:
        pp.savefig()
    a.PSF.graph(label='GLAO')
    a.PSF_seeing.graph(oplot=True,label='seeing')
    plt.legend()
    if pdf:
        pp.savefig()
    a.PSF.show()
    if pdf:
        pp.savefig()
    a.PSF_seeing.show()
    if pdf:
        pp.savefig()
        pp.close()
        print 'Graphs written to\n    %s'%os.path.abspath(gfile)

default_config = {
    'ngs':3,
    'geom':'circle',
    'rot': '45.',
    'radius':'6 arcmin',
    'profile':'Maunakea 13N median',
    'outer_scale':'30 meters',
    'r0': '',
    'DM_conjugate': '-280 meters',
    'actuator_spacing': '0 cm',
    'wavelength':'0.5 microns',
    'field_point': '(0.,0.), (2.5,0), (4.,0.), (5.,0.) arcmin',
    'run_name':'rdata',
    'filename':'psf',
    'seeing_psf_filename':'psf0'
}
    
def get_config(configFile=None,verbose=True):
    """Read the config file and generate a dictionary that can be sent
    as an argument to run()
    """
    
    if verbose:
        print 'reading config params from '; flush()
    path = os.path.abspath(__file__)
    dir_path = os.path.dirname(path)
    exampleConfigFile = os.path.join(dir_path,'example.cfg')

    if configFile is None:
        configFile = exampleConfigFile
    
    if not os.path.isfile(configFile):
        if configFile == 'example.cfg':
            configFile = exampleConfigFile
        else:
            raise IOError,'no file named %s'%configFile

    if configFile == exampleConfigFile:
        if verbose:
            print '### using example config file from code source directory ###'

    if verbose:
        print '    %s'%os.path.abspath(configFile)
            
    config  = cp.ConfigParser(default_config)
    config.read(configFile)
    
    config_syntax = {
        'constellation/ngs':[int,{}],
        'constellation/geom':[str,{}],
        'constellation/radius':[float,{'arcmin':1.,'arcsec':1./60.}],
        'constellation/rot':[float,{'degrees':1}],
        'atmosphere/profile':[str,{}],
        'atmosphere/outer_scale':[float,{'meters':1., 'm':1.}],
        'atmosphere/r0':[float,{'meters':1.,'cm':0.01}],
        'AO/DM_conjugate':[float,{'meters':1.,'m':1.}],
        'AO/actuator_spacing':[float,{'meters':1.,'cm':0.01}],
        'image/wavelength':[float,{'microns':1.,'micron':1.,'A':0.1,'angstrom':0.1}],
        'image/field_point':[(float,float),{'arcmin':1.,'arcsec':1./60.}],
        'output/filename':[str,{}],
        'output/seeing_psf_filename':[str,{}],
        'output/run_name':[str,{}],
    }
    
    args = {'configFile':configFile}
    for key in config_syntax:
        section,pname = key.split('/')
        val = config.get(section,pname)
        typer,units = config_syntax[key]
        unames = units.keys()
        uscale = 1
        for uname in unames:
            if val.endswith(uname):
                uscale = units[uname]
                val = val[:-len(uname)]
                break
        if len(val) == 0:
            val = ''
        else:
            if pname == 'radius' and val.startswith('follow'):
                # optional format: 'follow <fac> x <min> [unit]'
                val = val.split(' ')
                fac = float(val[1])
                minr = float(val[3])
                val = {'factor':fac, 'minimum':minr*uscale}
            elif typer is str:
                val = val.split(',')
                if len(val) == 1:
                    val = val[0].strip()
                else:
                    val = map(lambda x: x.strip(),val)
            elif typer == (float,float):
                val = eval(val)
                try:
                    val = map(lambda x: tuple(map(float,x)), val)
                except:
                    val = tuple(map(float,val))
            else:
                val = val.split(',')
                u = []
                for v in val:
                    if v.strip().lower() in ['infinite','infinity']: v = 'inf'
                    u.append(v)
                val = map(lambda x: typer(x)*uscale, u)
                if len(val) == 1:
                    val = val[0]
        args[pname] = val

    return args

def progress_bar(n,N):
    """This creates and maintains a progress bar to show the status of long computations
    Arguments:
        n = the number of operations performed so far
        N = the total number of operations to be performed
    """
    pc = int(np.round(100*float(n)/float(N)))
    N_max = 50
    d = N//N_max + 1
    N = N//d
    n = n//d
    sys.stdout.write('\r')
    fmt = '[%%-%ds]' % N
    ostr = (fmt+' %d%%') % ('='*n,pc)
    sys.stdout.write(ostr)
    sys.stdout.flush()

def test():
    '''Test run of multiple PSF calculations
    '''
    d = get_config('keck.cfg')
    d['radius'] = 5.
    d['DM_conjugate'] = 0.
    L0_set = [20.,30.,50.,100.,float('Infinity')]
    for L0 in L0_set:
        d['outer_scale'] = L0
        run(args=d,verbose=False,save_result=False)
        print '<test> L0 = %0.3f, ENA_r = %0.3f (%0.3f)'%(a.L0,a.PSF.ena_r,a.PSF_seeing.ena_r)
        

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--verbose',nargs='?',default=False,const=True,type=bool,help='print diagnostics as it runs')
    parser.add_argument('--summary',nargs='?',default=False,const=True,type=bool,help='create a summary and save graphs to a file')
    parser.add_argument('config_file',nargs='?',default='example.cfg',type=str,help='config file name')
    args = parser.parse_args()
    configFile = args.config_file
    verbose = args.verbose
    run(configFile,verbose=verbose)
    if args.summary:
        summary(pdf=True)
