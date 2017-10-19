# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# Copyright (C) 2014-2017 GEM Foundation
#
# OpenQuake is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# OpenQuake is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with OpenQuake. If not, see <http://www.gnu.org/licenses/>.

import re
import os
import logging
import operator
import collections

import numpy

from openquake.baselib import hdf5, parallel, performance
from openquake.baselib.general import (
    humansize, group_array, DictArray, deprecated)
from openquake.hazardlib import valid
from openquake.hazardlib.imt import from_string
from openquake.hazardlib.calc import disagg
from openquake.calculators.views import view
from openquake.calculators.export import export
from openquake.calculators.extract import convert_to_array
from openquake.risklib.riskinput import GmfGetter
from openquake.commonlib import writers, hazard_writers, calc, util, source

F32 = numpy.float32
F64 = numpy.float64
U8 = numpy.uint8
U16 = numpy.uint16
U32 = numpy.uint32


GMF_MAX_SIZE = 10 * 1024 * 1024  # 10 MB
GMF_WARNING = '''\
There are a lot of ground motion fields; the export will be slow.
Consider canceling the operation and accessing directly %s.'''

# with compression you can save 60% of space by losing only 10% of saving time
savez = numpy.savez_compressed


def get_mesh(sitecol, complete=True):
    sc = sitecol.complete if complete else sitecol
    if sc.at_sea_level():
        mesh = numpy.zeros(len(sc), [('lon', F64), ('lat', F64)])
        mesh['lon'] = sc.lons
        mesh['lat'] = sc.lats
    else:
        mesh = numpy.zeros(len(sc), [('lon', F64), ('lat', F64),
                                     ('depth', F64)])
        mesh['lon'] = sc.lons
        mesh['lat'] = sc.lats
        mesh['depth'] = sc.depths
    return mesh


@export.add(('ruptures', 'xml'))
def export_ruptures_xml(ekey, dstore):
    """
    :param ekey: export key, i.e. a pair (datastore key, fmt)
    :param dstore: datastore object
    """
    fmt = ekey[-1]
    oq = dstore['oqparam']
    events = dstore['events']
    sm_by_grp = dstore['csm_info'].get_sm_by_grp()
    mesh = get_mesh(dstore['sitecol'])
    ruptures = {}
    for grp in dstore['ruptures']:
        grp_id = int(grp[4:])  # strip grp-
        ruptures[grp_id] = []
        for ebr in calc.get_ruptures(dstore, events, grp_id):
            ruptures[grp_id].append(ebr.export(mesh, sm_by_grp))
    dest = dstore.export_path('ses.' + fmt)
    writer = hazard_writers.SESXMLWriter(dest)
    writer.serialize(ruptures, oq.investigation_time)
    return [dest]


@export.add(('ruptures', 'csv'))
def export_ruptures_csv(ekey, dstore):
    """
    :param ekey: export key, i.e. a pair (datastore key, fmt)
    :param dstore: datastore object
    """
    oq = dstore['oqparam']
    if 'scenario' in oq.calculation_mode:
        return []
    events = dstore['events']
    dest = dstore.export_path('ruptures.csv')
    header = ('rupid multiplicity mag centroid_lon centroid_lat centroid_depth'
              ' trt strike dip rake boundary').split()
    csm_info = dstore['csm_info']
    grp_trt = csm_info.grp_trt()
    gsims = csm_info.get_rlzs_assoc().gsims_by_grp_id
    rows = []
    for grp_id, trt in sorted(grp_trt.items()):
        rup_data = calc.RuptureData(trt, gsims[grp_id]).to_array(
            calc.get_ruptures(dstore, events, grp_id))
        for r in rup_data:
            rows.append(
                (r['rup_id'], r['multiplicity'], r['mag'],
                 r['lon'], r['lat'], r['depth'],
                 trt, r['strike'], r['dip'], r['rake'],
                 r['boundary']))
    rows.sort()  # by rupture serial
    writers.write_csv(dest, rows, header=header, sep='\t',
                      comment='investigation_time=%s' % oq.investigation_time)
    return [dest]


# #################### export Ground Motion fields ########################## #

class GmfSet(object):
    """
    Small wrapper around the list of Gmf objects associated to the given SES.
    """
    def __init__(self, gmfset, investigation_time, ses_idx):
        self.gmfset = gmfset
        self.investigation_time = investigation_time
        self.stochastic_event_set_id = ses_idx

    def __iter__(self):
        return iter(self.gmfset)

    def __bool__(self):
        return bool(self.gmfset)

    def __str__(self):
        return (
            'GMFsPerSES(investigation_time=%f, '
            'stochastic_event_set_id=%s,\n%s)' % (
                self.investigation_time,
                self.stochastic_event_set_id, '\n'.join(
                    sorted(str(g) for g in self.gmfset))))


