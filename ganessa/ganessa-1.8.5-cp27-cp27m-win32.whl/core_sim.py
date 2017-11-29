# -*- coding: utf-8 -*-
from __future__ import (unicode_literals, print_function, absolute_import)
'''
Created on 8 sept. 2017

Functions specific to the hydraulic extended period and WQ simulation (Piccolo)

@author: Jarrige_Pi
'''
import numbers

from ganessa.util import winstr, quotefilename, hhmmss
from ganessa.sim import _dll_api
from ganessa.core import (M, DICT, SIMERR, GanessaError, _dll_version,
        selectlen, _select, _ganessa_raise_exceptions, _checkExceptions, 
        _fn_undefined, _ret_errstat)

# Run the simulation
try:
    solveh = _dll_api.simulh
except AttributeError:
    solveh = _dll_api.solveh
#****g* ganessa.sim/sFunctions
# DESCRIPTION
#   Functions available to ganessa.sim ONLY.
#****
#****g* ganessa.sim/sIterators
# DESCRIPTION
#   Iterators available to ganessa.sim ONLY
#****
#****f* sFunctions/full_solveH
# PURPOSE
#   Runs the full simulation and loads the result file for browsing results
# SYNTAX
#   istat = full_solveH([resultfile] [, silent] [, iverb] [, retry])
# ARGUMENT
#   * string resultfile: if provided, the results will be written in the file
#     instead of the default 'result.bin'. If the file exists it will be superseded.
#     If not it will be created.
#   * bool silent: if set to True, simulation runs without any output.
#     Optional - if False or not set, leaves 'iverb' unchanged.
#   * integer iverb: if provided, controls the amount of output during simulation
#     (SIM IVERB parameter). The defaults is -1.
#   * bool retry: if set to True, the simulation is run again if it fails
#     because of isolated nodes. Optional -  defaults to False
# RESULT
#   int istat: error status (0 if OK)
# REMARKS
#   - Unless explicitely disabled, results are saved to a binary file,
#     which defaults to the file 'result.bin' in the ganessa work directory.
#   - Binary result files also contain all data describing the model.
#   - silent=True overrides iverb setting if provided.
# HISTORY
#   optional argument 'retry' added in 1.5.1
#****
def full_solveH(resultfile= None, silent= False, iverb= -1, retry= False):
    # SIM IVERB
    if silent: sverb = '-9'
    elif iverb == -1: sverb = '-1'
    else: sverb = str(iverb)
    SIM = M.SIM
    _dll_api.gencmd(SIM.ROOT, SIM.IVER, M.NONE, sverb)
    if resultfile:
        # SIM FILE xxx
        _dll_api.gencmd(-SIM.ROOT, SIM.FILE, M.NONE, winstr(quotefilename(resultfile)))
    #  EXEC FULL-PERIOD
    _dll_api.gencmd(-SIM.ROOT, SIM.EXEC, DICT.FULLPER)
    istat = _dll_api.commit(0)
    if retry and abs(istat) % SIMERR.SIMERR == SIMERR.ISOL:
        _dll_api.gencmd(-SIM.ROOT, SIM.EXEC, DICT.FULLPER)
        istat = _dll_api.commit(0)
    _checkExceptions(32, istat, 'Error running hydraulic simulation')
    return istat

#****f* sFunctions/solveH
# PURPOSE
#   Runs the simulation at a given instant
# SYNTAX
#   istat = solveH(time [, retry])
# ARGUMENT
#   * int or str time: instant to run the simulation - default to 0.
#     if int: time in seconds; if str: time in the format hh:mm[:ss]
#   * bool silent: if set to True, simulation runs without any output.
#     Optional - if False or not set, leaves 'iverb' unchanged.
#   * integer iverb: if provided, controls the amount of output during simulation
#     (SIM IVERB parameter). If not set, leaves 'iverb' unchanged.
#   * bool retry: if set to True, the simulation is run again if it fails
#     because of isolated nodes. Optional -  defaults to False
# RESULT
#   int istat: error status (0 if OK)
# HISTORY
#   added 2017.05.15 - version 1.7.5
#****
def solveH(time= 0, silent= False, iverb= None, retry= False):
    # SIM
    SIM = M.SIM
    _dll_api.gencmd(SIM.ROOT, SIM.NONE, M.NONE)
    # IVERB
    if silent: 
        iverb = -9
    if iverb is not None: 
        _dll_api.gencmd(-SIM.ROOT, SIM.IVER, M.NONE, str(iverb))
    # Simulation time
    if isinstance(time, numbers.Number):
        if time == 0:
            stime = '0:0:0'
        else:
            stime = hhmmss(time, rounded=True)
    else:
        stime = time
    #  EXEC
    _dll_api.gencmd(-SIM.ROOT, SIM.EXEC, M.NONE, stime)
    istat = _dll_api.commit(0)
    if retry and abs(istat) % SIMERR.SIMERR == SIMERR.ISOL:
        _dll_api.gencmd(-SIM.ROOT, SIM.EXEC, M.NONE, stime)
        istat = _dll_api.commit(0)
    _checkExceptions(32, istat, 'Error running hydraulic simulation')
    return istat


