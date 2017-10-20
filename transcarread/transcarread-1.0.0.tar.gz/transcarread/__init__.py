import logging
from pathlib import Path
from datetime import datetime
from dateutil.parser import parse
import numpy as np
from scipy.interpolate import interp1d
from pandas import DataFrame
from dateutil.relativedelta import relativedelta
from pytz import UTC
import xarray
#
from sciencedates import find_nearest
from gridaurora.ztanh import setupz
#
nhead = 126 #a priori from transconvec_13
NumPerRow = 5
NdataCol = 11
NprecipCol = 2
d_bytes = 4
#ncol0 = 50 #from transconvec_13.op.f
headbytes = 504 #from inspection of "good" .dat file, x1F8=d504, 504 gets us up to this point

toobig = 300 #beyond which number of altitude cells transcar will crash


ISRPARAM = ['ne','vi','Ti','Te']
PARAM = ['n1','n2','n3','n4','n5','n6','n7',
            'v1','v2','v3','vm','ve',
            't1p','t1t','t2p','t2t','t3p','t3t','tmp','tmt','tep','tet']


def read_tra(tcofn:Path, tReq:datetime=None):
    """
    reads binary "transcar_output" file
    many more quantities exist in the binary file, these are the ones we use so far.
    requires: Matplotlib >= 1.4

    examples: test_readtra.py

    Michael Hirsch

    inputs:
    tcofn: path/filename of transcar_output file
    tReq: optional, datetime at which to extract data from file (will still read whole file first)

    variables:
    n_t: number of time steps in file
    n_alt: number of altitudes in simulation
    d_bytes: number of bytes per data element
    size_record: number of data bytes per time step

    Note: header length = 2*ncol
    """
    head0 = readionoheader(tcofn, nhead)[0]
    ncol = head0['ncol']; n_alt = head0['nx']

    size_head = 2*ncol #+2 by defn of transconvec_13
    size_data_record = n_alt*ncol #data without header
    size_record = size_head + size_data_record

    assert size_head == nhead
#%% read data based on header
    iono,chi,pp = loopread(tcofn,size_record,ncol,n_alt,size_head,size_data_record,tReq)

    return iono,chi, pp

def loopread(tcoutput,size_record,ncol,n_alt,size_head,size_data_record,tReq):
    tcoutput = Path(tcoutput).expanduser()
    n_t = tcoutput.stat().st_size//size_record//d_bytes

    chi  = np.empty(n_t, float)
    t =    np.empty(n_t, datetime)

    plasmaparam = xarray.DataArray(data= np.empty((n_t,n_alt,4)),
                                   dims=['time','alt_km','isrparam'])
    iono = xarray.DataArray(data=np.empty((n_t,n_alt,22)),
                     dims=['time','alt_km','param'])

    with tcoutput.open('rb') as f: #reset to beginning
        for i in range(n_t):
            iono[i,...], chi[i], t[i], alt, plasmaparam[i,...] = data_tra(f, size_record,ncol,n_alt, size_head, size_data_record)
        # FIXME isn't there a way to inherit coordinates like Pandas?
        iono = iono.assign_coords(time=t,param=PARAM,alt_km=alt)
        plasmaparam = plasmaparam.assign_coords(time=t,isrparam=ISRPARAM,alt_km=alt)
#%% handle time request -- will return Dataframe if tReq, else returns Panel of all times
    if tReq is not None: #have to qualify this since picktime default gives last time as fallback
        tUsedInd = picktime(iono.time, tReq, None)[0]
        if tUsedInd is not None: # in case ind is 0
            iono = iono[tUsedInd,...]
            plasmaparam = plasmaparam[tUsedInd,...]

    return iono,chi,plasmaparam

def data_tra(f, size_record, ncol, n_alt, nhead, size_data_record):
#%% parse header
    h = np.fromfile(f, np.float32, nhead)
    head = parseionoheader(h)
#%% read and index data
    data = np.fromfile(f, np.float32,size_data_record).reshape((n_alt,ncol),order='C')

    dextind = tuple(range(1,7)) + (49,) + tuple(range(7,13))
    if head['approx'] >= 13:
        dextind += tuple(range(13,22))
    else:
        dextind += (12,13,13,14,14,15,15,16,16)
    #n7=49 if ncol>49 else None

    iono = xarray.DataArray(data[:,dextind],
                             coords=[('alt_km',data[:,0]),
                                     ('isrparam', PARAM)])