class GroundMotionField(object):
    """
    The Ground Motion Field generated by the given rupture
    """
    def __init__(self, imt, sa_period, sa_damping, rupture_id, gmf_nodes):
        self.imt = imt
        self.sa_period = sa_period
        self.sa_damping = sa_damping
        self.rupture_id = rupture_id
        self.gmf_nodes = gmf_nodes

    def __iter__(self):
        return iter(self.gmf_nodes)

    def __getitem__(self, key):
        return self.gmf_nodes[key]

    def __str__(self):
        # string representation of a _GroundMotionField object showing the
        # content of the nodes (lon, lat an gmv). This is useful for debugging
        # and testing.
        mdata = ('imt=%(imt)s sa_period=%(sa_period)s '
                 'sa_damping=%(sa_damping)s rupture_id=%(rupture_id)s' %
                 vars(self))
        nodes = sorted(map(str, self.gmf_nodes))
        return 'GMF(%s\n%s)' % (mdata, '\n'.join(nodes))


class GroundMotionFieldNode(object):
    # the signature is not (gmv, x, y) because the XML writer expects
    # a location object
    def __init__(self, gmv, loc):
        self.gmv = gmv
        self.location = loc

    def __lt__(self, other):
        """
        A reproducible ordering by lon and lat; used in
        :function:`openquake.commonlib.hazard_writers.gen_gmfs`
        """
        return (self.location.x, self.location.y) < (
            other.location.x, other.location.y)

    def __str__(self):
        """Return lon, lat and gmv of the node in a compact string form"""
        return '<X=%9.5f, Y=%9.5f, GMV=%9.7f>' % (
            self.location.x, self.location.y, self.gmv)


class GmfCollection(object):
    """
    Object converting the parameters

    :param sitecol: SiteCollection
    :param ruptures: ruptures
    :param investigation_time: investigation time

    into an object with the right form for the EventBasedGMFXMLWriter.
    Iterating over a GmfCollection yields GmfSet objects.
    """
    def __init__(self, sitecol, imts, ruptures, investigation_time):
        self.sitecol = sitecol
        self.ruptures = ruptures
        self.imts = imts
        self.investigation_time = investigation_time

    def __iter__(self):
        completemesh = self.sitecol.complete.mesh
        gmfset = collections.defaultdict(list)
        for imti, imt_str in enumerate(self.imts):
            imt, sa_period, sa_damping = from_string(imt_str)
            for rupture in self.ruptures:
                gmf = rupture.gmfa['gmv'][:, imti]
                mesh = completemesh[rupture.indices]
                assert len(mesh) == len(gmf), (len(mesh), len(gmf))
                nodes = (GroundMotionFieldNode(gmv, loc)
                         for gmv, loc in zip(gmf, mesh))
                gmfset[rupture.ses_idx].append(
                    GroundMotionField(
                        imt, sa_period, sa_damping, rupture.eid, nodes))
        for ses_idx in sorted(gmfset):
            yield GmfSet(gmfset[ses_idx], self.investigation_time, ses_idx)

# ####################### export hazard curves ############################ #

HazardCurve = collections.namedtuple('HazardCurve', 'location poes')


def export_hazard_csv(key, dest, sitemesh, pmap,
                      imtls, comment):
    """
    Export the curves of the given realization into CSV.

    :param key: output_type and export_type
    :param dest: name of the exported file
    :param sitemesh: site collection
    :param pmap: a ProbabilityMap
    :param dict imtls: intensity measure types and levels
    :param comment: comment to use as header of the exported CSV file
    """
    curves = util.compose_arrays(
        sitemesh, convert_to_array(pmap, len(sitemesh), imtls))
    writers.write_csv(dest, curves, comment=comment)
    return [dest]


def add_imt(fname, imt):
    """
    >>> add_imt('/path/to/hcurve_23.csv', 'SA(0.1)')
    '/path/to/hcurve-SA(0.1)_23.csv'
    """
    name = os.path.basename(fname)
    newname = re.sub('(_\d+\.)', '-%s\\1' % imt, name)
    return os.path.join(os.path.dirname(fname), newname)


def export_hcurves_by_imt_csv(key, kind, rlzs_assoc, fname, sitecol, pmap, oq):
    """
    Export the curves of the given realization into CSV.

    :param key: output_type and export_type
    :param kind: a string with the kind of output (realization or statistics)
    :param rlzs_assoc: a :class:`openquake.commonlib.source.RlzsAssoc` instance
    :param fname: name of the exported file
    :param sitecol: site collection
    :param pmap: a probability map
    :param oq: job.ini parameters
    """
    nsites = len(sitecol)
    fnames = []
    slicedic = oq.imtls.slicedic
    for imt, imls in oq.imtls.items():
        dest = add_imt(fname, imt)
        lst = [('lon', F32), ('lat', F32), ('depth', F32)]
        for iml in imls:
            lst.append(('poe-%s' % iml, F32))
        hcurves = numpy.zeros(nsites, lst)
        for sid, lon, lat, dep in zip(
                range(nsites), sitecol.lons, sitecol.lats, sitecol.depths):
            poes = pmap.setdefault(sid, 0).array[slicedic[imt]]
            hcurves[sid] = (lon, lat, dep) + tuple(poes)
        fnames.append(writers.write_csv(dest, hcurves, comment=_comment(
            rlzs_assoc, kind, oq.investigation_time) + ',imt=%s' % imt,
                                        header=[name for (name, dt) in lst]))
    return fnames