#****f* sFunctions/setWQresultfile
# PURPOSE
#   Defines the binary result file(s) for WQ simulation.
# SYNTAX
#   setWQresultfile([fnode] , [flink])
# ARGUMENTS
#   * str fnode: name of the node WQ result file
#   * str flink: name of the link WQ result file (optional)
# REMARK
#   * if fnode is omitted, either use None or flink=filename
#   * this command can be used either before running the simulation, for writing
#     the file(s), or afterwards, in order to choose which result file(s) to browse.
#****
def setWQresultfile(fnode=None, flink=None):
    '''Added 150914'''
    QUA = M.QUA
    if fnode is not None:
        # QUAL FILE xxx
        _dll_api.gencmd(QUA.ROOT, QUA.NODEFILE, M.NONE, winstr(quotefilename(fnode)))
    if flink is not None:
        # QUAL FILE xxx
        _dll_api.gencmd(QUA.ROOT, QUA.LINKFILE, M.NONE, winstr(quotefilename(flink)))
    _istat = _dll_api.commit(0)

#****f* sFunctions/browseH, browseWQ
# PURPOSE
#   Retrieves and interpolate results from a given time step or instant:
#   * browseH retrieves hydraulic results
#   * browseWQ retrieves hydraulic
#   |html <b>and</b> water quality results
# SYNTAX
#   * istat = browseH(time_step)
#   * istat = browseH(instant)
# ARGUMENTS
#   * int time_step: time step to load
#   * string instant: instant to load, in the form hh:mm:ss
# RESULT
#   int istat: error status (0 if OK)
# REMARKS
#   For hydraulic results, two set of results may be available at a given instant:
#   * at boudary of time steps, except beginning and end of the simulation,
#     results ending the previous time step and results starting the next time step.
#   * at internal time steps when a state transition occured (pump start/stop etc.).
#   In such a situation the results are those from the end of the previous interval.
#****
def browseH(time_or_str, wq= False):
    if isinstance(time_or_str, numbers.Number):
        stime = hhmmss(time_or_str, rounded= True)
    else:
        stime = time_or_str
    GEN = M.GEN
    _dll_api.gencmd(GEN.ROOT, GEN.FIND, DICT.INSTANT, stime)
    if wq:
        _dll_api.gencmd(GEN.ROOT, GEN.FIND)
        _dll_api.gencmd(M.QUA.ROOT, M.NONE, extmode= 1)
    istat = _dll_api.commit(0)
    if _ganessa_raise_exceptions and istat:
        raise GanessaError(16*3, istat,
                'Error while retrieving simulation results at: ' + stime)
    return istat

def browseWQ(time_or_str):
    return browseH(time_or_str, True)

#****f* sFunctions/tsdemand, tsdevice, tsdemandlen, tsdevicelen
# PURPOSE
#   * tsdemandlen: returns the number of values in the profile
#   * tsdevicelen: returns the number of values in the device state TS
#   * tsdemand: return the profile time series
#   * tsdevice: return the device state time series(boundary conditions)
# SYNTAX
#   * tslen = tsdemandlen(code)
#   * vec_tim, vec_val, len, mode = tsdemand(code)
#   * tslen = tsdevicelen(sid[, attr])
#   * vec_tim, vec_val, len, mode = tsdevice(sid [, attr] [, fixed_interval])
# ARGUMENTS
#   * string code: demand type of element
#   * string sid: device element ID
#   * string attr: pump attribute (speed or number of units) or ''
#   * float fixed_interval (optional): if present and > 0, return values at the give time step
# RESULT
#   * int tslen: number of values for the time serie (0 if none)
#   * float[] vec_tim: vector of instants in seconds
#   * float[] vec_val: vector of demand coefficients (not percentages) or settings
#    (for pumps: 0= off, 1 or higher= open/active)
#   * int mode: type of demand profile (<0 as time series, >0 based on time steps)
# REMARKS
#   * These functions require version 2016 or higher of Piccolo/Ganessa dll
#   * when the demand code or equipment does not exist or has no forcing TS associated,
#     the value (None, None, 0, 0) is returned.
#   * The demand coefficient for the demand type 'code' can be retrieved
#     as float(getvar('coefficient:' + code))
#   * A pump is shut off when the number of units running is 0, even if rotation speed is > 0.
# HISTORY
#   * 25.01.2017: added 'fixed_interval' parameter to tsdevide; changed return value to float
#
#****
try:
    tsdemandlen = _dll_api.demand_tslen