#%% four ISR parameters
    """
    ion velocity from read_fluidmod.m
    data_tra.m does not consider n7 for ne or vi computation,
    BUT read_fluidmod.m does consider n7!
    """
    pp = compplasmaparam(iono,head['approx'])

    return iono, head['chi'],head['htime'], data[:,0],pp


#%% read iono
def readmsis(ifn, ofn, dz, newaltmethod):
    nhead = headbytes//d_bytes
    hd,hdraw = readionoheader(ifn,nhead)

    msis,raw = readinitconddat(hd,ifn) #index is altitude (km)

    pp = compplasmaparam(msis,hd['approx'])

    msisinterp,hdinterp,ppinterp, rawinterp = interpdat(msis, dz,hd,pp,raw, newaltmethod)

    writeinterpunformat(hdinterp['nx'], rawinterp,hdraw,ofn)

    return msisinterp,hdinterp,ppinterp


def getaltgrid(ifn):
    """
    Helper function for HiST-feasibility to quickly get transcar alt grid
    """
    nhead = headbytes//d_bytes
    hd = readionoheader(ifn,nhead)[0]
    msis,raw = readinitconddat(hd,ifn) #index is altitude (km)

    return msis.index.values

def interpdat(md, dz, hd, pp, raw,newaltmethod):

#%% was interpolation requested?
    if dz[0] is None:
        return md, hd, pp, raw
#%% interpolate initial conditions
    malt = newaltmethod.lower()
    if malt == 'tanh':
        z_new = setupz(md.shape[0], md.index[0], dz[0], dz[1])
    elif malt == 'linear':
        print('interpolating to grid space {:.2f}'.format(dz) + ' km.')
        z_new = np.arange(md.index[0], md.index[-1], dz[0], dtype=float)
    elif malt =='incr':
        """
        in this case, dz is start spacing and  amount to increase step size for each element
        The method used to implement this is inefficient, but it is a very small dataset.
        """
        z_new = [md.index[0]]
        cdz = dz[0]
        while (z_new[-1] + cdz)<md.index[-1]:
            z_new.append(z_new[-1]+cdz)
            cdz+=dz[0]
        z_new = np.asarray(z_new)
    else:
        logging.warning('unknown interp method {}, returning unaltered values.'.format(newaltmethod))
        return md, hd, pp, raw

    if z_new.size > toobig:
        logging.warning('note: Transcar may not accept altitude grids with more than about {} elements.'.format(toobig))



    mint = DataFrame(index=z_new,
                     columns=md.columns.values.tolist()) #this is faster than list(md)
    for m in md:
        fint = interp1d(md.index, md[m], kind='linear',axis=0)
        mint[m] = fint(z_new)
#%% new header, only change to number of altitudes
    hdint = hd
    hdint['nx'] = z_new.size
#%% raw data, we'll write this to disk later
    fint = interp1d(md.index, raw, kind='linear', axis=0)
    rawint = fint(z_new)
#%% interpolate derived parameters
    ppint = DataFrame(index=z_new,
                      columns=pp.columns.values.tolist())
    for p in pp:
        fint = interp1d(pp.index, pp[p], kind='linear', axis=0)
        ppint[p] = fint(z_new)

    return mint,hdint, ppint, rawint

def writeinterpunformat(nx, rawi, hdraw, ofn):
    if ofn is None:
        return
    ofn = Path(ofn).expanduser()
    #update header with new number of altitudes due to interpolation
    hdraw[0] = nx

    print('writing',ofn)
    with ofn.open('wb') as f:
        hdraw.tofile(f,'','%f32')
        rawi.astype(np.float32).tofile(f,'','%f32')


def readionoheader(ifn, nhead):
    """ reads BINARY transcar_output file """
    ifn = Path(ifn).expanduser() #not dupe, for those importing externally

    with ifn.open('rb') as f:
        h = np.fromfile(f, np.float32, nhead)

    return parseionoheader(h), h