def hazard_curve_name(dstore, ekey, kind, rlzs_assoc):
    """
    :param calc_id: the calculation ID
    :param ekey: the export key
    :param kind: the kind of key
    :param rlzs_assoc: a RlzsAssoc instance
    """
    key, fmt = ekey
    prefix = {'hcurves': 'hazard_curve', 'hmaps': 'hazard_map',
              'uhs': 'hazard_uhs'}[key]
    if kind.startswith('quantile-'):  # strip the 7 characters 'hazard_'
        fname = dstore.build_fname('quantile_' + prefix[7:], kind[9:], fmt)
    else:
        fname = dstore.build_fname(prefix, kind, fmt)
    return fname


def _comment(rlzs_assoc, kind, investigation_time):
    rlz = rlzs_assoc.get_rlz(kind)
    if not rlz:
        return '%s, investigation_time=%s' % (kind, investigation_time)
    else:
        return (
            'source_model_tree_path=%s, gsim_tree_path=%s, '
            'investigation_time=%s' % (
                rlz.sm_lt_path, rlz.gsim_lt_path, investigation_time))


@util.reader
def build_hcurves(getter, imtls, monitor):
    with getter.dstore:
        pmaps = getter.get_pmaps(getter.sids)
        idx = dict(zip(getter.sids, range(len(getter.sids))))
        curves = numpy.zeros((len(getter.sids), len(pmaps)), imtls.dt)
        for r, pmap in enumerate(pmaps):
            for sid in pmap:
                curves[idx[sid], r] = pmap[sid].convert(imtls)
    return getter.sids, curves


@export.add(('hcurves-rlzs', 'hdf5'))
@deprecated('Use `oq extract hazard/all` instead')
def export_hcurves_rlzs(ekey, dstore):
    """
    Export all hazard curves in a single .hdf5 file. This is not
    recommended, even if this exporter is parallel and very efficient.
    I was able to export 6 GB of curves per minute. However for large
    calculations it is then impossible to view the .hdf5 file with the
    hdfviewer because you will run out of memory. Also, compression is not
    enabled, otherwise all the time will be spent in the compression phase
    in the controller node with the workers doing nothing.
    The  recommended way to postprocess large computations is to instantiate
    the PmapGetter and to work one block of sites at the time,
    discarding what it is not needed. The exporter here is meant for
    small/medium calculation and as an example of what you should
    implement yourself if you need to postprocess the hazard curves.
    """
    oq = dstore['oqparam']
    imtls = oq.imtls
    rlzs_assoc = dstore['csm_info'].get_rlzs_assoc()
    sitecol = dstore['sitecol']
    pgetter = calc.PmapGetter(dstore, rlzs_assoc)
    N = len(sitecol)
    R = len(rlzs_assoc.realizations)
    fname = dstore.export_path('%s.%s' % ekey)
    monitor = performance.Monitor(ekey[0], fname)
    size = humansize(dstore.get_attr('poes', 'nbytes'))
    logging.info('Reading %s of probability maps', size)
    allargs = [(pgetter.new(tile.sids), imtls, monitor)
               for tile in sitecol.split_in_tiles(R)]
    with hdf5.File(fname, 'w') as f:
        f['imtls'] = imtls
        dset = f.create_dataset('hcurves-rlzs', (N, R), imtls.dt)
        dset.attrs['investigation_time'] = oq.investigation_time
        logging.info('Building the hazard curves for %d sites, %d rlzs', N, R)
        for sids, allcurves in parallel.Starmap(build_hcurves, allargs):
            for sid, curves in zip(sids, allcurves):
                dset[sid] = curves
    return [fname]


def get_kkf(ekey):
    """
    :param ekey: export key, for instance ('uhs/rlz-1', 'xml')
    :returns: key, kind and fmt from the export key, i.e. 'uhs', 'rlz-1', 'xml'
    """
    key, fmt = ekey
    if '/' in key:
        key, kind = key.split('/', 1)
    else:
        kind = ''
    return key, kind, fmt


@export.add(('hcurves', 'csv'), ('hmaps', 'csv'), ('uhs', 'csv'))
def export_hcurves_csv(ekey, dstore):
    """
    Exports the hazard curves into several .csv files

    :param ekey: export key, i.e. a pair (datastore key, fmt)
    :param dstore: datastore object
    """
    oq = dstore['oqparam']
    rlzs_assoc = dstore['csm_info'].get_rlzs_assoc()
    sitecol = dstore['sitecol']
    sitemesh = get_mesh(sitecol)
    key, kind, fmt = get_kkf(ekey)
    fnames = []
    if oq.poes:
        pdic = DictArray({imt: oq.poes for imt in oq.imtls})
    for kind, hcurves in calc.PmapGetter(dstore).items(kind):
        fname = hazard_curve_name(dstore, (key, fmt), kind, rlzs_assoc)
        comment = _comment(rlzs_assoc, kind, oq.investigation_time)
        if key == 'uhs' and oq.poes and oq.uniform_hazard_spectra:
            uhs_curves = calc.make_uhs(
                hcurves, oq.imtls, oq.poes, len(sitemesh))
            writers.write_csv(
                fname, util.compose_arrays(sitemesh, uhs_curves),
                comment=comment)
            fnames.append(fname)
        elif key == 'hmaps' and oq.poes and oq.hazard_maps:
            hmap = calc.make_hmap(hcurves, oq.imtls, oq.poes)
            fnames.extend(
                export_hazard_csv(ekey, fname, sitemesh, hmap, pdic, comment))
        elif key == 'hcurves':
            fnames.extend(
                export_hcurves_by_imt_csv(
                    ekey, kind, rlzs_assoc, fname, sitecol, hcurves, oq))
    return sorted(fnames)