except AttributeError:
    _fn_undefined.append('tsdemand')
    tsdemandlen = _ret_errstat

def tsdemand(code):
    nbval = tsdemandlen(code)
    if nbval > 0:
        return _dll_api.demand_ts(code, nbval)
    else:
        return (None, None, 0, 0)

try:
    tsdevicelen = _dll_api.device_tslen
except AttributeError:
    _fn_undefined.append('tsdevice')
    tsdevicelen = _ret_errstat

def tsdevice(sid, attr= ' ', fixed_interval= 0.0):
    if fixed_interval > 0.0:
        tmin, tmax, nbval = _dll_api.tsinterv()
        nbval = int((tmax - tmin)/fixed_interval + 1.499999)
        del tmin, tmax
    else:
        nbval = tsdevicelen(sid, attr)
        fixed_interval = 0.0
    if nbval > 0:
        return _dll_api.device_ts(sid, nbval, fixed_interval, attr)
    else:
        return (None, None, 0, 0)

#****f* sFunctions/hstepcount, tslen, mslen, tsval, msval, tsvalbymts, tsinterv, refdate
# PURPOSE
#   * hstepcount: returns the number of user time steps
#   * tslen, mslen: return number of elements in the time serie
#   * tsval, msval: return the time series of results and measurements
#   * tsvalbymts: return the time series of results at measurement time steps
#     for a given element type, id and attribute
#   * refdate: return date corresponding to the beginning of simulation
# SYNTAX
#   * hsc = hstepcount()
#   * len = tslen()
#   * len = mslen(typelt, id, attr)
#   * vec_tim, vec_val, len = tsval(typelt, id, attr, [interval])
#   * vec_tim, vec_mes, len = msval(typelt, id, attr, [interval])
#   * vec_tim, vec_val, len = tsvalbymts(typelt, id, attr)
#   * tmin, tmax, len = tsinterv()
#   * sdate = refdate()
# ARGUMENTS
#   * int typelt: type of element
#   * string id: id of element
#   * string attr: attribute (data or result) for which value is requested
#   * float interval (optional): if present, requests the time serie
#     at given fixed interval in seconds
# RESULT
#   * int hsc: number of user time steps
#   * int len: number of values for the time serie
#   * float[] vec_tim: vector of instants in seconds
#   * float[] vec_val: vector of simulated results at the instants vec_tim
#   * float[] vec_mes: vector of measurements at the instants vec_tim
#   * float tmin and tmax: first (vec_tim[0]) and last (vec_tim[-1])
#     instants available in the result time series
#   * string sdate: date time at beginning of the simulation (iso format)
# REMARKS
#   * The time vector is identical for simulation results of all elements of all types ,
#     and can be much larger than the number of (user) time steps
#   * two consecutive instants in the time vector for simulation results may
#     be identical at time step boundaries, change status instants etc.
#   * Each element may have a different measurement time vector form the others
#   * Measurements time series may have different begin and end dates from results
#   * Add 'sdate' in order to get absolute date time
#   * hstepcount requires version 2016 or higher of Piccolo/Ganessa dll
# HISTOTY
#  12/12/2016 (1.5.1): bug fix when no simulation result available
#****
# Get functions - time series (results and measurements)
try:
    hstepcount = _dll_api.hstepcount
except AttributeError:
    _fn_undefined.append('hstepcount')
    hstepcount = _ret_errstat
tslen = _dll_api.tslen
tsinterv = _dll_api.tsinterv
mslen = _dll_api.mslen
ms = _dll_api.ms
ts = _dll_api.ts

