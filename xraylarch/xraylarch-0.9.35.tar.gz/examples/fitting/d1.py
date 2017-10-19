## examples/fitting/doc_example1.lar
# create mock data
from numpy import linspace, random
from larch import Interpreter, Group, Parameter, minimize, param_group
from lmfit.lineshapes import gaussian

_larch = Interpreter()

mdat = Group()
mdat.x = linspace(-10, 10, 201)
mdat.y = 1.0 + gaussian(mdat.x, amplitude=12, center=1.5, sigma=2.0) + \
         random.normal(size=len(mdat.x), scale=0.050)

# create a parameter group for the fit:
params = param_group(off = Parameter('off', 0, vary=True),
                     amp = Parameter('amp', 5, min=0),
                     cen = Parameter('cen', 2),
                     wid = Parameter('wid', 1, min=0), _larch=_larch)

init = params.off + gaussian(mdat.x, params.amp, params.cen, params.wid)

# define objective function for fit residual
def resid(p, data):
    return data.y - (p.off + gaussian(data.x, p.amp, p.cen, p.wid))
#enddef

# perform fit
out  = minimize(resid, params, args=(mdat,), _larch=_larch)

#
# make final array
# final = params.off + gaussian(mdat.x, params.amp, params.cen, params.wid)
# #
# # plot results
# plot(mdat.x, mdat.y, label='data', show_legend=True, new=True)
# plot(mdat.x, init,   label='initial', color='black', style='dotted')
# plot(mdat.x, final,  label='final', color='red')

# print report of parameters, uncertainties
print(out)

## end of examples/fitting/doc_example1.lar