UHS = collections.namedtuple('UHS', 'imls location')


def get_metadata(realizations, kind):
    """
    :param list realizations:
        realization objects
    :param str kind:
        kind of data, i.e. a key in the datastore
    :returns:
        a dictionary with smlt_path, gsimlt_path, statistics, quantile_value
    """
    metadata = {}
    if kind.startswith('rlz-'):
        rlz = realizations[int(kind[4:])]
        metadata['smlt_path'] = '_'.join(rlz.sm_lt_path)
        metadata['gsimlt_path'] = rlz.gsim_rlz.uid
    elif kind.startswith('quantile-'):
        metadata['statistics'] = 'quantile'
        metadata['quantile_value'] = float(kind[9:])
    elif kind == 'mean':
        metadata['statistics'] = 'mean'
    elif kind == 'max':
        metadata['statistics'] = 'max'
    return metadata


@export.add(('uhs', 'xml'))
def export_uhs_xml(ekey, dstore):
    oq = dstore['oqparam']
    rlzs_assoc = dstore['csm_info'].get_rlzs_assoc()
    pgetter = calc.PmapGetter(dstore)
    sitemesh = get_mesh(dstore['sitecol'].complete)
    key, kind, fmt = get_kkf(ekey)
    fnames = []
    periods = [imt for imt in oq.imtls if imt.startswith('SA') or imt == 'PGA']
    for kind, hcurves in pgetter.items(kind):
        metadata = get_metadata(rlzs_assoc.realizations, kind)
        _, periods = calc.get_imts_periods(oq.imtls)
        uhs = calc.make_uhs(hcurves, oq.imtls, oq.poes, len(sitemesh))
        for poe in oq.poes:
            fname = hazard_curve_name(
                dstore, (key, fmt), kind + '-%s' % poe, rlzs_assoc)
            writer = hazard_writers.UHSXMLWriter(
                fname, periods=periods, poe=poe,
                investigation_time=oq.investigation_time, **metadata)
            data = []
            for site, curve in zip(sitemesh, uhs[str(poe)]):
                data.append(UHS(curve, Location(site)))
            writer.serialize(data)
            fnames.append(fname)
    return sorted(fnames)


class Location(object):
    def __init__(self, xyz):
        self.x, self.y = tuple(xyz)[:2]
        self.wkt = 'POINT(%s %s)' % (self.x, self.y)

HazardCurve = collections.namedtuple('HazardCurve', 'location poes')
HazardMap = collections.namedtuple('HazardMap', 'lon lat iml')


@export.add(('hcurves', 'xml'), ('hcurves', 'geojson'))
def export_hcurves_xml_json(ekey, dstore):
    key, kind, fmt = get_kkf(ekey)
    len_ext = len(fmt) + 1
    oq = dstore['oqparam']
    sitemesh = get_mesh(dstore['sitecol'])
    rlzs_assoc = dstore['csm_info'].get_rlzs_assoc()
    fnames = []
    writercls = (hazard_writers.HazardCurveGeoJSONWriter
                 if fmt == 'geojson' else
                 hazard_writers.HazardCurveXMLWriter)
    for kind, hcurves in calc.PmapGetter(dstore).items(kind):
        if kind.startswith('rlz-'):
            rlz = rlzs_assoc.realizations[int(kind[4:])]
            smlt_path = '_'.join(rlz.sm_lt_path)
            gsimlt_path = rlz.gsim_rlz.uid
        else:
            smlt_path = ''
            gsimlt_path = ''
        curves = hcurves.convert(oq.imtls, len(sitemesh))
        name = hazard_curve_name(dstore, ekey, kind, rlzs_assoc)
        for imt in oq.imtls:
            imtype, sa_period, sa_damping = from_string(imt)
            fname = name[:-len_ext] + '-' + imt + '.' + fmt
            data = [HazardCurve(Location(site), poes[imt])
                    for site, poes in zip(sitemesh, curves)]
            writer = writercls(fname,
                               investigation_time=oq.investigation_time,
                               imls=oq.imtls[imt], imt=imtype,
                               sa_period=sa_period, sa_damping=sa_damping,
                               smlt_path=smlt_path, gsimlt_path=gsimlt_path)
            writer.serialize(data)
            fnames.append(fname)
    return sorted(fnames)