def tsval(typelt, sid, sattr, fixed_interval= 0.0):
    if fixed_interval > 0.0:
        tmin, tmax, nbval = _dll_api.tsinterv()
        nbval = int((tmax - tmin)/fixed_interval + 1.499999)
        del tmin, tmax
    else:
        nbval = _dll_api.tslen()
        fixed_interval = 0.0
    if nbval > 0:
        return _dll_api.ts(typelt, sid, sattr, nbval, fixed_interval)
    return (None, None, nbval)

def msval(typelt, sid, sattr, fixed_interval= 0.0):
    nbval = _dll_api.mslen(typelt, sid, sattr)
    if nbval <= 0:
        return (None, None, nbval)
    if fixed_interval > 0.0:
        t, v, nb = _dll_api.ms(typelt, sid, sattr, nbval)
        nbval = int((t[-1] - t[0])/fixed_interval + 1.499999)
        del t, v, nb
    else:
        fixed_interval = 0.0
    return _dll_api.ms(typelt, sid, sattr, nbval, fixed_interval)

def tsvalbymts(typelt, sid, sattr):
    nbval = _dll_api.mslen(typelt if _dll_version < 20141205 else -typelt, sid, sattr)
    if nbval > 0:
        return _dll_api.ts(-typelt, sid, sattr, nbval, 0.0)
    return (None, None, nbval)

def refdate():
    sdate, slen = _dll_api.refdate()
    return sdate[0:slen] if slen > 0 else ''

#****f* sFunctions/msmooth
# PURPOSE
#   Defines the smoothing constant for time series of measurements
# SYNTAX
#   msmooth(twidth)
# ARGUMENTS
#   twidth: characteristic time window for smoothing, in seconds
# REMARKS
#   * The smoothing algorithm is a convolution with exp(-(t/twidth)^2).
#   * Best results are expected when twidth is in the order of magnitude
#     or larger than the sampling interval.
#   * call msmooth(0.0) in order to cancel smoothing.
#****
def msmooth(twidth):
    # MESURE DT-LISSAGE xxx
    sval = str(twidth) if isinstance(twidth, numbers.Number) else twidth
    MES = M.MES
    _dll_api.gencmd(MES.ROOT, MES.SMOOTH, M.NONE, sval)
    _dll_api.gencmd(M.COM.ROOT, M.NONE)
    _dll_api.commit(0)

#****f* sFunctions/defcalind, getcalind
# PURPOSE
#   Compute and return calibration indicators
# SYNTAX
#   * defcalind(br_threshold, no_threshold, rsv_threshold)
#   * val, ival = getcalind(typelt, numelt)
# ARGUMENTS
#   * br_*** : thresholds for computing indicators
#   * int typelt: type of element
#   * string id: id of element
# RESULT
#   val:  percentage of values below threshold
#   ival: indicator rank, from 1 (best) to 4 (worse) (-1 if not defined)
# REMARK
#   defcalind actually compute all indicators; getcalind returns them.
#****
def defcalind(br_threshold= 0.1, no_threshold= 0.2, rsv_threshold= 0.5):
    _dll_api.defcalind(br_threshold, no_threshold, rsv_threshold)

getcalind = _dll_api.getcalind

#****f* sFunctions/getallminmax
# PURPOSE
#   * getallminmax returns the min, max, average and mindate, maxdate
#     for all objects of the given type
# SYNTAX
#   * vec_min, vec_max, vec_avg, vec_tmin, vec_tmax = getallminmax(typelt, attr)
# ARGUMENTS
#   * int typelt: type of element (LINK, NODE, TANK)
#   * string attr: attribute (result) for which value is requested
# RESULT
#   * float[] vec_min, vec_max, vec_avg: min, max and avg values for all elements
#   * float[] vec_tmin, vec_tmax: vector of instants where the min, max value is reached
#****
def getallminmax(typelt, sattr):
    nbval = _dll_api.nbobjects(typelt)
    if nbval > 0:
        return _dll_api.getallminmax(typelt, sattr, nbval)
    else:
        return (None, None, None, None, None)