def parseionoheader(h):
    """
    for reading 90kmmaxpt123.dat, which may have been generated by MSIS90
    This file was figured out by inspection of dir.source/transconvec_13.op.f
    Michael Hirsch
    GPLv3+

    inputs:
    dz: altitude step

    variables:
    nx: number of altitudes
    raw: 2-D array of data for each altitude, this is what we'll interpolate and
    write back to disk

    Note: by inspection, data values of 90kmmaxpt123.dat start at byte 504

    TRANSCAR takes the initial conditions file as an initial state at t=0, and then
    computes the state of the ionosphere for times t=0+{T1,T2,T3....Tn}.
    This output is stored in dir.output/transcar_output, which is read by
    read_tra.py in a similar manner to this code
    """
    assert 1<=h[3]<=12
    assert 1<=h[4]<=31
    assert 0<=h[5]<24
    assert 0<=h[6]<60
    assert 0<=h[7]<60
    #... and so on with asserts. Just checking we aren't reading the totally wrong type of file
    # not a Series because all have to be same datatype
    # not a Dataframe because it's only 1-D
    hd = {'nx':h[0].astype(int), 'ncol':h[1].astype(int),
          #'year':h[2], 'month':h[3], 'day':h[4], 'hour':h[5], 'minute':h[6], 'second':h[7],
          'intpas':h[8], 'longeo':h[9], 'latgeo':h[10], 'lonmag':h[11], 'latmag':h[12],
          'tmag':h[13], 'f1072':h[14], 'f1073':h[15], 'ap2':h[16], 'ikp':h[17],
          'dTinf':h[18], 'dUinf':h[19], 'cofo':h[20], 'cofh':h[21],'cofn':h[22],
          'chi':h[23],'approx':h[36]}

    # h[37] last non-zero value till h[59], then zeros till start of data at byte 504
    # h[59] has value of 1.0

    hd['htime'] = datetime(year=h[2], month=h[3], day=h[4],
                           hour=h[5], minute=h[6], second=h[7],tzinfo=UTC)

    return hd

def readinitconddat(hd,fn):
    fn = Path(fn).expanduser()
    nx = hd['nx']
    ncol = hd['ncol']

    # *** these indices correspond exactly to the columns of msis!! ****
    # from transconvec_13.op.f lines 452 - 542
    if hd['approx'].astype(int) == 13:
        dextind = tuple(range(1,34))
    else:
        dextind = tuple(range(1,13)) + (12,13,13,14,14,15,15,16,16) + tuple(range(17,29))

    if ncol>60:
        dextind += (60,61,62)

    dextind += (49,) #as in output

    with fn.open('rb') as f: #python2 requires r first
        ipos = 2* ncol * d_bytes
        f.seek(ipos,0)
        rawall = np.fromfile(f,np.float32,nx*ncol).reshape((nx,ncol),order='C') #yes order='C'!

    msis = DataFrame(rawall[:,dextind],
                     index = rawall[:,0], # altitude
                     columns=('n1','n2','n3','n4','n5','n6',
                              'v1','v2','v3','vm','ve',
                              't1p','t1t','t2p','t2t','t3p','t3t',
                              'tmp','tmt','tep','tet',
                              'q1','q2','q3','qe','nno','uno',
                              'po','ph','pn','pn2','po2','heat',
                              'po1d','no1d','uo1d','n7'))

    return msis,rawall

#%% read transcar
def calcVERtc(kinfn:Path,datadir:Path, beamEnergy, tReq, sim):
    '''
    calcVERtc is the function called by "hist-feasibility" to get Transcar modeled VER/flux

    outputs:
    --------
    spec: Panel of excitation rates: reaction x altitude x time

    We use pcolormesh instead of imshow to enable correct log-plot labeling/coloring

    References include:
    Zettergren, M. "Model-based optical and radar remote sensing of transport and composition in the auroral ionosphere" PhD Thesis, Boston Univ., 2009
    Zettergren, M. et al "Optical estimation of aurinfileinfileoral ion upflow: 2. A case study" JGR Vol 113 A7  2008 DOI:10.1029/2007JA012691
    Zettergren, M. et al "Optical estimation of auroral ion upflow: Theory"          JGR Vol 112 A12 2007 DOI: 10.1029/2007JA012691

    Tested with:
    Matplotlib 1.4 (1.3.1 does NOT work for pcolormesh)

    Plambda contains all the wavelengths generated for the reactions at a particular beam energy level
    Plambda row: wavelength col: altitude
    for each energy bin, we take Plambda through the EMCCD window and optional BG3 filter,
    yielding Peigen, a ver eigenprofile p(z,E) for that particular energy
    '''