@export.add(('hmaps', 'xml'), ('hmaps', 'geojson'))
def export_hmaps_xml_json(ekey, dstore):
    key, kind, fmt = get_kkf(ekey)
    oq = dstore['oqparam']
    sitecol = dstore['sitecol']
    sitemesh = get_mesh(sitecol)
    rlzs_assoc = dstore['csm_info'].get_rlzs_assoc()
    fnames = []
    writercls = (hazard_writers.HazardMapGeoJSONWriter
                 if fmt == 'geojson' else
                 hazard_writers.HazardMapXMLWriter)
    pdic = DictArray({imt: oq.poes for imt in oq.imtls})
    nsites = len(sitemesh)
    for kind, hcurves in calc.PmapGetter(dstore).items():
        hmaps = calc.make_hmap(
            hcurves, oq.imtls, oq.poes).convert(pdic, nsites)
        if kind.startswith('rlz-'):
            rlz = rlzs_assoc.realizations[int(kind[4:])]
            smlt_path = '_'.join(rlz.sm_lt_path)
            gsimlt_path = rlz.gsim_rlz.uid
        else:
            smlt_path = ''
            gsimlt_path = ''
        for imt in oq.imtls:
            for j, poe in enumerate(oq.poes):
                suffix = '-%s-%s' % (poe, imt)
                fname = hazard_curve_name(
                    dstore, ekey, kind + suffix, rlzs_assoc)
                data = [HazardMap(site[0], site[1], _extract(hmap, imt, j))
                        for site, hmap in zip(sitemesh, hmaps)]
                writer = writercls(
                    fname, investigation_time=oq.investigation_time,
                    imt=imt, poe=poe,
                    smlt_path=smlt_path, gsimlt_path=gsimlt_path)
                writer.serialize(data)
                fnames.append(fname)
    return sorted(fnames)


def _extract(hmap, imt, j):
    # hmap[imt] can be a tuple or a scalar if j=0
    tup = hmap[imt]
    if hasattr(tup, '__iter__'):
        return tup[j]
    assert j == 0
    return tup


def save_np(fname, dic, mesh, *extras, **kw):
    """
    Save a dictionary of arrays as a single .npy file containing a
    structured array with fields which are they keys of the dictionary,
    plus lon/lat fields coming from the mesh.
    The length of the array is assumed to be equal to the length of the
    mesh. It is also possible to pass extra triples (field, dtype, values)
    to store additional fields.

    :param fname: .npy or .npz file name
    :param dic: dictionary of arrays of the same shape
    :param mesh: a mesh array with lon, lat fields of the same length
    :param extras: optional triples (field, dtype, values)
    :param kw: dictionary of parameters (like investigation_time)
    """
    arr = dic[next(iter(dic))]
    dtlist = [(str(field), arr.dtype) for field in sorted(dic)]
    for field, dtype, values in extras:
        dtlist.append((str(field), dtype))
    array = numpy.zeros(arr.shape, dtlist)
    for field in dic:
        array[field] = dic[field]
    for field, dtype, values in extras:
        array[field] = values
    if fname.endswith('.npy'):
        numpy.save(fname, util.compose_arrays(mesh, array))
    else:  # npz
        numpy.savez(fname, all=util.compose_arrays(mesh, array), **kw)
    return [fname]


@export.add(('hcurves', 'npz'))
def export_hcurves_np(ekey, dstore):
    oq = dstore['oqparam']
    mesh = get_mesh(dstore['sitecol'])
    fname = dstore.export_path('%s.%s' % ekey)
    dic = {}
    for kind, hcurves in calc.PmapGetter(dstore).items():
        dic[kind] = hcurves.convert_npy(oq.imtls, len(mesh))
    save_np(fname, dic, mesh, investigation_time=oq.investigation_time)
    return [fname]


@export.add(('uhs', 'npz'))
def export_uhs_np(ekey, dstore):
    oq = dstore['oqparam']
    mesh = get_mesh(dstore['sitecol'])
    fname = dstore.export_path('%s.%s' % ekey)
    dic = {}
    for kind, hcurves in calc.PmapGetter(dstore).items():
        dic[kind] = calc.make_uhs(hcurves, oq.imtls, oq.poes, len(mesh))
    save_np(fname, dic, mesh, investigation_time=oq.investigation_time)
    return [fname]


@export.add(('hmaps', 'npz'))
def export_hmaps_np(ekey, dstore):
    oq = dstore['oqparam']
    sitecol = dstore['sitecol']
    mesh = get_mesh(sitecol)
    pdic = DictArray({imt: oq.poes for imt in oq.imtls})
    fname = dstore.export_path('%s.%s' % ekey)
    dic = {}
    for kind, hcurves in calc.PmapGetter(dstore).items():
        hmap = calc.make_hmap(hcurves, oq.imtls, oq.poes)
        dic[kind] = convert_to_array(hmap, len(mesh), pdic)
    save_np(fname, dic, mesh, ('vs30', F32, sitecol.vs30),
            investigation_time=oq.investigation_time)
    return [fname]