#****k* sIterators/getMinMax
# PURPOSE
#   Returns the id, min, max, avg value reached by the attribute for each object
#   of the given type or selection in turn
# SYNTAX
#   for id, vmin, vmax, vavg in getMinMax(typelt or selection, sattr):
# ARGUMENT
#   * int typelt: type element constants BRANCH, NODE, RESERVOIR
#   * string selection: name of a selection
#   * string attr: attribute (result) for which value is requested
# RESULT
#   id, vmin, vmax, vavg: element id, minimum, maximum and average values
#   for the attribute over the simulation
#****
class getMinMax(object):
    def __init__(self, typelt_sel, sattr):
        self.attr = sattr
        if isinstance(typelt_sel, numbers.Number):
            self.type = typelt_sel
            self.nbmax = _dll_api.nbobjects(self.type)
            self.select = range(1, self.nbmax + 1)
        elif isinstance(typelt_sel, basestring):
            self.nbmax, self.type = selectlen(typelt_sel)
            if self.nbmax > 0:
                self.select = _select(self.nbmax)
        else:
            raise TypeError
        nbelem = _dll_api.nbobjects(self.type)
        if self.nbmax > 0:
            self.vmin, self.vmax, self.avg, tmin, tmax = _dll_api.getallminmax(self.type, sattr, nbelem)
            del tmin, tmax
        self.index = 0
    def __iter__(self):
        return self
    def next(self):
        if self.index >= self.nbmax:
            if self.nbmax > 0:
                del self.vmin, self.vmax, self.avg, self.select
                self.nbmax = 0
            raise StopIteration
        # returns fortran index (from 1)
        numelt = self.select[self.index]
        (elem, ls) = _dll_api.getid(self.type, numelt)
        # np.array index
        numelt -= 1
        vmin, vmax, vmoy = self.vmin[numelt], self.vmax[numelt], self.avg[numelt]
        self.index += 1
        return (elem[0:ls], vmin, vmax, vmoy)
#****f* sFunctions/inv_summary
# SYNTAX
#   * iter, iter100, fobjmin, fobj100, fobj0, flambda = inv_summary()
# ARGUMENTS
#   none
# RESULT
#   * int iter: number of iterations
#   * int iter100: number of iterations required to get 1.01 * min
#   * float fobjmin: minimum value of misfit function
#   * float fobj100: misfit function at iteration iter100
#   * float fobj0: misfit function before fitting
#   * float flambda: Levenberg-Marquardt multiplier
# REMARK
#   * inv_summary requires version 2016 (160309) or higher of Piccolo/Ganessa dll
# HISTORY
#   new in 1.3.4
#****
try:
    inv_summary = _dll_api.inv_summary
except AttributeError:
    _fn_undefined.append('inv_summary')
    inv_summary = _ret_errstat


#****f* sFunctions/stat_quantiles, stat_duration
# PURPOSE
#   stat_quantiles and stat_duration returns stat info associated with result TS
#   of a given attribute for all elements in a selection.
#   raw_stat_quantiles and raw_stat_duration are pass_thru versions where
#   the selection is provided as its type, buffer and length 
# SYNTAX
#   * quantiles = stat_quantiles(sel, attr, qtl)
#   * duration = stat_duration(sel, attr, sop, threshold)
#   * quantiles = raw_stat_quantiles(typelt, attr, qtl, bufsel, nb)
#   * duration = raw_stat_duration(typelt, attr, sop, threshold, bufsel, nb)
# ARGUMENTS
#   * string sel: selection of elements for which stats are expected
#   * string attr: attribute over which the stat is computed
#   * float iterable qtl: quantiles to be computed (0 <= qtl[i] <= 1)
#   * string sop: comparison operator '<' or '>'
#   * float threshold: comparison threshold (expressed in attribute unit)
#   * int typelt: selection object type
#   * int nb: selection count
#   * int[] bufsel: selection vector of indices
# RESULT
#   * float[:,:] quantiles: 2-dim array of quantiles - shape (#sel, #qtl).
#     quantiles[i] is the array of quantiles for the element in position i;
#     quantiles[:, k] is the array of quantile qtl[k] for all elements
#   * float[:] duration: array of cumulated duration (att sop threshold) - shape (#sel, ).
#   The functions return an empty list if the selection or qtl is empty .
# EXAMPLE
#   * cd = stat_duration('branch (d > 500) end', 'V', '>', 0.7)
#   * qtl = stat_quantiles('branch (d > 500) end', 'V', [0.5, 0.95, 1.0])
#     will return median, 95% quantile and maximum for velocity.
# REMARK
#   Allowed attributes are:
#   * links: flow (Q), velocity (V), head loss (PC / HL), gradient (GR)
#   * nodes: Head (HH / CH), pressure (P) and pipe pressure (PP)
#   * tanks: level (NC / CL), height (H), volume (CV / VC), volume percentage (V%),
#     flow (Q), filling flow (IQ / QR), draught flow (OQ / QV),
#   * all: water quality attributes T, C0 ... C9.
#   See also: getallminmax, getMinMax, Dynamic_stats
# HISTORY
#   * new in 1.5.0 (161124) - should be compatible with 2016b kernel.
#   * 1.8.0 (170908): added raw_stat_quantiles and raw_stat_duration
#****