#%% get beam directory
    beamdir = Path(datadir) / f'beam{beamEnergy}'
    logging.debug(beamEnergy)
#%% read simulation parameters
    tctime = readTranscarInput(beamdir/'dir.input'/sim.transcarconfig)
    if tctime is None:
        return None, None #leave here

    try:
      if not tctime['tstartPrecip'] < tReq < tctime['tendPrecip']:
        logging.info(f'precip start/end: {tctime["tstartPrecip"]} / {tctime["tendPrecip"]}' )
        logging.error(f'your requested time {tReq} is outside the precipitation time')
        tReq = tctime['tendPrecip']
        logging.warning(f'falling back to using the end simulation time: {tReq}')
    except TypeError as e:
        tReq=None
        logging.error(f'problem with requested time : {tReq} beam {beamEnergy}  {e}')
#%% convert transcar output
    spec, tTC, dipangle = ExcitationRates(beamdir/kinfn)

    tReqInd,tUsed = picktime(tTC,tReq,beamEnergy)

    return spec,tUsed,tReqInd

def picktime(tTC,tReq,beamEnergy):
    tReqInd = find_nearest(tTC,tReq)[0]

    tUsed = tTC[tReqInd]

    return tReqInd,tUsed

#%% for testing only
class SimpleSim():
    """
    simple input for debugging/self test
    """
    def __init__(self,filt,inpath,reacreq=None,lambminmax=None,transcarutc=None):
        self.loadver = False
        self.loadverfn = Path('precompute/01Mar2011_FA.h5')
        self.opticalfilter = filt
        self.minbeamev = 0
        self.obsalt_km=0
        self.zenang=77.5
        #self.maxbeamev = #future
        self.transcarev = Path('~/code/transcar/transcar/BT_E1E2prev.csv')

        self.excratesfn = 'dir.output/emissions.dat'
        self.transcarpath = inpath
        self.transcarconfig = 'DATCAR'

        if isinstance(transcarutc,str):
            self.transcarutc = parse(transcarutc)
        else:
            self.transcarutc = transcarutc

        if reacreq is None:
            self.reacreq = ['metastable','atomic','n21ng','n2meinel','n22pg','n21pg']
        else:
            self.reacreq = reacreq

        if lambminmax is None:
            self.lambminmax = (1200,200)
        else:
            self.lambminmax = lambminmax

        self.reactionfn = Path('precompute/vjeinfc.h5')
        self.bg3fn = Path('precompute/BG3transmittance.h5')
        self.windowfn = Path('precompute/ixonWindowT.h5')
        self.qefn = Path('precompute/emccdQE.h5')

# %% ISR
def compplasmaparam(iono, approx) -> xarray.DataArray:
    assert isinstance(iono, xarray.DataArray)

    pp = xarray.DataArray(np.empty((iono.shape[0],4)),
                   coords=[('alt_km',iono.alt_km),
                           ('isrparam',['ne','vi','Ti','Te'])]
                   )

    nm = iono.sel(isrparam=['n4','n5','n6']).sum(dim='isrparam')

    pp.loc[:,'ne'] = comp_ne(iono)
#    pp.sel(isrparam='ne') = comp_ne(iono) # doesn't work for assign?
    pp.loc[:,'vi'] = comp_vi(iono,nm,pp)
    pp.loc[:,'Ti'] = comp_Ti(iono,nm,pp)
    pp.loc[:,'Te'] = comp_Te(iono,approx)

    return pp

def comp_ne(d):
    return (d.loc[:,['n1','n2','n3','n4','n5','n6','n7']].sum('isrparam'))

def comp_vi(d,nm,pp):
    return (d.loc[:,['n1','v1']].prod('isrparam') +
            d.loc[:,['n2','v2']].prod('isrparam') +
            d.loc[:,['n3','v3']].prod('isrparam') +
            nm * d.loc[:,'vm']) / pp.loc[:,'ne']