@export.add(('gmf_data', 'xml'))
def export_gmf(ekey, dstore):
    """
    :param ekey: export key, i.e. a pair (datastore key, fmt)
    :param dstore: datastore object
    """
    sitecol = dstore['sitecol']
    oq = dstore['oqparam']
    investigation_time = (None if oq.calculation_mode == 'scenario'
                          else oq.investigation_time)
    fmt = ekey[-1]
    gmf_data = dstore['gmf_data']
    nbytes = gmf_data.attrs['nbytes']
    logging.info('Internal size of the GMFs: %s', humansize(nbytes))
    if nbytes > GMF_MAX_SIZE:
        logging.warn(GMF_WARNING, dstore.hdf5path)
    fnames = []
    ruptures_by_rlz = collections.defaultdict(list)
    data = gmf_data['data'].value
    events = dstore['events'].value
    eventdict = dict(zip(events['eid'], events))
    for rlzi, gmf_arr in group_array(data, 'rlzi').items():
        ruptures = ruptures_by_rlz[rlzi]
        for eid, gmfa in group_array(gmf_arr, 'eid').items():
            ses_idx = eventdict[eid]['ses']
            rup = Rup(eid, ses_idx, sorted(set(gmfa['sid'])), gmfa)
            ruptures.append(rup)
    rlzs = dstore['csm_info'].get_rlzs_assoc().realizations
    for rlzi in sorted(ruptures_by_rlz):
        ruptures_by_rlz[rlzi].sort(key=operator.attrgetter('eid'))
        fname = dstore.build_fname('gmf', rlzi, fmt)
        fnames.append(fname)
        globals()['export_gmf_%s' % fmt](
            ('gmf', fmt), fname, sitecol, oq.imtls, ruptures_by_rlz[rlzi],
            rlzs[rlzi], investigation_time)
    return fnames


Rup = collections.namedtuple('Rup', ['eid', 'ses_idx', 'indices', 'gmfa'])


def export_gmf_xml(key, dest, sitecol, imts, ruptures, rlz,
                   investigation_time):
    """
    :param key: output_type and export_type
    :param dest: name of the exported file
    :param sitecol: the full site collection
    :param imts: the list of intensity measure types
    :param ruptures: an ordered list of ruptures
    :param rlz: a realization object
    :param investigation_time: investigation time (None for scenario)
    """
    if hasattr(rlz, 'gsim_rlz'):  # event based
        smltpath = '_'.join(rlz.sm_lt_path)
        gsimpath = rlz.gsim_rlz.uid
    else:  # scenario
        smltpath = ''
        gsimpath = rlz.uid
    writer = hazard_writers.EventBasedGMFXMLWriter(
        dest, sm_lt_path=smltpath, gsim_lt_path=gsimpath)
    writer.serialize(
        GmfCollection(sitecol, imts, ruptures, investigation_time))
    return {key: [dest]}


@export.add(('gmf_data', 'csv'))
def export_gmf_data_csv(ekey, dstore):
    oq = dstore['oqparam']
    rlzs_assoc = dstore['csm_info'].get_rlzs_assoc()
    imts = list(oq.imtls)
    sitemesh = get_mesh(dstore['sitecol'])
    eid = int(ekey[0].split('/')[1]) if '/' in ekey[0] else None
    gmfa = dstore['gmf_data']['data'].value
    if eid is None:  # new format
        f = dstore.build_fname('sitemesh', '', 'csv')
        sids = numpy.arange(len(sitemesh), dtype=U32)
        sites = util.compose_arrays(sids, sitemesh, 'site_id')
        writers.write_csv(f, sites)
        fname = dstore.build_fname('gmf', 'data', 'csv')
        gmfa.sort(order=['rlzi', 'sid', 'eid'])
        writers.write_csv(fname, _expand_gmv(gmfa, imts))
        return [fname, f]
    # old format for single eid
    gmfa = gmfa[gmfa['eid'] == eid]
    fnames = []
    for rlzi, array in group_array(gmfa, 'rlzi').items():
        rlz = rlzs_assoc.realizations[rlzi]
        data, comment = _build_csv_data(
            array, rlz, dstore['sitecol'], imts, oq.investigation_time)
        fname = dstore.build_fname(
            'gmf', '%d-rlz-%03d' % (eid, rlzi), 'csv')
        writers.write_csv(fname, data, comment=comment)
        fnames.append(fname)
    return fnames


def _expand_gmv(array, imts):
    # the array-field gmv becomes a set of scalar fields gmv_<imt>
    dtype = array.dtype
    assert dtype['gmv'].shape[0] == len(imts)
    dtlist = []
    for name in dtype.names:
        dt = dtype[name]
        if name == 'gmv':
            for imt in imts:
                dtlist.append(('gmv_' + imt, F32))
        else:
            dtlist.append((name, dt))
    return array.view(dtlist)


def _build_csv_data(array, rlz, sitecol, imts, investigation_time):
    # lon, lat, gmv_imt1, ..., gmv_imtN
    smlt_path = '_'.join(rlz.sm_lt_path)
    gsimlt_path = rlz.gsim_rlz.uid
    comment = ('smlt_path=%s, gsimlt_path=%s, investigation_time=%s' %
               (smlt_path, gsimlt_path, investigation_time))
    rows = [['lon', 'lat'] + imts]
    for sid, data in group_array(array, 'sid').items():
        row = ['%.5f' % sitecol.lons[sid], '%.5f' % sitecol.lats[sid]] + list(
            data['gmv'])
        rows.append(row)
    return rows, comment