try:
    _tmp_ = _dll_api.stat_quantiles
except AttributeError:
    _fn_undefined.append('stat_quantiles')
    _fn_undefined.append('stat_duration')
    stat_quantiles = _ret_errstat
    stat_duration = _ret_errstat
else:
    del _tmp_
    def stat_squantiles(sel, attr, qtl):
        if len(qtl) > 0:
            nb, _typelt = selectlen(sel)
            # vqtl = numpy.array(qtl).astype(numpy.float32, order='F')
            if nb > 0:
                ret = _dll_api.stat_squantiles(sel, attr, nb, qtl)
                return ret
        return []

    def stat_quantiles(sel, attr, qtl):
        if len(qtl) > 0:
            nb, typelt = selectlen(sel)
            if nb > 0:
                bufsel = _select(nb)
                ret = _dll_api.stat_quantiles(typelt, attr, qtl, bufsel, nb)
                # vqtl = numpy.array(qtl).astype(numpy.float32, order='F')
                return ret
        return []

    def stat_sduration(sel, attr, sop, threshold):
        nb, _typelt = selectlen(sel)
        ret = _dll_api.stat_sduration(sel, attr, sop, threshold, nb) if nb > 0 else []
        return ret

    def stat_duration(sel, attr, sop, threshold):
        nb, typelt = selectlen(sel)
        if nb > 0:
            bufsel = _select(nb)
            ret = _dll_api.stat_duration(typelt, attr, sop, threshold, bufsel, nb)
            return ret
        return []

    raw_stat_duration = _dll_api.stat_duration

#****k* sIterators/Dynamic_Stats
# PURPOSE
#   Iterator which returns stat info associated with result TS
#   of a given attribute for all elements in a selection in turn.
# SYNTAX
#   for id, retval in Dynamic_Stats(sel, attr [, quantile= qtl] [, duration= (sop, threshold)]):
# ARGUMENT
#   * string sel: selection
#   * string attr: attribute
#   * float iterable qtl: quantiles to be computed (0 <= qtl[i] <= 1)
#   * string sop: comparison operator '<' or '>'
#   * float threshold: comparison threshold (expressed in attribute unit)
# RESULT
#   Returns the id and type of each element in the selection in turn:
#   * string id: id of the next element in the selection
#   * retval: result of the requested stat.
#   The return value depends on the input parameters:
#   * if duration= (sop, threshold) is present, returns the cumulated duration for which attribute (sop) threshold.
#   * if not, if quantile= qtl is present, returns a numpy array of the quantiles for the element id.
#   * without duration and quantile keywords, the return value is [minval, maxval, avg] over the result TS.
# REMARK
#   See also getallminmax, stat_quantiles, stat_duration, getMinMax
# HISTORY
#   new in 1.5.0 (161124) - should be compatible with 2016b kernel.
#****
# Iterators for browsing model elements
class Dynamic_Stats(object):
    def __init__(self, sel, attr, quantiles= None, duration= None):
        nb, typ = selectlen(sel)
        self.nbmax, self.type = nb, typ
        if self.nbmax > 0:
            sbuf = _select(self.nbmax)
            self.select = sbuf
            if duration is not None:
                sop, threshold = duration
                self.values = _dll_api.stat_duration(typ, attr, sop, threshold, sbuf, nb)
            elif quantiles is not None:
                self.values = _dll_api.stat_quantiles(typ, attr, quantiles, sbuf, nb)
            else:
                from numpy import array as nparray
                nobj = _dll_api.nbobjects(typ)
                vmin, vmax, avg, tmin, tmax = _dll_api.getallminmax(typ, attr, nobj)
                del tmin, tmax
                vbuf = sbuf - 1
                self.values = nparray([vmin[vbuf], vmax[vbuf], avg[vbuf]]).transpose()
        self.index = 0
    def __iter__(self):
        return self
    def next(self):
        if self.index >= self.nbmax:
            if self.nbmax > 0:
                del self.select
                del self.values
                self.nbmax = 0
            raise StopIteration
        numelt = self.select[self.index]
        elem, ls = _dll_api.getid(self.type, numelt)
        value = self.values[self.index]
        self.index += 1
        return (elem[0:ls], value)
    def len(self):
        return self.nbmax