def comp_Ti(d,nm,pp):
    """transconvec_13.op.f
    read_fluidmod.m, data_tra.m
    """

    Tipar= (d.loc[:,['n1','t1p']].prod('isrparam') +
            d.loc[:,['n2','t2p']].prod('isrparam') +
            d.loc[:,['n3','t3p']].prod('isrparam') +
            nm * d.loc[:,'tmp']) / pp.loc[:,'ne']

    Tiperp=(d.loc[:,['n1','t1t']].prod('isrparam') +
            d.loc[:,['n2','t2t']].prod('isrparam') +
            d.loc[:,['n3','t3t']].prod('isrparam') +
            nm * d.loc[:,'tmt']) / pp.loc[:,'ne']
    #return (n1*t1 + n2*t2 + n3*t3 +nm*tm)/(n1 +n2 +n3 +nm)
    Ti = (1/3)*Tipar + (2/3)*Tiperp

    return Ti

def comp_Te(d,approx):
    if int(approx)==13:
        Te =  (d.loc[:,'tep'] + 2*d.loc[:,'tet']).astype(float) / 3.
    else:
        Te = d.loc[:,'tep'].astype(float)

    return Te
# %%

def ExcitationRates(kinfn:Path):
    """
    Michael Hirsch 2014
    Parses the ASCII dir.output/emissions.dat in milliseconds
    based on transconvec_13

    outputs:
    excrate: Panel of reaction x altitude x time

    variables:
    ------------
    Nalt: number of altitudes in simulation (not necessarily uniform spacing!)
    nen:
    dipangle,cdip: dip angle of B-field (degrees)
    timeop,ctime: time of simulation step (UTC)
    zop: altitudes [km]
    Nprecip: At the end of each time step, there are this many elements of precipitation data to read
    NprecipCol: 2, this accounts for e and fluxdown (each taking one column)
    NdataCol: number of data elements per altitude + 1
    NumData: number of data elements to read at this time step
    """
    excrate, dipangle, precip, t = readexcrates(kinfn)
    # breakup slightly to meet needs of simpler external programs
    #z = excite.major_axis.values
    return excrate, t, dipangle

def initparams(kinfn:Path):
    kinfn = Path(kinfn).expanduser()

    with kinfn.open('r') as fid: #going to rewind after this priming read
        line = fid.readline()

    ctime,dip,nalt,nen = getHeader(line)

    Nprecip = NprecipCol * nen # how many precip elements to read at this time step
    ndat = NdataCol * nalt #how many elements to read at this time step
    # how many rows of data (less header) to read in a batch
    ndatrow = (ndat + Nprecip)//NumPerRow  + 1

    logging.debug(f'{kinfn} {ctime} Nalt: {nalt} nen: {nen} dipangle[deg]: {dip:.2f}')

    return kinfn,nalt,nen,dip,ctime,ndatrow,ndat,Nprecip

def readexcrates(kinfn):
    kinfn,nalt,nen,dipangle,ctime,ndatrow,ndat,Nprecip = initparams(kinfn)
    #using read_csv was vastly slower!

    with kinfn.open('r') as f:
        dstream = np.asarray(f.read().split()).astype(float)
    #print(time()-tic)
    nhead = NumPerRow
    size_record = ndat + Nprecip + nhead
    n_t = dstream.size//size_record

    t = np.empty(n_t, datetime)
    excrate = xarray.DataArray(data=np.empty((n_t,nalt,10)),
                        dims=['time','alt_km','reaction'])
    excrate['reaction'] = ['no1d','no1s','noii2p','nn2a3','po3p3p','po3p5p', 'p1ng','pmein','p2pg','p1pg']

    precip = xarray.DataArray(data=np.empty((n_t,nen,NprecipCol)),dims=['time','e','fluxdown'])

    for i in range(n_t):
        cind = np.s_[i*size_record:(i+1)*size_record]
        crec = dstream[cind]

        #h = crec[:nhead] #unused
        d = crec[nhead:-Nprecip].reshape((nalt,NdataCol),order='C')
        # blank nan are between data and precip
        p = crec[-Nprecip:].reshape((nen,NprecipCol),order='C')

        t[i] = parseheadtime(crec[:2])

        excrate[i,...]= d[:,1:]

        precip[i,...] = p

    excrate['alt_km'] = d[:,0]
    excrate['time'] = t

    precip['time'] = t

    return excrate, dipangle, precip, t