@export.add(('gmf_scenario', 'csv'))
def export_gmf_scenario_csv(ekey, dstore):
    what = ekey[0].split('/')
    if len(what) == 1:
        raise ValueError('Missing "/rup-\d+"')
    oq = dstore['oqparam']
    csm_info = dstore['csm_info']
    rlzs_assoc = csm_info.get_rlzs_assoc()
    samples = csm_info.get_samples_by_grp()
    imts = list(oq.imtls)
    mo = re.match('rup-(\d+)$', what[1])
    if mo is None:
        raise ValueError(
            "Invalid format: %r does not match 'rup-(\d+)$'" % what[1])
    rup_id = int(mo.group(1))
    grp_ids = sorted(int(grp[4:]) for grp in dstore['ruptures'])
    events = dstore['events']
    ruptures = list(calc._get_ruptures(dstore, events, grp_ids, rup_id))
    if not ruptures:
        logging.warn('There is no rupture %d', rup_id)
        return []
    [ebr] = ruptures
    rlzs_by_gsim = rlzs_assoc.rlzs_by_gsim[ebr.grp_id]
    samples = samples[ebr.grp_id]
    min_iml = calc.fix_minimum_intensity(oq.minimum_intensity, imts)
    correl_model = oq.get_correl_model()
    sitecol = dstore['sitecol'].complete
    getter = GmfGetter(
        rlzs_by_gsim, ruptures, sitecol, imts,
        min_iml, oq.truncation_level, correl_model, samples)
    getter.init()
    hazardr = getter.get_hazard()
    rlzs = rlzs_assoc.realizations
    fields = ['eid-%03d' % eid for eid in getter.eids]
    dt = numpy.dtype([(f, F32) for f in fields])
    mesh = numpy.zeros(len(ebr.sids), [('lon', F64), ('lat', F64)])
    mesh['lon'] = sitecol.lons[ebr.sids]
    mesh['lat'] = sitecol.lats[ebr.sids]
    writer = writers.CsvWriter(fmt='%.5f')
    for rlzi in range(len(rlzs)):
        hazard = hazardr[rlzi]
        for imti, imt in enumerate(imts):
            gmfs = numpy.zeros(len(ebr.sids), dt)
            for s, sid in enumerate(ebr.sids):
                for rec in hazard[sid]:
                    event = 'eid-%03d' % rec['eid']
                    gmfs[s][event] = rec['gmv'][imti]
            dest = dstore.build_fname(
                'gmf', 'rup-%s-rlz-%s-%s' % (rup_id, rlzi, imt), 'csv')
            data = util.compose_arrays(mesh, gmfs)
            writer.save(data, dest)
    return writer.getsaved()


def _gmf_scenario(data, num_sites, imts):
    # convert data into the composite array expected by QGIS
    eids = sorted(numpy.unique(data['eid']))
    eid2idx = {eid: idx for idx, eid in enumerate(eids)}
    E = len(eid2idx)
    gmf_dt = numpy.dtype([(imt, (F32, (E,))) for imt in imts])
    gmfa = numpy.zeros(num_sites, gmf_dt)
    for rec in data:
        arr = gmfa[rec['sid']]
        for imt, gmv in zip(imts, rec['gmv']):
            arr[imt][eid2idx[rec['eid']]] = gmv
    return gmfa, E


@export.add(('gmf_data', 'npz'))
def export_gmf_scenario_npz(ekey, dstore):
    dic = {}
    oq = dstore['oqparam']
    mesh = get_mesh(dstore['sitecol'])
    n = len(mesh)
    fname = dstore.export_path('%s.%s' % ekey)
    if 'gmf_data' in dstore:
        data_by_rlzi = group_array(dstore['gmf_data/data'].value, 'rlzi')
        for rlzi in data_by_rlzi:
            gmfa, e = _gmf_scenario(data_by_rlzi[rlzi], n, oq.imtls)
            logging.info('Exporting array of shape %s for rlz %d',
                         (n, e), rlzi)
            dic['rlz-%03d' % rlzi] = util.compose_arrays(mesh, gmfa)
    else:  # nothing to export
        return []
    savez(fname, **dic)
    return [fname]


DisaggMatrix = collections.namedtuple(
    'DisaggMatrix', 'poe iml dim_labels matrix')


@export.add(('disagg', 'xml'))
def export_disagg_xml(ekey, dstore):
    oq = dstore['oqparam']
    rlzs = dstore['csm_info'].get_rlzs_assoc().realizations
    group = dstore['disagg']
    fnames = []
    writercls = hazard_writers.DisaggXMLWriter
    for key in group:
        matrix = dstore['disagg/' + key]
        attrs = group[key].attrs
        rlz = rlzs[attrs['rlzi']]
        poe = attrs['poe']
        iml = attrs['iml']
        imt, sa_period, sa_damping = from_string(attrs['imt'])
        fname = dstore.export_path(key + '.xml')
        lon, lat = attrs['location']
        # TODO: add poe=poe below
        writer = writercls(
            fname, investigation_time=oq.investigation_time,
            imt=imt, smlt_path='_'.join(rlz.sm_lt_path),
            gsimlt_path=rlz.gsim_rlz.uid, lon=lon, lat=lat,
            sa_period=sa_period, sa_damping=sa_damping,
            mag_bin_edges=attrs['mag_bin_edges'],
            dist_bin_edges=attrs['dist_bin_edges'],
            lon_bin_edges=attrs['lon_bin_edges'],
            lat_bin_edges=attrs['lat_bin_edges'],
            eps_bin_edges=attrs['eps_bin_edges'],
            tectonic_region_types=attrs['trts'],
        )
        data = [
            DisaggMatrix(poe, iml, dim_labels, matrix['_'.join(dim_labels)])
            for i, dim_labels in enumerate(disagg.pmf_map)]
        writer.serialize(data)
        fnames.append(fname)
    return sorted(fnames)


