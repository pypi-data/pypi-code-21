import itertools

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

args = {'radius':'follow 1.2 1.0'}
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



import ConfigParser as cp

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

configFile = 'keck.cfg'
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

args = {}
for key in config_syntax:
    section,pname = key.split('/')
    val = config.get(section,pname)
    typer,units = config_syntax[key]
    unames = units.keys()
    for uname in unames:
        if val.endswith(uname):
            uscale = units[uname]
            val = val[:-len(uname)]
            break
    if len(val) == 0:
        val = ''
    else:
        if typer is str:
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
            val = map(typer,u)
            if len(val) > 1:
                val = map(typer,val)
            else:
                val = typer(val[0])

    args[pname] = val

method = 'original'; outer_scale = Infinity
>>> db.iloc[0]['ENA_R']
0.6515398672199999
db[db.FIELD_PO == '(0.0, 0.0)'][['ENA_R','RADIUS']]
       ENA_R  RADIUS  Speedup
7   0.369332     0.5  3.1120610952616117
8   0.425501     1.0  2.344665104106218
9   0.464750     1.5  1.9653648887889608
10  0.497316     2.0  1.716394547533906
11  0.545843     3.0  1.4247757004083634
12  0.596712     5.0  1.1922091390271172
13  0.643981    10.0  1.0236132095356916
>>> db.iloc[0]['ENA_R']

method = 'original'; outer_scale = 30 meters
>>> db.iloc[0]['ENA_R']
0.47675858099299995
>>> db[db.FIELD_PO == '(0.0, 0.0)'][['ENA_R','RADIUS']]
       ENA_R  RADIUS
7   0.346919     0.5
8   0.379747     1.0
9   0.401612     1.5
10  0.423602     2.0
11  0.465301     3.0
12  0.519550     5.0
13  0.566069    10.0

method = 'new'; outer_scale = 30 meters
>>> db.iloc[0]['ENA_R']
0.47675858099299995
>>> db[db.FIELD_PO == '(0.0, 0.0)'][['ENA_R','RADIUS']]
       ENA_R  RADIUS
7   0.333927     0.5
8   0.387271     1.0
9   0.392240     1.5
10  0.425824     2.0
11  0.466039     3.0
12  0.518515     5.0
13  0.565266    10.0

method = 'new'; outer_scale = Infinity
>>> db.iloc[0]['ENA_R']
0.6515398672199999
>>> db[db.FIELD_PO == '(0.0, 0.0)'][['ENA_R','RADIUS']]
       ENA_R  RADIUS
7   0.355881     0.5
8   0.433445     1.0
9   0.455512     1.5
10  1.077291     2.0
11  0.530403     3.0
12  0.623651     5.0
13  0.654957    10.0