def getHeader(line):
    """
    head[0]: Year, day of year YYYYDDD
    head[1]: second of day from midnight UTC
    head[2]: 90 - head[2] = B-field dipangle [deg]
    head[3]: Nalt
    head[4]: nen
    """
    head = line.split(None) #None: multiple whitespace as one
    assert len(head) == 5
    timeop = parseheadtime(head) #dt.strptime(head[0],'%Y%j').replace(tzinfo=UTC) + relativedelta(seconds=float(head[1]))
    dipangle = 90. - float(head[2])
    nalt = int(head[3])
    nen = int(head[4])

    return timeop, dipangle, nalt, nen

def parseheadtime(h):
    return datetime.strptime(str(int(h[0])),'%Y%j').replace(tzinfo=UTC) + relativedelta(seconds=float(h[1]))


def readTranscarInput(infn):
    '''
    The transcar input file is indexed by line number --this is what the Fortran
      #  code of transcar does, and it's what we do here as well.
    '''
    infn = Path(infn).expanduser()
    hd = {}
    with infn.open('r') as f:
        hd['kiappel'] =           int(f.readline().split()[0])
        hd['precfile'] =              f.readline().split()[0]
        hd['dtsim'] =           float(f.readline().split()[0]) #"dto"
        hd['dtfluid'] =         float(f.readline().split()[0]) #"sortie"
        hd['iyd_ini'] =         int(f.readline().split()[0])
        hd['dayofsim'] =  datetime.strptime(str(hd['iyd_ini']),'%Y%j').replace(tzinfo=UTC)
        hd['simstartUTCsec'] =  float(f.readline().split()[0]) #"tempsini"
        hd['simlengthsec'] =    float(f.readline().split()[0]) #"tempslim"
        hd['jpreci'] =            int(f.readline().split()[0])
        # transconvec calls the next two latgeo_ini, longeo_ini
        hd['latgeo_ini'], hd['longeo_ini'] = [float(a) for a in f.readline().split(None)[0].split(',')]
        hd['tempsconv_1'] =     float(f.readline().split()[0]) #from transconvec, time before precip
        hd['tempsconv'] =       float(f.readline().split()[0]) #from transconvec, time after precip
        hd['step'] =            float(f.readline().split()[0])
        hd['dtkinetic'] =       float(f.readline().split()[0]) #transconvec calls this "postinto"
        hd['vparaB'] =          float(f.readline().split()[0])
        hd['f107ind'] =         float(f.readline().split()[0])
        hd['f107avg'] =         float(f.readline().split()[0])
        hd['apind'] =           float(f.readline().split()[0])
        hd['convecEfieldmVm'] = float(f.readline().split()[0])
        hd['cofo'] =            float(f.readline().split()[0])
        hd['cofn2'] =           float(f.readline().split()[0])
        hd['cofo2'] =           float(f.readline().split()[0])
        hd['cofn'] =            float(f.readline().split()[0])
        hd['cofh'] =            float(f.readline().split()[0])
        hd['etopflux'] =        float(f.readline().split()[0])
        hd['precinfn'] =              f.readline().split()[0]
        hd['precint'] =           int(f.readline().split()[0])
        hd['precext'] =           int(f.readline().split()[0])
        hd['precipstartsec'] =  float(f.readline().split()[0])
        hd['precipendsec'] =    float(f.readline().split()[0])

        # derived parameters not in datcar file
        hd['tstartSim'] =    hd['dayofsim'] + relativedelta(seconds=hd['simstartUTCsec'])
        hd['tendSim'] =      hd['dayofsim'] + relativedelta(seconds=hd['simlengthsec']) #TODO verify this isn't added to start
        hd['tstartPrecip'] = hd['dayofsim'] + relativedelta(seconds=hd['precipstartsec'])
        hd['tendPrecip'] =   hd['dayofsim'] + relativedelta(seconds=hd['precipendsec'])

    return hd