# adapted from the nrml_converters
def save_disagg_to_csv(metadata, matrices):
    """
    Save disaggregation matrices to multiple .csv files.
    """
    skip_keys = ('Mag', 'Dist', 'Lon', 'Lat', 'Eps', 'TRT')
    base_header = ','.join(
        '%s=%s' % (key, value) for key, value in metadata.items()
        if value is not None and key not in skip_keys)
    for disag_tup, (poe, iml, matrix, fname) in matrices.items():
        header = '%s,poe=%s,iml=%s\n' % (base_header, poe, iml)

        if disag_tup == ('Mag', 'Lon', 'Lat'):
            matrix = numpy.swapaxes(matrix, 0, 1)
            matrix = numpy.swapaxes(matrix, 1, 2)
            disag_tup = ('Lon', 'Lat', 'Mag')

        axis = [metadata[v] for v in disag_tup]
        header += ','.join(v for v in disag_tup)
        header += ',poe'

        # compute axis mid points
        axis = [(ax[: -1] + ax[1:]) / 2. if ax.dtype == float
                else ax for ax in axis]

        values = None
        if len(axis) == 1:
            values = numpy.array([axis[0], matrix.flatten()]).T
        else:
            grids = numpy.meshgrid(*axis, indexing='ij')
            values = [g.flatten() for g in grids]
            values.append(matrix.flatten())
            values = numpy.array(values).T

        writers.write_csv(fname, values, comment=header, fmt='%.5E')


@export.add(('disagg', 'csv'))
def export_disagg_csv(ekey, dstore):
    oq = dstore['oqparam']
    disagg_outputs = oq.disagg_outputs or valid.disagg_outs
    rlzs = dstore['csm_info'].get_rlzs_assoc().realizations
    group = dstore['disagg']
    fnames = []
    for key in group:
        matrix = dstore['disagg/' + key]
        attrs = group[key].attrs
        rlz = rlzs[attrs['rlzi']]
        poe = attrs['poe']
        iml = attrs['iml']
        imt, sa_period, sa_damping = from_string(attrs['imt'])
        lon, lat = attrs['location']
        metadata = collections.OrderedDict()
        # Loads "disaggMatrices" nodes
        metadata['smlt_path'] = '_'.join(rlz.sm_lt_path)
        metadata['gsimlt_path'] = rlz.gsim_rlz.uid
        metadata['imt'] = imt
        metadata['investigation_time'] = oq.investigation_time
        metadata['lon'] = lon
        metadata['lat'] = lat
        metadata['Mag'] = attrs['mag_bin_edges']
        metadata['Dist'] = attrs['dist_bin_edges']
        metadata['Lon'] = attrs['lon_bin_edges']
        metadata['Lat'] = attrs['lat_bin_edges']
        metadata['Eps'] = attrs['eps_bin_edges']
        metadata['TRT'] = attrs['trts']
        data = {}
        for label in disagg_outputs:
            tup = tuple(label.split('_'))
            fname = dstore.export_path(key + '_%s.csv' % label)
            data[tup] = poe, iml, matrix[label].value, fname
            fnames.append(fname)
        save_disagg_to_csv(metadata, data)
    return fnames


@export.add(('realizations', 'csv'))
def export_realizations(ekey, dstore):
    rlzs = dstore[ekey[0]]
    data = [['ordinal', 'uid', 'model', 'gsim', 'weight']]
    for i, rlz in enumerate(rlzs):
        data.append([i, rlz['uid'], rlz['model'], rlz['gsims'], rlz['weight']])
    path = dstore.export_path('realizations.csv')
    writers.write_csv(path, data, fmt='%s')
    return [path]


@export.add(('sourcegroups', 'csv'))
def export_sourcegroups(ekey, dstore):
    csm_info = dstore['csm_info']
    data = [['grp_id', 'trt', 'eff_ruptures']]
    for i, sm in enumerate(csm_info.source_models):
        for src_group in sm.src_groups:
            trt = source.capitalize(src_group.trt)
            er = src_group.eff_ruptures
            data.append((src_group.id, trt, er))
    path = dstore.export_path('sourcegroups.csv')
    writers.write_csv(path, data, fmt='%s')
    return [path]


# because of the code in server.views.calc_results we are not visualizing
# .txt outputs, so we use .rst here
@export.add(('fullreport', 'rst'))
def export_fullreport(ekey, dstore):
    with open(dstore.export_path('report.rst'), 'w') as f:
        f.write(view('fullreport', dstore))
    return [f.name]
