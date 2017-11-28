from numpy import argsort as numpy_argsort
from numpy import dtype   as numpy_dtype
from numpy import sort    as numpy_sort

from operator  import attrgetter, itemgetter
from itertools import izip

#from .ancillaryvariables  import AncillaryVariables
#from .comparison          import gt
from .coordinate          import AuxiliaryCoordinate
from .coordinatereference import CoordinateReference
from .domainaxis          import DomainAxis
from .field               import Field, FieldList
from .query               import gt
from .units               import Units
from .functions           import (flat, RTOL, ATOL, equals, hash_array, allclose,
                                  _numpy_allclose)
from .functions           import inspect as cf_inspect

from .data.data      import Data
from .data.filearray import FileArray

_dtype_float = numpy_dtype(float)

## --------------------------------------------------------------------
## Global properties, as defined in Appendix A of the CF conventions.
## --------------------------------------------------------------------
#_global_properties = set(('comment',
#                          'Conventions',
#                          'history',
#                          'institution',
#                          'references',
#                          'source',
#                          'title',
#                          ))

# --------------------------------------------------------------------
# Data variable properties, as defined in Appendix A of the CF
# conventions, without those which are not simple. And less
# 'long_name'.
# --------------------------------------------------------------------
_signature_properties = set(('add_offset',
                             'calendar',
                             'cell_methods',
                             '_FillValue',
                             'flag_masks',
                             'flag_meanings',
                             'flag_values',
                             'missing_value',
                             'scale_factor',
                             'standard_error_multiplier',
                             'standard_name',
                             'units',
                             'valid_max',
                             'valid_min',
                             'valid_range',
                             ))

#_standard_properties = _data_properties.union(_global_properties)

_no_units = Units()


class _HFLCache(object):
    '''

A cache for coordinate and cell measure hashes, first and last values
and first and last cell bounds

'''
    def __init__(self):
        self.hash = {}
        self.fl   = {}
        self.flb  = {}
        self.hash_to_array = {}
    #--- End: def

    def inspect(self):
        '''

Inspect the object for debugging.

.. seealso:: `cf.inspect`

:Returns: 

    None

:Examples:

>>> f.inspect()

'''
        print cf_inspect(self)
    #--- End: def

#--- End: class


class _Meta(object):
    '''

A summary of a field.

This object contains everything you need to know in order to aggregate
the field.

'''
    #
    _canonical_units = {}

    #
    _canonical_cell_methods = []

    def __init__(self, f,
                 rtol=None, atol=None,
                 info=0,
                 relaxed_units=False,
                 allow_no_identity=False,
                 respect_valid=False,
                 equal_all=False,
                 exist_all=False,
                 equal=None,
                 exist=None,
                 ignore=None,
                 dimension=(),
                 relaxed_identities=False,
                 ncvar_identities=False):
        '''

**initialization**

:Parameters:

    f: `cf.Field`

    info: `int`, optional
        See the `aggregate` function for details.

    relaxed_units: `bool`, optional
        See the `aggregate` function for details.

    allow_no_identity: `bool`, optional
        See the `aggregate` function for details.

    rtol: `float`, optional
        See the `aggregate` function for details.

    atol: `float`, optional
        See the `aggregate` function for details.
   
    dimension: (sequence of) `str`, optional
        See the `aggregate` function for details.

:Examples:

'''
        self._nonzero    = False
        self.cell_values = False

        self.info            = info

        self.sort_indices    = {}
        self.sort_keys       = {}
        self.key_to_identity = {}

        self.all_field_anc_identities  = set()
        self.all_domain_anc_identities = set()

        self.message = ''

        strict_identities = not (relaxed_identities or ncvar_identities)
#        self.strict_identities = strict_identities
#        self.ncvar_identities  = ncvar_identities
        self.relaxed_identities = relaxed_identities
        self.strict_identities  = strict_identities
        self.ncvar_identities   = ncvar_identities

        # Initialize the flag which indicates whether or not this
        # field has already been aggregated
        self.aggregated_field = False

        # Map axis canonical identities to their identifiers
        #
        # For example: {'time': 'dim2'}
        self.id_to_axis = {}
        
        # Map axis identifiers to their canonical identities
        #
        # For example: {'dim2': 'time'}
        self.axis_to_id = {}

        # ------------------------------------------------------------
        # Field
        # ------------------------------------------------------------
        self.field    = f
        self._hasData = f._hasData
        self.identity = f.name(identity=strict_identities,
                               ncvar=ncvar_identities)

        # ------------------------------------------------------------
        #
        # ------------------------------------------------------------
        signature_override = getattr(f, 'aggregate', None)
        if signature_override is not None:
            self.signature = signature_override
            self._nonzero = True
            return

        if self.identity is None:
            if not allow_no_identity and self._hasData:
                if info:
                    self.message = \
"no identity; consider setting relaxed_identities"
                return
        elif not self._hasData:
            if info:
                self.message = \
"no data array"
            return
        #--- End: if

        items = f.items
        item  = f.item
 
        # ------------------------------------------------------------
        # Promote selected properties to 1-d, size 1 auxiliary
        # coordinates
        # ------------------------------------------------------------
        for prop in dimension:
            value = f.getprop(prop, None)
            if value is None:
                continue

            aux_coord = AuxiliaryCoordinate(properties={'long_name': prop},
                                            attributes={'id'   : prop,
                                                        'ncvar': prop},
                                            data=Data([value], units=''),
                                            copy=False)
            axis = f.insert_axis(DomainAxis(1))
            f.insert_aux(aux_coord, axes=[axis], copy=False)

            f.delprop(prop) ### dch COPY issue?
        #--- End: for

        self.units = self.canonical_units(f, self.identity,
                                          relaxed_units=relaxed_units)

        # ------------------------------------------------------------
        # Coordinate and cell measure arrays
        # ------------------------------------------------------------
        self.hash_values  = {}
        self.first_values = {}
        self.last_values  = {}
        self.first_bounds = {}
        self.last_bounds  = {}

        # Dictionaries mapping auxiliary coordinate identifiers
        # to their auxiliary coordinate objects
        aux_1d = items(role='a', ndim=1)
            
        # A set containing the identity of each coordinate
        #
        # For example: set(['time', 'height', 'latitude',
        # 'longitude'])
        self.all_coord_identities = set()

        self.axis = {}


        # ------------------------------------------------------------
        # Coordinate references (formula_terms and grid mappings)
        # ------------------------------------------------------------
        refs = f.refs()
        if not refs:
            self.coordrefs = ()
        else:
            self.coordrefs = refs.values()

        for axis in f.axes():
    
            # List some information about each 1-d coordinate which
            # spans this axis. The order of elements is arbitrary, as
            # ultimately it will get sorted by each element's 'name'
            # key values.
            #
            # For example: [{'name': 'time', 'key': 'dim0', 'units':
            # <CF Units: ...>}, {'name': 'forecast_ref_time', 'key':
            # 'aux0', 'units': <CF Units: ...>}]
            info_dim = []

            dim_coord = item(axis)

            if dim_coord is not None:
                # ----------------------------------------------------
                # 1-d dimension coordinate
                # ----------------------------------------------------
                identity = self.coord_has_identity_and_data(dim_coord)

                if identity is None:
                    return

                # Find the canonical units for this dimension
                # coordinate
                units = self.canonical_units(dim_coord, identity,
                                             relaxed_units=relaxed_units)
    
                info_dim.append(
                    {'identity' : identity,
                     'key'      : axis,
                     'units'    : units,
                     'hasbounds': dim_coord._hasbounds,
                     'coordrefs': self.find_coordrefs(axis)})
#                     'size'     : None})
            #--- End: if
    
            # Find the 1-d auxiliary coordinates which span this axis
            aux_coords = {}
            for aux in aux_1d.keys():
                if axis in f.item_axes(aux): #dimensions[aux]:
                    aux_coords[aux] = aux_1d.pop(aux)
            #--- End: for
    
            info_aux = []
            for key, aux_coord in aux_coords.iteritems():
                # ----------------------------------------------------
                # 1-d auxiliary coordinate
                # ----------------------------------------------------
                identity = self.coord_has_identity_and_data(aux_coord)
                if identity is None:
                    return
    
                # Find the canonical units for this 1-d auxiliary
                # coordinate
                units = self.canonical_units(aux_coord, identity,
                                             relaxed_units=relaxed_units)

                info_aux.append(
                    {'identity' : identity,
                     'key'      : key,
                     'units'    : units,
                     'hasbounds': aux_coord._hasbounds,
                     'coordrefs': self.find_coordrefs(key)})
#                     'size'     : None})
            #--- End: for
    
            # Sort the 1-d auxiliary coordinate information
            info_aux.sort(key=itemgetter('identity'))
    
            # Prepend the dimension coordinate information to the
            # auxiliary coordinate information
            info_1d_coord = info_dim + info_aux

#            if not info_1d_coord:
#                if info:
#                    self.message ="\
#axis has no one-dimensional nor scalar coordinates"
#
#                return
#            #--- End: if

            # Find the canonical identity for this axis
            identity = None
            if info_1d_coord:
                identity = info_1d_coord[0]['identity']
            elif not self.relaxed_identities:
                if info:
                    self.message = "\
axis has no one-dimensional nor scalar coordinates"

                return
            #--- End: if
            
            ncdim = False
            if identity is None and self.relaxed_identities:
                # There are no 1-d coordinates, so see if we can
                # identify the domain axis by their netCDF dimension
                # name.
                domain_axis = f.axis(axis)
                identity = getattr(domain_axis, 'ncdim', None)
                if identity is None:
                    if info:
                        self.message = "\
axis {0!r} has no netCDF dimension name".format(f.axis_name(axis))

                    return
                else:
                    ncdim = True
            #--- End: if

            self.axis[identity] = \
                {'ids'      : tuple([i['identity']  for i in info_1d_coord]),
                 'keys'     : tuple([i['key']       for i in info_1d_coord]),
                 'units'    : tuple([i['units']     for i in info_1d_coord]),
                 'hasbounds': tuple([i['hasbounds'] for i in info_1d_coord]),
                 'coordrefs': tuple([i['coordrefs'] for i in info_1d_coord])}
#                 'size'     : None} #tuple([i['size']      for i in info_1d_coord])}        

            if info_dim:
                self.axis[identity]['dim_coord_index'] = 0
            else:
                self.axis[identity]['dim_coord_index'] = None

            # Store the axis size if the axis has no 1-d coordinates
            if ncdim:
                self.axis[identity]['size'] = domain_axis.size
            else:
                self.axis[identity]['size'] = None

            self.id_to_axis[identity] = axis
            self.axis_to_id[axis]     = identity
        #--- End: for
    
        # Create a sorted list of the axes' canonical identities
        #
        # For example: ['latitude', 'longitude', 'time']
        self.axis_ids = sorted(self.axis)

        # ------------------------------------------------------------
        # N-d auxiliary coordinates
        # ------------------------------------------------------------
        self.nd_aux = {}
        for key, nd_aux_coord in items(role='a', ndim=gt(1)).iteritems():
           
            # Find this N-d auxiliary coordinate's identity
            identity = self.coord_has_identity_and_data(nd_aux_coord)
            if identity is None:
                return

            # Find the canonical units
            units = self.canonical_units(nd_aux_coord, identity,
                                         relaxed_units=relaxed_units)
            
            # Find axes' canonical identities
            axes = [self.axis_to_id[axis] for axis in f.item_axes(key)]
            axes = tuple(sorted(axes))

            self.nd_aux[identity] = {
                'key'      : key,
                'units'    : units,
                'axes'     : axes,
                'hasbounds': nd_aux_coord._hasbounds,
                'coordrefs': self.find_coordrefs(key)}
        #--- End: for

        # ------------------------------------------------------------
        # Cell methods
        # ------------------------------------------------------------
        self.cell_methods = self.canonical_cell_methods(rtol=rtol, atol=atol)

        # ------------------------------------------------------------
        # Field ancillaries
        # ------------------------------------------------------------
        self.field_anc = {}
        for key, field_anc in items(role='f').iteritems():
           
            # Find this field ancillary's identity
            identity = self.field_ancillary_has_identity_and_data(field_anc)
            if identity is None:
                return

            # Find the canonical units
            units = self.canonical_units(field_anc, identity,
                                         relaxed_units=relaxed_units)
            
            # Find axes' canonical identities
            axes = [self.axis_to_id[axis] for axis in f.item_axes(key)]
            axes = tuple(sorted(axes))

            self.field_anc[identity] = {'key'  : key,
                                        'units': units,
                                        'axes' : axes}
        #--- End: for

        # ------------------------------------------------------------
        # Coordinate reference structural signatures. (Do this after
        # self.key_to_identity has been populated with domain
        # ancillary keys.)
        # ------------------------------------------------------------
        self.coordref_signatures = self.coordinate_reference_signatures(self.coordrefs)

        # ------------------------------------------------------------
        # Domain ancillaries
        # ------------------------------------------------------------
        self.domain_anc = {}

        # List of keys of domain ancillaries which are used in
        # coordinate references
        ancs_in_refs = []

        # Firstly process domain ancillaries which are used in
        # coordinate references
        for ref in f.refs().values():
            for term, identifier in ref.ancillaries.iteritems():
                key = item(identifier, role=('c',), exact=True, key=True)
                if key is None:
                    continue

                anc = f.item(key)
                
                # Set this domain ancillary's identity
                identity = (ref.name(), term)
                identity = self.domain_ancillary_has_identity_and_data(anc, identity)

                # Find the canonical units
                units = self.canonical_units(anc, identity,
                                             relaxed_units=relaxed_units)
                
                # Find the canonical identities of the axes
                axes = [self.axis_to_id[axis] for axis in f.item_axes(key)]
                axes = tuple(sorted(axes))
                
                self.domain_anc[identity] = {'key'  : key,
                                             'units': units,
                                             'axes' : axes}
                
                self.key_to_identity[key] = identity
            
                ancs_in_refs.append(key)
            #--- End: for
        #--- End: for

        # Secondly process domain ancillaries which are not being used
        # in coordinate references
        for key, anc in items(role='c').iteritems():
            if key in ancs_in_refs:
                continue
                
            # Find this domain ancillary's identity
            identity = self.domain_ancillary_has_identity_and_data(anc)
            if identity is None:
                return

            # Find the canonical units
            units = self.canonical_units(anc, identity,
                                         relaxed_units=relaxed_units)
            
            # Find the canonical identities of the axes
            axes = [self.axis_to_id[axis] for axis in f.item_axes(key)]
            axes = tuple(sorted(axes))

            self.domain_anc[identity] = {
                'key'      : key,
                'units'    : units,
                'axes'     : axes,
            }

            self.key_to_identity[key] = identity
        #--- End: 
        
        # ------------------------------------------------------------
        # Cell measures
        # ------------------------------------------------------------
        self.msr = {}
        info_msr = {}
        for key, msr in items(role='m').iteritems():
            
            if not self.cell_measure_has_data_and_units(msr):
                return

            # Find the canonical units for this cell measure
            units = self.canonical_units(msr,
                                         msr.name(identity=strict_identities,
                                                  ncvar=ncvar_identities),
                                         relaxed_units=relaxed_units)
            
            # Find axes' canonical identities
            axes = [self.axis_to_id[axis] for axis in f.item_axes(key)]
            axes = tuple(sorted(axes))
            
            if units in info_msr:
                # Check for ambiguous cell measures, i.e. those which
                # have the same units and span the same axes.
                for value in info_msr[units]:
                    if axes == value['axes']:
                        if info:
                           self.message = \
"duplicate {0!r}".format(msr)
                        return
            else:
                info_msr[units] = []
            #--- End: if
    
            info_msr[units].append({'key' : key,
                                    'axes': axes})
        #--- End: for
    
        # For each cell measure's canonical units, sort the
        # information by axis identities.
        for units, value in info_msr.iteritems():
            value.sort(key=itemgetter('axes'))        
            self.msr[units] = {'keys': tuple([v['key']  for v in value]),
                               'axes': tuple([v['axes'] for v in value])}
        #--- End: for

        # ------------------------------------------------------------
        # Properties and attributes
        # ------------------------------------------------------------
        if not (equal or exist or equal_all or exist_all):
            self.properties = ()
        else:
            properties = f.properties()
            for p in ignore:
                properties.pop(p, None)

            if equal:
                eq = dict([(p, properties[p]) for p in equal
                           if p in properties])
            else:
                eq = {}

            if exist:
                ex = [p for p in exist if p in properties]
            else:
                ex = []

            eq_all = {}
            ex_all = []

            if equal_all or exist_all:
                if equal_all:
                    if not equal and not exist:
                        eq_all = properties
                    elif equal and exist:
                        eq_all = dict([(p, properties[p]) for p in properties
                                       if p not in ex and p not in eq])
                    elif equal:
                        eq_all = dict([(p, properties[p]) for p in properties
                                       if p not in eq])
                    elif exist:
                        eq_all = dict([(p, properties[p]) for p in properties
                                       if p not in ex])
                
                elif exist_all:
                    if not equal and not exist:
                         ex_all = list(properties)
                    elif equal and exist:
                        ex_all = [p for p in properties
                                  if p not in ex and p not in eq]
                    elif equal:
                        ex_all = [p for p in properties if p not in eq]
                    elif exist:
                        ex_all = [p for p in properties if p not in ex]
            #--- End: if

            self.properties = tuple(sorted(ex_all + ex +
                                           eq_all.items() + eq.items()))
        #--- End: if

        # Attributes
        self.attributes = set(('file',))

        # ------------------------------------------------------------
        # Still here? Then create the structural signature.
        # ------------------------------------------------------------
        self.respect_valid = respect_valid
        self.structural_signature()

        # Initialize the flag which indicates whether or not this
        # field has already been aggregated
        self.aggregated_field = False

        self.sort_indices = {}
        self.sort_keys    = {}
  
        # Finally, set the object to True
        self._nonzero = True
    #--- End: def

    def __nonzero__(self):
        '''

x.__nonzero__() <==> bool(x)

'''
        return self._nonzero
    #--- End: if

    def __repr__(self):
        '''

x.__repr__() <==> repr(x)

'''
        return '<CF %s: %r>' % (self.__class__.__name__,
                                getattr(self, 'field', None))
    #--- End: def

    def __str__(self):
        '''

x.__str__() <==> str(x)

'''
        strings = []
        for attr in sorted(self.__dict__):
            strings.append('%s.%s = %r' % (self.__class__.__name__, attr,
                                           getattr(self, attr)))
            
        return '\n'.join(strings)
    #--- End: def

    def coordinate_values(self):
        '''
'''
        string =     ['First cell: '+str(self.first_values)]
        string.append('Last cell:  '+str(self.last_values))
        string.append('First bounds: '    +str(self.first_bounds))
        string.append('Last bounds:  '    +str(self.last_bounds))

        return '\n'.join(string)                           
    #--- End: def

    def copy(self):
        '''
'''
        new = _Meta.__new__(_Meta)
        new.__dict__ = self.__dict__.copy()
        new.field = new.field.copy()
        return new

    def canonical_units(self, variable, identity, relaxed_units=False):
        '''

Updates the `_canonical_units` attribute.

:Parameters:

    variable : cf.Variable

    identity : str

    relaxed_units : bool 
        See the `cf.aggregate` for details.

:Returns:

    out : cf.Units or None

:Examples:

'''
        var_units = variable.Units

        _canonical_units = self._canonical_units

        if identity in _canonical_units:
            if var_units:
                for u in _canonical_units[identity]:
                    if var_units.equivalent(u):
                        return u
                #--- End: for
    
                # Still here?
                _canonical_units[identity].append(var_units)

            elif relaxed_units or variable.dtype.kind == 'S':
                var_units = _no_units
        else:
            if var_units:
                _canonical_units[identity] = [var_units]                
            elif relaxed_units or variable.dtype.kind == 'S':
                var_units = _no_units
        #--- End: if

        # Still here?
        return var_units
    #--- End: def

    def canonical_cell_methods(self, rtol=None, atol=None):
        '''

Updates the `_canonical_cell_methods` attribute.

:Parameters:

    atol : float

    rtol : float

:Returns:

    out : cf.CellMethods or None

:Examples:

'''
        _canonical_cell_methods = self._canonical_cell_methods

        cms = getattr(self.field, 'CellMethods', None)
        if not cms:
            return None

        cms = cms.copy()
        for cm in cms:
            cm.axes = [self.axis_to_id.get(axis, axis) for axis in cm.axes]
            cm.sort()

        for ccms in _canonical_cell_methods:
            if cms.equivalent(ccms, rtol=rtol, atol=atol):
                return cms
               
        # Still here?
        _canonical_cell_methods.append(cms)

        return cms
    #--- End: def

    def cell_measure_has_data_and_units(self, msr):
        '''

:Parameters:

    msr : cf.CellMeasure

:Returns:

    out : bool

:Examples:

'''
        if not msr.Units:
            if self.info:
                self.message = \
"%r cell measure has no units" % msr.name('')
            return

        if not msr._hasData:
            if self.info:
                self.message = \
"%r cell measure has no data" % msr.name('')
            return

        return True
    #--- End: def

    def coord_has_identity_and_data(self, coord):
        '''

:Parameters:

    coord : cf.Coordinate

:Returns:

    out : str or None
        The coordinate object's identity, or None if there is no
        identity and/or no data.

:Examples:

'''
        identity = coord.name(identity=self.strict_identities,
                              ncvar=self.ncvar_identities)

        if self.relaxed_identities and identity is not None:
            identity = identity.replace('long_name:', '', 1)
            identity = identity.replace('ncvar%', '', 1)

        if identity is None:
            # Coordinate has no identity, but it may have a recognised
            # axis.
            for ctype in ('T', 'X', 'Y', 'Z'):
                if getattr(coord, ctype):
                    identity = ctype
                    break
        #--- End: if

        if identity is not None:
            all_coord_identities = self.all_coord_identities

            if identity in all_coord_identities:
                if self.info:
                    self.message = \
"multiple {0!r} coordinates".format(identity)
                return None
            #--- End: if

            if coord._hasData or (coord._hasbounds and coord.bounds._hasData):
                all_coord_identities.add(identity)
                return identity
        #--- End: if

        if self.info:
            self.message = \
"%r coordinate has no identity or no data" % coord.name('')
            
        return None
    #--- End: def

    def field_ancillary_has_identity_and_data(self, anc):
        '''

:Parameters:

    coord : cf.FieldAncillary

:Returns:

    out : str or None
        The coordinate object's identity, or None if there is no
        identity and/or no data.

:Examples:

'''
        identity = anc.name(identity=self.strict_identities,
                            ncvar=self.ncvar_identities)

        if identity is not None:
            all_field_anc_identities = self.all_field_anc_identities

            if identity in all_field_anc_identities:
                if self.info:
                    self.message = \
"multiple {0!r} field ancillaries".format(identity)
                return None
            #--- End: if

            if anc._hasData:
                all_field_anc_identities.add(identity)
                return identity
        #--- End: if

        if self.info:
            self.message = \
"{0!r} field ancillary has no identity or no data".format(anc.name(''))
            
        return None
    #--- End: def

    def coordinate_reference_signatures(self, refs):
        '''

:Parameters:

    refs : sequence of cf.CoordinateReference

:Returns:

    out : list
        A structural signature of each coordinate reference object.

:Examples:

>>> sig = coordinate_reference_signatures(refs):
'''
        signatures = []

        if not refs:
            return signatures

        signatures = [ref.structural_signature() for ref in refs]

        for signature in signatures:
            if signature[0] is None:
                if info:
                    self.messsage = \
"{0!r} field can't be aggregated due to it having an unidentifiable coordinate reference".format(self.f.name(''))
                return
        #--- End: for
        
        signatures.sort()
        return signatures
    #--- End: def

    def domain_ancillary_has_identity_and_data(self, anc, identity=None):
        ''':Parameters:

    anc : cf.DomainAncillary

    identity : *optional*

:Returns:

    out : str or None
        The domain ancillary identity, or None if there is no identity
        and/or no data.

:Examples:

        '''
        if identity is not None:
            anc_identity = identity
        else:
            anc_identity = anc.name(identity=self.strict_identities,
                                    ncvar=self.ncvar_identities)

        if anc_identity is None:
            if self.info:
                self.message = \
"{0!r} domain ancillary has no identity".format(anc.name(''))
            return 

        all_domain_anc_identities = self.all_domain_anc_identities
            
        if anc_identity in all_domain_anc_identities:
            if self.info:
                self.message = \
"multiple {0!r} domain ancillaries".format(anc_identity)
            return

        if not anc._hasData:
            if self.info:
                self.message = \
"{0!r} domain ancillary has no data".format(anc.name(''))     
            return

        all_domain_anc_identities.add(anc_identity)

        return anc_identity
    #--- End: def

    def print_info(self, info, signature=True):
        '''
    
:Parameters:

    m : _Meta

    info : int

'''
        if info >= 2:
            if signature:
                print 'STRUCTURAL SIGNATURE:\n', self.string_structural_signature()
            if self.cell_values:
                print 'CANONICAL COORDINATES:\n', self.coordinate_values()
            
        if info >= 3:
            print 'COMPLETE AGGREGATION METADATA:\n', self
    #--- End: def

    def string_structural_signature(self):
        '''
'''
        keys = ('Identity', 
                'Units', 
                'Cell methods',
                'Data',
                'Properties', 
                'standard error multiplier',
                'valid_min',
                'valid_max',
                'valid_range',
                'Flags',
                'Ancillary variables',
                'Coordinate reference systems',
                '1-d coordinates',
                'Dimension coordinates', 
                'N-d coordinates',
                'Cell measures',
                'Domain ancillaries',
                'Field ancillaries',
                )

        string = []

        for key, value in zip(keys[:], self.signature[:]):
            if not (value == () or value is None):
                string.append('{0}: {1!r}'.format(key, value))
        
        return '\n'.join(string)
    #--- End: def

    def structural_signature(self):
        '''

:Returns:

    out : tuple

:Examples:

'''
        f = self.field    
      
        # Initialize the structual signature with:
        #
        # * the identity
        # * the canonical units
        # * the canonical cell methods
        # * whether or not there is a data array
        signature = [self.identity,
                     self.units.formatted(definition=True),
                     self.cell_methods,
                     self._hasData]
        signature_append = signature.append

        # Properties
        signature_append(self.properties)

        # standard_error_multiplier
        signature_append(f.getprop('standard_error_multiplier', None))

        # valid_min, valid_max, valid_range
        if self.respect_valid:
            signature.extend((f.getprop('valid_min'  , None),
                              f.getprop('valid_max'  , None),
                              f.getprop('valid_range', None)))
        else:
            signature.extend((None, None, None))            

        # Flags
        signature_append(getattr(f, 'Flags', None))
        
        # Coordinate references
        signature_append(tuple(['Coordinate references'] + self.coordref_signatures))

        # 1-d coordinates for each axis. Note that self.axis_ids has
        # already been sorted.
        axis = self.axis        
        x = [(identity,
              ('ids'      , axis[identity]['ids']), 
              ('units'    , tuple([u.formatted(definition=True) for u in axis[identity]['units']])),
              ('hasbounds', axis[identity]['hasbounds']),
              ('coordrefs', axis[identity]['coordrefs']),
              ('size'     , axis[identity]['size']))
             for identity in self.axis_ids]
        signature_append(tuple(['Axes'] + x))
        
        # Whether or not each axis has a dimension coordinate
        x = [False if axis[identity]['dim_coord_index'] is None else True
             for identity in self.axis_ids]
        signature_append(tuple(x))
        
        # N-d auxiliary coordinates
        nd_aux = self.nd_aux
        x = [(identity,
              ('units'    , nd_aux[identity]['units'].formatted(definition=True)),
              ('axes'     , nd_aux[identity]['axes']),
              ('hasbounds', nd_aux[identity]['hasbounds']),
              ('coordrefs', nd_aux[identity]['coordrefs']))
             for identity in sorted(nd_aux)]
        signature_append(tuple(['N-d coordinates'] + x))
        
        # Cell measures
        msr = self.msr
        x = [(('units', units.formatted(definition=True)),
              ('axes' , msr[units]['axes']))
             for units in sorted(msr)]
        signature_append(tuple(['Cell measures'] + x))

        # Domain ancillaries
        domain_anc = self.domain_anc
        x = [(identity,
              ('units', domain_anc[identity]['units'].formatted(definition=True)),
              ('axes' , domain_anc[identity]['axes']))
             for identity in sorted(domain_anc)]
        signature_append(tuple(['Domain ancillaries'] + x))
                
        # Field ancillaries
        field_anc = self.field_anc
        x = [(identity,
              ('units', field_anc[identity]['units'].formatted(definition=True)),
              ('axes' , field_anc[identity]['axes']))
             for identity in sorted(field_anc)]
        signature_append(tuple(['Field ancillaries'] + x))
                
        self.signature = tuple(signature)
    #--- End: def

    def find_coordrefs(self, key):
        '''

:Parameters:

    key: `str`
        The field identifier of the coordinate object

:Returns:

    out: `tuple` or `None`

:Examples:

>>> m.find_coordrefs('dim0')
>>> m.find_coordrefs('aux1')

'''    
        coordrefs = self.coordrefs

        if not coordrefs:
            return None

        # Select the coordinate references which contain a pointer to
        # this coordinate
        names = [ref.name() for ref in coordrefs if key in ref.coordinates]
        
        if not names:
            return None

        return tuple(sorted(names))
    #--- End: def

#--- End: class

def aggregate(fields,
              info=0,
              relaxed_units=False,
              no_overlap=False,
              contiguous=False,
              relaxed_identities=False,
              ncvar_identities=False,
              respect_valid=False,
              equal_all=False,
              exist_all=False,
              equal=None,
              exist=None,
              ignore=None,
              exclude=False,
              dimension=(),
              concatenate=True,
              copy=True, 
              axes=None,
              donotchecknonaggregatingaxes=False,
              allow_no_identity=False,
              shared_nc_domain=False,
              atol=None,
              rtol=None,
              ):
    r'''Aggregate fields into as few fields as possible.

The aggregation of fields may be thought of as the combination fields
into each other to create a new field that occupies a larger domain.

Using the CF aggregation rules, input fields are separated into
aggregatable groups and each group (which may contain just one field)
is then aggregated to a single field. These aggregated fields are
returned in a field list.

**Identities**

In order for aggregation to be possible, fields and their components
need to be unambiguously identifiable. By default, these identities
are taken from `!standard_name` CF properties or else `!id`
attributes. If both of these identifiers are absent then `!long_name`
CF properties or else `!ncvar` attributes may be used if the
*relaxed_identities* parameter is True.

:Parameters:

    fields: `cf.FieldList` or sequence of `cf.Field`
        The fields to aggregated.

    info: `int`, optional
        Print information about the aggregation process. If *info* is
        0 then no information is displayed.  If *info* is 1 or more
        then display information on which fields are unaggregatable,
        and why. If *info* is 2 or more then display the structural
        signatures of the fields and, when there is more than one
        field with the same structural signature, their canonical
        first and last coordinate values.  If *info* is 3 or more then
        display the fields' complete aggregation metadata. By default
        *info* is 0 and no information is displayed.

    no_overlap: `bool`, optional
        If True then require that aggregated fields have adjacent
        dimension coordinate object cells which do not overlap (but
        they may share common boundary values). Ignored if the
        dimension coordinates objects do not have bounds. See the
        *contiguous* parameter.

    contiguous: `bool`, optional
        If True then require that aggregated fields have adjacent
        dimension coordinate object cells which partially overlap or
        share common boundary values. Ignored if the dimension
        coordinate objects do not have bounds. See the *no_overlap*
        parameter.

    relaxed_units: `bool`, optional
        If True then assume that fields or domain items (such as
        coordinate objects) with the same identity (as returned by
        their `!identity` methods) but missing units all have
        equivalent but unspecified units, so that aggregation may
        occur. By default such fields are not aggregatable.

    allow_no_identity: `bool`, optional
        If True then treat fields with data arrays but with no
        identities (see the above notes) as having equal but
        unspecified identities, so that aggregation may occur. By
        default such fields are not aggregatable.

    relaxed_identities: `bool`, optional
        If True then allow fields and their components to be
        identified by their `!long_name` CF properties or else
        `!ncvar` attributes if their `!standard_name` CF properties or
        `!id` attributes are missing.

    ncvar_identities: `bool`, optional
        If True then Force fields and their components (such as
        coordinates) to be identified by their netCDF file variable
        names.

    shared_nc_domain: `bool`, optional
        If True then match axes between a field and its contained
        ancillary variable and coordinate reference fields via their
        netCDF dimension names and not via their domains.

    equal_all: `bool`, optional
        If True then require that aggregated fields have the same set
        of non-standard CF properties (including
        `~cf.Field.long_name`), with the same values. See the
        *concatenate* parameter.

    equal_ignore: (sequence of) `str`, optional
        Specify CF properties to omit from any properties specified by
        or implied by the *equal_all* and *equal* parameters.

    equal: (sequence of) `str`, optional
        Specify CF properties for which it is required that aggregated
        fields all contain the properties, with the same values. See
        the *concatenate* parameter.

    exist_all: `bool`, optional
        If True then require that aggregated fields have the same set
        of non-standard CF properties (including, in this case,
        long_name), but not requiring the values to be the same. See
        the *concatenate* parameter.

    exist_ignore: (sequence of) `str`, optional
        Specify CF properties to omit from the properties specified by
        or implied by the *exist_all* and *exist* parameters.

    exist: (sequence of) `str`, optional
        Specify CF properties for which it is required that aggregated
        fields all contain the properties, but not requiring the
        values to be the same. See the *concatenate* parameter.

    respect_valid: `bool`, optional
        If True then the CF properties `~cf.Field.valid_min`,
        `~cf.Field.valid_max` and `~cf.Field.valid_range` are taken
        into account during aggregation. By default these CF
        properties are ignored and are not set in the output fields.

    dimension: (sequence of) `str`, optional
        Create new axes for each input field which has one or more of
        the given properties. For each CF property name specified, if
        an input field has the property then, prior to aggregation, a
        new axis is created with an auxiliary coordinate whose datum
        is the property's value and the property itself is deleted
        from that field.

    concatenate: `bool`, optional
        If False then a CF property is omitted from an aggregated
        field if the property has unequal values across constituent
        fields or is missing from at least one constituent field. By
        default a CF property in an aggregated field is the
        concatenated collection of the distinct values from the
        constituent fields, delimited with the string
        ``' :AGGREGATED: '``.

    copy: `bool`, optional
        If False then do not copy fields prior to aggregation.
        Setting this option to False may change input fields in place,
        and the output fields may not be independent of the
        inputs. However, if it is known that the input fields are
        never to accessed again (such as in this case: ``f =
        cf.aggregate(f)``) then setting *copy* to False can reduce the
        time taken for aggregation.

    axes: (sequence of) `str`, optional
        Select axes to aggregate over. Aggregation will only occur
        over as large a subset as possible of these axes. Each axis is
        identified by the exact identity of a one dimensional
        coordinate object, as returned by its `!identity`
        method. Aggregations over more than one axis will occur in the
        order given. By default, aggregation will be over as many axes
        as possible.

    donotchecknonaggregatingaxes: `bool`, optional
        If True, and *axes* is set, then checks for consistent data
        array values will only be made for one dimensional coordinate
        objects which span the any of the given aggregating axes. This
        can reduce the time taken for aggregation, but if any those
        checks would have failed then this clearly allows the
        possibility of an incorrect result. Therefore, this option
        should only be used in cases for which it is known that the
        non-aggregating axes are in fact already entirely consistent.

    atol: float, optional
        The absolute tolerance for all numerical comparisons. The
        tolerance is a non-negative, typically very small number. Two
        numbers, x and y, are considered the same if :math:`|x-y| \le
        atol + rtol*|y|`. By default the value returned by the `ATOL`
        function is used.

    rtol: float, optional
        The relative tolerance for all numerical comparisons. The
        tolerance is a non-negative, typically very small number. Two
        numbers, x and y, are considered the same if :math:`|x-y| \le
        atol + rtol*|y|`. By default the value returned by the `RTOL`
        function is used.

:Returns:

    out: `cf.FieldList`
        The aggregated fields.
    
:Examples:

The following six fields comprise eastward wind at two different times
and for three different atmospheric heights for each time:

>>> f
[<CF Field: eastward_wind(latitude(73), longitude(96)>,
 <CF Field: eastward_wind(latitude(73), longitude(96)>,
 <CF Field: eastward_wind(latitude(73), longitude(96)>,
 <CF Field: eastward_wind(latitude(73), longitude(96)>,
 <CF Field: eastward_wind(latitude(73), longitude(96)>,
 <CF Field: eastward_wind(latitude(73), longitude(96)>]
>>> g = cf.aggregate(f)
>>> g
[<CF Field: eastward_wind(height(3), time(2), latitude(73), longitude(96)>]
>>> g[0].source
'Model A'
>>> g = cf.aggregate(f, dimension=('source',))
[<CF Field: eastward_wind(source(1), height(3), time(2), latitude(73), longitude(96)>]
>>> g[0].source
AttributeError: 'Field' object has no attribute 'source'

'''
    # Initialise the cache for coordinate and cell measure hashes,
    # first and last values and first and last cell bounds
    hfl_cache = _HFLCache()

    output_fields = FieldList()

    output_fields_append = output_fields.append

    if exclude:
        exclude = ' NOT'
    else:
        exclude = ''

    if atol is None:
        atol = ATOL()
    if rtol is None:
        rtol = RTOL()

    if axes is not None and isinstance(axes, basestring):
        axes = (axes,)

    # Parse parameters
    strict_identities = not (relaxed_identities or ncvar_identities)

    if exist_all and equal_all:
        raise AttributeError("asdasdas  jnf0____")

    if equal or exist or ignore:
        properties = {'equal' : equal,
                      'exist' : exist, 
                      'ignore': ignore}
        
        for key, value in properties.iteritems():
            if not value:
                continue
        
            if isinstance(equal, basestring):
                # If it is a string then convert to a single element
                # sequence
                properties[key] = (value,)
            else:
                try:
                    value[0]
                except TypeError:
                    raise TypeError("Bad type of %r parameter: %r" % 
                                    (key, type(value)))
        #--- End: for
        
        equal  = properties['equal']
        exist  = properties['exist']
        ignore = properties['ignore']
        
        if equal and exist:
            if set(equal).intersection(exist):
                raise AttributeError("888888888888888 asdasdas  jnf0____")
        
        if ignore:
            ignore = _signature_properties.union(ignore)
        else:
            ignore = _signature_properties
    #--- End: if

    unaggregatable = False
    status = 0

    # ================================================================
    # 1. Group together fields with the same structural signature
    # ================================================================
    signatures = {}
    for f in flat(fields):
        # ------------------------------------------------------------
        # Create the metadata summary, including the structural
        # signature
        # ------------------------------------------------------------
        meta = _Meta(f,
                     info=info, rtol=rtol, atol=atol,
                     relaxed_units=relaxed_units, 
                     allow_no_identity=allow_no_identity,
                     equal_all=equal_all,
                     exist_all=exist_all,
                     equal=equal,
                     exist=exist,
                     ignore=ignore,
                     dimension=dimension,
                     relaxed_identities=relaxed_identities,
                     ncvar_identities=ncvar_identities,
                     respect_valid=respect_valid)

        if not meta:
            unaggregatable = True
            status = 1

            if info:
                print(
"Unaggregatable {0!r} has{1} been output: {2}".format(
    f, exclude, meta.message))

            if not exclude:
                # This field does not have a structural signature, so
                # it can't be aggregated. Put it straight into the
                # output list and move on to the next input field.
                if not copy:
                    output_fields_append(f)
                else:
                    output_fields_append(f.copy())
            #--- End: if

            continue
        #--- End: if

        # ------------------------------------------------------------
        # This field has a structural signature, so append it to the
        # list of fields with the same structural signature.
        # ------------------------------------------------------------
        signatures.setdefault(meta.signature, []).append(meta)
    #--- End: for    

    # ================================================================
    # 2. Within each group of fields with the same structural
    #    signature, aggregate as many fields as possible. Sort the
    #    signatures so that independent aggregations of the same set
    #    of input fields return fields in the same order.
    # ================================================================
    for signature in sorted(signatures):
 
        meta = signatures[signature]

        if info >= 2:
            # Print useful information
            meta[0].print_info(info)
            print ''

        if len(meta) == 1:
            # --------------------------------------------------------
            # There's only one field with this signature, so we can
            # add it straight to the output list and move on to the
            # next signature.
            # --------------------------------------------------------
            if not copy:       
                output_fields_append(meta[0].field) 
            else:
                output_fields_append(meta[0].field.copy()) 

            continue
        #--- End: if

        # ------------------------------------------------------------
        # Still here? Then there are 2 or more fields with this
        # signature which may be aggregatable. These fields need to be
        # passed through until no more aggregations are possible. With
        # each pass, the number of fields in the group will reduce by
        # one for each aggregation that occurs. Each pass represents
        # an aggregation in another axis.
        # ------------------------------------------------------------

        # ------------------------------------------------------------
        # For each axis's 1-d coordinates, create the canonical hash
        # value and the first and last cell values.
        # ------------------------------------------------------------
        if axes is None:
            # Aggregation will be over as many axes as possible
            aggregating_axes = meta[0].axis_ids
            _create_hash_and_first_values(meta, None, False, hfl_cache, rtol, atol)

        else:    
            # Specific aggregation axes have been selected
            aggregating_axes = []
            axis_items = meta[0].axis.items()
            for axis in axes:
                coord = meta[0].field.coord(axis, exact=True)
                if coord is None:
                    continue

                coord_identity = coord.name(identity=strict_identities,
                                            ncvar=ncvar_identities)
                for identity, value in axis_items:
                    if (identity not in aggregating_axes and 
                        coord_identity in value['ids']):
                        aggregating_axes.append(identity)
                        break
            #--- End: for

            _create_hash_and_first_values(meta, aggregating_axes, 
                                          donotchecknonaggregatingaxes,
                                          hfl_cache, rtol, atol)
        #--- End: if

        if info >= 2:
            # Print useful information
            for m in meta:
                m.print_info(info, signature=False)
            print ''
        #--- End: if

        # Take a shallow copy in case we abandon and want to output
        # the original, unaggregated fields.
        meta0 = meta[:]

        unaggregatable = False

        for axis in aggregating_axes:

            number_of_fields = len(meta)
            if number_of_fields == 1:
                break

            # --------------------------------------------------------
            # Separate the fields with the same structural signature
            # into groups such that either within each group the
            # fields' domains differ only long the axis or each group
            # contains only one field.
            #
            # Note that the 'a_identity' attribute is set in the
            # _group_fields function.
            # --------------------------------------------------------
            grouped_meta = _group_fields(meta, axis)

            if not grouped_meta:                
                if info:
                    print(
"Unaggregatable %r fields have%s been output: %s" % 
(meta[0].field.name(''), exclude, meta[0].message))

                unaggregatable = True
                break
            #--- End: if

            if len(grouped_meta) == number_of_fields:
                if info >= 3:
                    print(
"%r fields can't be aggregated along their %r axis" %
(meta[0].field.name(''), axis))
                continue

            # --------------------------------------------------------
            # Within each group, aggregate as many fields as possible.
            # --------------------------------------------------------
            for m in grouped_meta:

                if len(m) == 1:
                    continue
                
                # ----------------------------------------------------
                # Still here? The sort the fields in place by the
                # canonical first values of their 1-d coordinates for
                # the aggregating axis.
                # ----------------------------------------------------
                _sorted_by_first_values(m, axis)

                # ----------------------------------------------------
                # Check that the aggregating axis's 1-d coordinates
                # don't overlap, and don't aggregate anything in this
                # group if any do.
                # ----------------------------------------------------
                if not _ok_coordinate_arrays(m, axis, no_overlap, contiguous,
                                             info):
                    if info:
                        print(
"Unaggregatable %r fields have%s been output: %s" % 
(m[0].field.name(''), exclude, m[0].message))

                    unaggregatable = True
                    break
                #--- End: if

                # ----------------------------------------------------
                # Still here? Then pass through the fields
                # ----------------------------------------------------
                m0 = m[0].copy()

                for m1 in m[1:]:
                    m0 = _aggregate_2_fields(m0, m1,
                                             rtol=rtol, atol=atol,
                                             respect_valid=respect_valid,
                                             contiguous=contiguous,
                                             no_overlap=no_overlap,
                                             relaxed_units=relaxed_units,
                                             info=info,
                                             concatenate=concatenate,
                                             copy=(copy or not exclude),
                                             relaxed_identities=relaxed_identities,
                                             ncvar_identities=ncvar_identities,
                                             shared_nc_domain=shared_nc_domain)
                                                                 
                    if not m0:
                        # Couldn't aggregate these two fields, so
                        # abandon all aggregations on the fields with
                        # this structural signature, including those
                        # already done.
                        if info:
                            print(
"Unaggregatable {!r} fields have{} been output: {}".format( 
    m1.field.name(''), exclude, m1.message))

                        unaggregatable = True
                        break
                #--- End: while

                m[:] = [m0]
            #--- End: for

            if unaggregatable:
                break

            # --------------------------------------------------------
            # Still here? Then the aggregation along this axis was
            # completely successful for each sub-group, so reassemble
            # the aggregated fields as a single list ready for
            # aggregation along the next axis.
            # --------------------------------------------------------
            meta = [m for gm in grouped_meta for m in gm]
        #--- End: for

        # Add fields to the output list
        if unaggregatable:
            status = 1
            if not exclude:
                if copy:       
                    output_fields.extend((m.field.copy() for m in meta0)) 
                else:
                    output_fields.extend((m.field for m in meta0)) 
        else:
            output_fields.extend((m.field for m in meta)) 
    #--- End: for

    aggregate.status = status

    if status and info > 0:
        print ''

    return output_fields
#--- End: def

# --------------------------------------------------------------------
# Initialise the status
# --------------------------------------------------------------------
aggregate.status = 0

def _create_hash_and_first_values(meta, axes, donotchecknonaggregatingaxes,
                                  hfl_cache, rtol, atol):
    '''

Updates each field's _Meta object.

:Parameters:

    meta: `list` of `_Meta`

    axes: `None` or `list`

    donotchecknonaggregatingaxes: `bool`

:Returns:

    `None`

'''
    for m in meta:
        field = m.field

        item_axes = m.field.Items._axes

        m_sort_keys    = m.sort_keys
        m_sort_indices = m.sort_indices

        m_hash_values  = m.hash_values
        m_first_values = m.first_values
        m_last_values  = m.last_values

        m_id_to_axis = m.id_to_axis
        # --------------------------------------------------------
        # Create a hash value for each metadata array
        # --------------------------------------------------------
        
        # --------------------------------------------------------
        # 1-d coordinates
        # --------------------------------------------------------
        for identity in m.axis_ids:

            if (axes is not None and donotchecknonaggregatingaxes and
                identity not in axes):
                x = [None] * len(m.axis[identity]['keys'])
                m_hash_values[identity]  = x
                m_first_values[identity] = x[:]
                m_last_values[identity]  = x[:]
                continue

            # Still here?
            m_axis_identity = m.axis[identity]
            axis = m_id_to_axis[identity]

            # If this axis has no 1-d coordinates and is defined only
            # its netCDF dimension name and its size, then hash the
            # domain axis object
            axis_size = m_axis_identity['size']
            if axis_size is not None:
                m_hash_values[identity]  = [hash(field.axis(axis))]
                m_first_values[identity] = [None]
                m_last_values[identity]  = [None]
                m_sort_indices[axis] = slice(None)
                continue

            # Still here?
            dim_coord = m.field.item(axis)

            # Find the sort indices for this axis ...
            if dim_coord is not None:
                # ... which has a dimension coordinate
                m_sort_keys[axis] = axis
                if not field.direction(axis):
                    # Axis is decreasing
                    sort_indices = slice(None, None, -1)
                    null_sort = False
                else:
                    # Axis is increasing
                    sort_indices = slice(None)
                    null_sort = True
             
            else:
                # ... or which doesn't have a dimension coordinate but
                #     does have one or more 1-d auxiliary coordinates
                aux = m_axis_identity['keys'][0]
                sort_indices = numpy_argsort(field.item(aux).unsafe_array)
                m_sort_keys[axis] = aux 
                null_sort = False
            #-- End: if
            m_sort_indices[axis] = sort_indices

            hash_values  = []
            first_values = []
            last_values  = []

            for key, canonical_units in izip(m_axis_identity['keys'],
                                             m_axis_identity['units']):

                coord = field.item(key)

                # Get the hash of the data array and its first and
                # last values
                h, f, l = _get_hfl(coord, canonical_units, sort_indices,
                                   null_sort, True, False, hfl_cache, rtol, atol)

                first_values.append(f)
                last_values.append(l)
                
                if coord._hasbounds:                        
                    if coord.isdimension:
                        # Get the hash of the dimension coordinate
                        # bounds data array and its first and last
                        # cell values
                        hb, fb, lb = _get_hfl(coord.bounds, canonical_units,
                                              sort_indices, null_sort, 
                                              False, True, hfl_cache, rtol, atol)
                        m.first_bounds[identity] = fb
                        m.last_bounds[identity]  = lb
                    else:
                        # Get the hash of the auxiliary coordinate
                        # bounds data array
                        hb  = _get_hfl(coord.bounds, canonical_units,
                                       sort_indices, null_sort,
                                       False, False, hfl_cache, rtol, atol)
                    #--- End: if
                    h = (h, hb)
                #--- End: if
                
                hash_values.append(h)
##                else:
##                    coord_units = coord.Units
##    
##                    # Change the coordinate data type if required
##                    if coord.dtype.char not in ('d', 'S'):
##                        coord = coord.copy(_only_Data=True)
##                        coord.dtype = _dtype_float
##    
##                    # Change the coordinate's units to the canonical ones
##                    coord.Units = canonical_units
##    
##                    # Get the coordinate's data array
##                    if null_sort:
##                        array = coord.Data.unsafe_array
##                    else:
##                        array = coord.Data.array[sort_indices]
##    
##                    hash_value = hash_array(array)
##    
##                    first_values.append(array.item(0)) #[0])
##                    last_values.append(array.item(-1)) #[-1])
##    
##                    if coord._hasbounds:
##                        if null_sort:
##                            array = coord.bounds.Data.unsafe_array
##                        else:
##                            array = coord.bounds.Data.array[sort_indices, ...]
##    
##                        hash_value = (hash_value, hash_array(array))
##    
##                        if key[:3] == 'dim':  # can do better than this! DCH
##                            # Record the bounds of the first and last
##                            # (sorted) cells of a dimension coordinate
##                            # (don't need to do this for an auxiliary
##                            # coordinate).
##                            array0 = array[0, ...].copy()
##                            array0.sort()
##                            m.first_bounds[identity] = array0
##    
##                            array0 = array[-1, ...].copy()
##                            array0.sort()
##                            m.last_bounds[identity] = array0
##                    #--- End: if
##                        
##                    hash_values.append(hash_value)
##    
##                    # Reinstate the coordinate's original units
##                    coord.Units = coord_units
            #--- End: for
                
            m_hash_values[identity]  = hash_values
            m_first_values[identity] = first_values
            m_last_values[identity]  = last_values
        #--- End: for

        # ------------------------------------------------------------
        # N-d auxiliary coordinates
        # ------------------------------------------------------------
        if donotchecknonaggregatingaxes:
            for aux in m.nd_aux.itervalues():
                aux['hash_value'] = None
        else:
            for aux in m.nd_aux.itervalues():
                key             = aux['key']
                canonical_units = aux['units']

                coord = field.item(key)
                
                axes = [m_id_to_axis[identity] for identity in aux['axes']]
                domain_axes = item_axes[key]
                if axes != domain_axes:
                    coord = coord.copy(_only_Data=True)                        
                    iaxes = [domain_axes.index(axis) for axis in axes]
                    coord.transpose(iaxes, i=True)
                
                sort_indices = tuple([m_sort_indices[axis] for axis in axes])
                    
                # Get the hash of the data array
                h = _get_hfl(coord, canonical_units, sort_indices, 
                             False, False, False, hfl_cache, rtol, atol)
                
                if coord._hasbounds:
                    # Get the hash of the bounds data array
                    hb  = _get_hfl(coord.bounds, canonical_units,
                                   sort_indices,
                                   False, False, False, hfl_cache, rtol, atol)
                    h = (h, hb)
                    
                aux['hash_value'] = h
            #--- End: for
        #--- End: if
            
        # ------------------------------------------------------------
        # Cell measures
        # ------------------------------------------------------------
        if donotchecknonaggregatingaxes:
            for msr in m.msr.itervalues():            
                msr['hash_values'] = [None] * len(msr['keys'])
        else:
            for canonical_units, msr in m.msr.iteritems():                
                hash_values = []           
                for key, axes in izip(msr['keys'], msr['axes']):            
                    coord = field.item(key) 
         
                    axes = [m_id_to_axis[identity] for identity in axes]
           
                    domain_axes = item_axes[key]
                    if axes != domain_axes:
                        coord = coord.copy(_only_Data=True)
                        iaxes = [domain_axes.index(axis) for axis in axes]
                        coord.transpose(iaxes, i=True)
 
                    sort_indices = [m_sort_indices[axis] for axis in axes]
                
                    # Get the hash of the data array
                    h = _get_hfl(coord, canonical_units,
                                 tuple(sort_indices),
                                 False, False, False, hfl_cache, rtol, atol)

                    hash_values.append(h)
                #--- End: for
            
                msr['hash_values'] = hash_values
            #--- End: for
        #--- End: if

        # ------------------------------------------------------------
        # Field ancillaries
        # ------------------------------------------------------------
        if donotchecknonaggregatingaxes:
            for anc in m.field_anc.itervalues():
                anc['hash_value'] = None
        else:
            for anc in m.field_anc.itervalues():
                key             = anc['key']
                canonical_units = anc['units']

                field_anc = field.item(key)
                
                axes = [m_id_to_axis[identity] for identity in anc['axes']]
                domain_axes = item_axes[key]
                if axes != domain_axes:
                    field_anc = field_anc.copy(_only_Data=True)                        
                    iaxes = [domain_axes.index(axis) for axis in axes]
                    field_anc.transpose(iaxes, i=True)
                
                sort_indices = tuple([m_sort_indices[axis] for axis in axes])
                    
                # Get the hash of the data array
                h = _get_hfl(field_anc, canonical_units, sort_indices, 
                             False, False, False, hfl_cache, rtol, atol)
                
                anc['hash_value'] = h
            #--- End: for
        #--- End: if
            
        # ------------------------------------------------------------
        # Domain ancillaries
        # ------------------------------------------------------------
        if donotchecknonaggregatingaxes:
            for anc in m.domain_anc.itervalues():
                anc['hash_value'] = None
        else:
            for anc in m.domain_anc.itervalues():
                key             = anc['key']
                canonical_units = anc['units']

                field_anc = field.item(key)
                
                axes = [m_id_to_axis[identity] for identity in anc['axes']]
                domain_axes = item_axes[key]
                if axes != domain_axes:
                    field_anc = field_anc.copy(_only_Data=True)                        
                    iaxes = [domain_axes.index(axis) for axis in axes]
                    field_anc.transpose(iaxes, i=True)
                #--- End: if
                
                sort_indices = tuple([m_sort_indices[axis] for axis in axes])
                    
                # Get the hash of the data array
                h = _get_hfl(field_anc, canonical_units, sort_indices, 
                             False, False, False, hfl_cache, rtol, atol)
                
                anc['hash_value'] = h
            #--- End: for
        #--- End: if

        m.cell_values = True
    #--- End: for
#--- End: def

def _get_hfl(v, canonical_units, sort_indices, null_sort, 
             first_and_last_values, first_and_last_bounds,
             hfl_cache, rtol, atol):
    '''Return the hash value, and optionally first and last values (or
cell bounds)

    '''
    create_hash = True
    create_fl   = first_and_last_values
    create_flb  = first_and_last_bounds

    key = None

    d = v.Data

    if d._pmsize == 1:
        partition = d.partitions.matrix.item()
        if not partition.part:
            key = getattr(partition.subarray, 'file_pointer', None)
            if key is not None:
                hash_value = hfl_cache.hash.get(key, None)
                create_hash = hash_value is None

                if first_and_last_values:
                    first, last = hfl_cache.fl.get(key, (None, None))
                    create_fl = first is None

                if first_and_last_bounds:
                    first, last = hfl_cache.flb.get(key, (None, None))
                    create_flb = first is None
    #--- End: if

    if create_hash or create_fl or create_flb:
        # Change the data type if required
        if d.dtype.char not in ('d', 'S'):
            d = d.copy()
            d.dtype = _dtype_float
        
        # Change the units to the canonical ones
        units = d.Units
        d.Units = canonical_units
        
        # Get the data array
        if null_sort:
            array = d.unsafe_array
        else:
            array = d.array[sort_indices]
            
        # Reinstate the original units
        d.Units = units

        if create_hash:
            hash_value = hash_array(array)

            if hash_value not in hfl_cache.hash_to_array:
                # Compare arrays, overriding hash value
                found_close = False
                for hash_value0, array0 in hfl_cache.hash_to_array.iteritems():

                    if array0.shape != array.shape:
                        continue

                    if array0.shape != array.shape:
                        continue

                    if _numpy_allclose(array0, array, rtol=rtol, atol=atol):
                        hash_value = hash_value0
                        found_close = True
                        break
                #--- End: for

                if not found_close:
                    hfl_cache.hash_to_array[hash_value] = array
            #--- End: if

            hfl_cache.hash[key] = hash_value                    
        #--- End: if

        if create_fl:
            first = array.item(0)
            last  = array.item(-1)           
            hfl_cache.fl[key] = (first, last)

        if create_flb: 
            # Record the bounds of the first and last (sorted) cells
            first = numpy_sort(array[0, ...])
            last  = numpy_sort(array[-1, ...])
            hfl_cache.flb[key] = (first, last)
    #--- End: if

    if first_and_last_values or first_and_last_bounds:
        return hash_value, first, last
    else:
        return hash_value
#--- End: def

def _group_fields(meta, axis):
    '''

:Parameters:

    meta: `list` of `_Meta`

    axis: `str`
        The name of the axis to group for aggregation.

:Returns:

    out : list of cf.FieldList

'''
    axes = meta[0].axis_ids

    if axes:
        if axis in axes:
            # Move axis to the end of the axes list
            axes = axes[:]
            axes.remove(axis)
            axes.append(axis)
        #--- End: if

        sort_by_axis_ids = itemgetter(*axes)            
        def _hash_values(m):
            return sort_by_axis_ids(m.hash_values)
        
        meta.sort(key=_hash_values)
    #--- End: if

    # Create a new group of potentially aggregatable fields (which
    # contains the first field in the sorted list)
    m0 = meta[0]
    groups_of_fields = [[m0]]

    hash0 = m0.hash_values

    for m0, m1 in izip(meta[:-1], meta[1:]):

        #-------------------------------------------------------------
        # Count the number of axes which are different between the two
        # fields
        # -------------------------------------------------------------
        count = 0
        hash1 = m1.hash_values
        for identity, value in hash0.iteritems():
            if value != hash1[identity]:
                count += 1
                a_identity = identity                
        #--- End: for
        hash0 = hash1

        if count == 1:
            # --------------------------------------------------------
            # Exactly one axis has different 1-d coordinate values
            # --------------------------------------------------------
            if a_identity != axis:
                # But it's not the axis that we're trying currently to
                # aggregate over
                groups_of_fields.append([m1])
                continue

            # Still here? Then it is the axis that we're trying
            # currently to aggregate over.
            ok = True

            # Check the N-d auxiliary coordinates
            for identity, aux0 in m0.nd_aux.iteritems():
                if (a_identity not in aux0['axes'] and 
                    aux0['hash_value'] != m1.nd_aux[identity]['hash_value']):
                    # This matching pair of N-d auxiliary coordinates
                    # does not span the aggregating axis and they have
                    # different data array values
                    ok = False
                    break
            #--- End: for
            if not ok:
                groups_of_fields.append([m1])
                continue 
                
            # Still here? Then check the cell measures
            msr0 = m0.msr
            for units in msr0:
                for axes, hash_value0, hash_value1 in izip(
                    msr0[units]['axes'],
                    msr0[units]['hash_values'],
                    m1.msr[units]['hash_values']):
                    
                    if a_identity not in axes and hash_value0 != hash_value1:
                        # There is a matching pair of cell measures
                        # with these units which does not span the
                        # aggregating axis and they have different
                        # data array values
                        ok = False
                        break
            #--- End: for
            if not ok:
                groups_of_fields.append([m1])
                continue 
                
            # Still here? Then set the identity of the aggregating
            # axis
            m0.a_identity = a_identity
            m1.a_identity = a_identity
            
            # Append field1 to this group of potentially aggregatable
            # fields
            groups_of_fields[-1].append(m1)

        elif not count:
            # --------------------------------------------------------
            # Zero axes have different 1-d coordinate values, so don't
            # aggregate anything in this entire group.
            # --------------------------------------------------------
            meta[0].message = \
"indistinguishable coordinates or other domain information"
            return ()

        else:
            # --------------------------------------------------------
            # Two or more axes have different 1-d coordinate values,
            # so create a new sub-group of potentially aggregatable
            # fields which contains field1.
            # --------------------------------------------------------
            groups_of_fields.append([m1])
        #--- End: if
    #--- End: for

    return groups_of_fields
#--- End: def

def _sorted_by_first_values(meta, axis):
    '''

Sort fields inplace

:Parameters:

    meta : list of _Meta

    axis : str

:Returns:

    None

''' 
    sort_by_axis_ids = itemgetter(axis)

    def _first_values(m):
        return sort_by_axis_ids(m.first_values)
    #--- End: def

    meta.sort(key=_first_values)
#--- End: def

def _ok_coordinate_arrays(meta, axis, no_overlap, contiguous, info):
    '''

Return True if the aggregating axis's 1-d coordinates are all
aggregatable.

It is assumed that the input metadata objects have already been sorted
by the canonical first values of their 1-d coordinates.

:Parameters:

    meta: `list` of `_Meta`

    axis: `str`
        Find the canonical identity of the aggregating axis.

    no_overlap: `bool`
        See the `cf.aggregate` function for details.

    contiguous: `bool`
        See the `cf.aggregate` function for details.

    info: 

:Returns:

    out : bool

:Examples:

>>> if not _ok_coordinate_arrays(meta, True, False)
...     print "Don't aggregate"

'''
    m = meta[0]

    dim_coord_index = m.axis[axis]['dim_coord_index']

    if dim_coord_index is not None:
        # ------------------------------------------------------------
        # The aggregating axis has a dimension coordinate
        # ------------------------------------------------------------
        # Check for overlapping dimension coordinate cell centres
        dim_coord_index0 = dim_coord_index

        for m0, m1 in izip(meta[:-1], meta[1:]):
            dim_coord_index1 = m1.axis[axis]['dim_coord_index']
            if (m0.last_values[axis][dim_coord_index0] >=
                m1.first_values[axis][dim_coord_index1]):
                # Found overlap
                if info:
                    meta[0].message = \
"%r dimension coordinate values overlap (%s >= %s)" % \
(m.axis[axis]['ids'][dim_coord_index],
 m0.last_values[axis][dim_coord_index0],
 m1.first_values[axis][dim_coord_index1])
#
#
#"%r fields can't be aggregated due to their %r dimension coordinate values over#lapping (%s >= %s)" % 
#(m.field.name(''),
# m.axis[axis]['ids'][dim_coord_index],
# m0.last_values[axis][dim_coord_index0],
# m1.first_values[axis][dim_coord_index1]))
                return

            dim_coord_index0 = dim_coord_index1        
        #--- End: for

        if axis in m.first_bounds:
            # --------------------------------------------------------
            # The dimension coordinates have bounds
            # --------------------------------------------------------
            if no_overlap:
                for m0, m1 in izip(meta[:-1], meta[1:]):
                    if (m1.first_bounds[axis][0] <
                        m0.last_bounds[axis][1]):
                        # Do not aggregate anything in this group
                        # because overlapping has been disallowed and
                        # the first cell from field1 overlaps with the
                        # last cell from field0.
                        if info:
                            meta[0].message = \
"%r dimension coordinate bounds values overlap (%s < %s)" % \
(m.axis[axis]['ids'][dim_coord_index],
 m1.first_bounds[axis][0],
 m0.last_bounds[axis][1])

                        return
                #--- End: for

            else:
                for m0, m1 in izip(meta[:-1], meta[1:]):
                    m0_last_bounds  = m0.last_bounds[axis]        
                    m1_first_bounds = m1.first_bounds[axis]
                    if (m1_first_bounds[0] <= m0_last_bounds[0] or
                        m1_first_bounds[1] <= m0_last_bounds[1]):
                        # Do not aggregate anything in this group
                        # because, even though overlapping has been
                        # allowed, the first cell from field1 overlaps
                        # in an unreasonable way with the last cell
                        # from field0.
                        if info:
                            meta[0].message = \
"%r dimension coordinate bounds values overlap by too much (%s <= %s)" % \
(m.axis[axis]['ids'][dim_coord_index],
 m1_first_bounds[0], m0_last_bounds[0],
 m1_first_bounds[1], m0_last_bounds[1])

                        return
                #--- End: for
            #--- End: if

            if contiguous:
                for m0, m1 in izip(meta[:-1], meta[1:]):
                    if (m0.last_bounds[axis][1] <
                        m1.first_bounds[axis][0]):
                        # Do not aggregate anything in this group
                        # because contiguous coordinates have been
                        # specified and the first cell from field1 is
                        # not contiguous with the last cell from
                        # field0.
                        if info:
                            meta[0].message = \
"%r dimension coordinate cells are not contiguous (%s < %s)" % \
(m.axis[axis]['ids'][dim_coord_index],
 m0.last_bounds[axis][1], 
 m1.first_bounds[axis][0])

                        return
                #--- End: for
            #--- End: if
        #--- End: if

    else:
        # ------------------------------------------------------------
        # The aggregating axis does not have a dimension coordinate,
        # but it does have at least one 1-d auxiliary coordinate.
        # ------------------------------------------------------------
        # Check for duplicate auxiliary coordinate values
        for i, identity in enumerate(meta[0].axis[axis]['ids']):
            set_of_1d_aux_coord_values    = set()
            number_of_1d_aux_coord_values = 0
            for m in meta:
                aux = m.axis[axis]['keys'][i]
                array = m.field.item(aux).array
                set_of_1d_aux_coord_values.update(array)
                number_of_1d_aux_coord_values += array.size
                if len(set_of_1d_aux_coord_values) != number_of_1d_aux_coord_values:
                    if info:
                        meta[0].message = \
"no %r dimension coordinates and %r auxiliary coordinates have duplicate values" % \
(identity, identity)

                    return
            #--- End: for
        #--- End: for
    #--- End: if
 
    # ----------------------------------------------------------------
    # Still here? Then the aggregating axis does not overlap between
    # any of the fields.
    # ----------------------------------------------------------------
    return True
#--- End: def

def _aggregate_2_fields(m0, m1,
                        rtol=None, atol=None,
                        info=0,    
                        respect_valid=False,
                        relaxed_units=False,
                        no_overlap=False, 
                        contiguous=False,
                        concatenate=True,
                        copy=True,
                        relaxed_identities=False,
                        ncvar_identities=False,
                        shared_nc_domain=False):
    '''

:Parameters:

    m0: `_Meta`

    m1: `_Meta`

    contiguous: `bool`, optional
        See the `cf.aggregate` function for details.
   
    rtol: `float`, optional
        See the `cf.aggregate` function for details.

    atol: `float`, optional
        See the `cf.aggregate` function for details.
   
    info: `int`, optional
        See the `cf.aggregate` function for details.
   
    no_overlap: `bool`, optional
        See the `cf.aggregate` function for details.
  
    relaxed_units: `bool`, optional
        See the `cf.aggregate` function for details.

    relaxed_identities: `bool`, optional
        See the `cf.aggregate` function for details.

    ncvar_identities: `bool`, optional
        See the `cf.aggregate` function for details.

:Returns:

    out : _Meta or bool
  
''' 
#    if copy and not m0.aggregated_field:
#        m0.field = m0.field.copy()

    a_identity = m0.a_identity
    
#    # ----------------------------------------------------------------
#    # Aggregate coordinate references
#    # ----------------------------------------------------------------
#    if m0.coordref_signatures:
#        t = _aggregate_coordrefs(m0, m1,
#                                 axis=a_identity,
#                                 rtol=rtol, atol=atol,
#                                 respect_valid=respect_valid,
#                                 relaxed_units=relaxed_units,
#                                 no_overlap=no_overlap, info=info,
#                                 contiguous=contiguous,
#                                 relaxed_identities=relaxed_identities,
#                                 ncvar_identities=ncvar_identities,
#                                 shared_nc_domain=shared_nc_domain)
#        if not t:
#            return
#    else:
#        t = None
#
#    # ----------------------------------------------------------------
#    # Aggregate ancillary variables
#    # ----------------------------------------------------------------
#    if m0.ancillary_variables:
#        av = _aggregate_ancillary_variables(m0, m1,
#                                            axis=a_identity,
#                                            rtol=rtol, atol=atol,
#                                            respect_valid=respect_valid,
#                                            relaxed_units=relaxed_units,
#                                            no_overlap=no_overlap,
#                                            info=info,
#                                            contiguous=contiguous,
#                                            relaxed_identities=relaxed_identities,
#                                            ncvar_identities=ncvar_identities,
#                                            shared_nc_domain=shared_nc_domain)
#        if not av:
#            return
#    else:
#        av = None
 
    # Still here?
    field0 = m0.field
    field1 = m1.field
    if copy:
        field1 = field1.copy()

#    domain0 = field0.domain
#    domain1 = field1.domain

#    if t:
#        # ------------------------------------------------------------
#        # Update coordinate references
#        # ------------------------------------------------------------
#        for key, ref in t.iteritems():
#            field0.insert_ref(ref, key=key, copy=False, replace=True)
#    #--- End: if
#
#    if av:
#        # ------------------------------------------------------------
#        # Update ancillary variables
#        # ------------------------------------------------------------
#        field0.ancillary_variables = av

    # ----------------------------------------------------------------
    # Map the axes of field1 to those of field0
    # ----------------------------------------------------------------
    dim1_name_map = {}
    for identity in m0.axis_ids:
        dim1_name_map[m1.id_to_axis[identity]] = m0.id_to_axis[identity]
        
    dim0_name_map = {}
    for axis1, axis0 in dim1_name_map.iteritems():
        dim0_name_map[axis0] = axis1        

    # ----------------------------------------------------------------
    # In each field, find the identifier of the aggregating axis.
    # ----------------------------------------------------------------
    adim0 = m0.id_to_axis[a_identity]
    adim1 = m1.id_to_axis[a_identity]

    # ----------------------------------------------------------------
    # Make sure that, along the aggregating axis, field1 runs in the
    # same direction as field0
    # ----------------------------------------------------------------
    direction0 = field0.direction(adim0)
    if field1.direction(adim1) != direction0:
        field1.flip(adim1, i=True)

    # ----------------------------------------------------------------
    # Find matching pairs of coordinates and cell measures which span
    # the aggregating axis
    # ----------------------------------------------------------------
    # 1-d coordinates
    spanning_variables = [(key0, key1, field0.item(key0), field1.item(key1))
                          for key0, key1 in izip(m0.axis[a_identity]['keys'],
                                                 m1.axis[a_identity]['keys'])] 
   
    hash_values0 = m0.hash_values[a_identity]
    hash_values1 = m1.hash_values[a_identity]
    for i, (hash0, hash1) in enumerate(izip(hash_values0, hash_values1)):
        try:
            hash_values0[i].append(hash_values1[i])
        except AttributeError:
            hash_values0[i] = [hash_values0[i], hash_values1[i]]
    #--- End: for

    # N-d auxiliary coordinates
    for identity in m0.nd_aux:
        aux0 = m0.nd_aux[identity]
        aux1 = m1.nd_aux[identity]
        if a_identity in aux0['axes']:
            key0 = aux0['key']
            key1 = aux1['key']
            spanning_variables.append((key0, key1,
                                       field0.item(key0),
                                       field1.item(key1)))

            hash_value0 = aux0['hash_value']
            hash_value1 = aux1['hash_value']
            try:
                hash_value0.append(hash_value1)
            except AttributeError:
                aux0['hash_value'] = [hash_value0, hash_value1]
    #--- End: for
    
    # Cell measures                
    for units in m0.msr:
        hash_values0 = m0.msr[units]['hash_values']
        hash_values1 = m1.msr[units]['hash_values']
        for i, (axes, key0, key1) in enumerate(izip(m0.msr[units]['axes'],
                                                    m0.msr[units]['keys'],
                                                    m1.msr[units]['keys'])):
            if a_identity in axes:
                spanning_variables.append((key0, key1,
                                           field0.item(key0),
                                           field1.item(key1)))

                try:
                    hash_values0[i].append(hash_values1[i])
                except AttributeError:
                    hash_values0[i] = [hash_values0[i], hash_values1[i]]
    #--- End: for

    # Field ancillaries
    for identity in m0.field_anc:
        anc0 = m0.field_anc[identity]
        anc1 = m1.field_anc[identity]
        if a_identity in anc0['axes']:
            key0 = anc0['key']
            key1 = anc1['key']
            spanning_variables.append((key0, key1,
                                       field0.item(key0),
                                       field1.item(key1)))

            hash_value0 = anc0['hash_value']
            hash_value1 = anc1['hash_value']
            try:
                hash_value0.append(hash_value1)
            except AttributeError:
                anc0['hash_value'] = [hash_value0, hash_value1]
    #--- End: for

    # Domain ancillaries
    for identity in m0.domain_anc:
        anc0 = m0.domain_anc[identity]
        anc1 = m1.domain_anc[identity]
        if a_identity in anc0['axes']:
            key0 = anc0['key']
            key1 = anc1['key']
            spanning_variables.append((key0, key1,
                                       field0.item(key0),
                                       field1.item(key1)))

            hash_value0 = anc0['hash_value']
            hash_value1 = anc1['hash_value']
            try:
                hash_value0.append(hash_value1)
            except AttributeError:
                anc0['hash_value'] = [hash_value0, hash_value1]
    #--- End: for

    # ----------------------------------------------------------------
    # For each matching pair of coordinates, cell measures, field and
    # domain ancillaries which span the aggregating axis, insert the
    # one from field1 into the one from field0
    # ----------------------------------------------------------------
    for key0, key1, item0, item1 in spanning_variables:
        item_axes0 = field0.item_axes(key0)
        item_axes1 = field1.item_axes(key1)

        # Ensure that the axis orders are the same in both items
        iaxes = [item_axes1.index(dim0_name_map[axis0]) for axis0 in item_axes0]
        item1.transpose(iaxes, i=True)

        # Find the position of the concatenating axis
        axis = item_axes0.index(adim0)

        if direction0:
            # The fields are increasing along the aggregating axis
            item0.Data = Data.concatenate((item0.Data, item1.Data), axis,
                                          _preserve=False)
            if item0._hasbounds:            
                item0.bounds.Data = Data.concatenate((item0.bounds.Data,
                                                      item1.bounds.Data),
                                                     axis, _preserve=False)
        else:
            # The fields are decreasing along the aggregating axis
            item0.Data = Data.concatenate((item1.Data, item0.Data), axis,
                                          _preserve=False)
            if item0._hasbounds:            
                item0.bounds.Data = Data.concatenate((item1.bounds.Data,
                                                      item0.bounds.Data),
                                                     axis, _preserve=False)
    #--- End: for        
        
    # ----------------------------------------------------------------
    # Insert the data array from field1 into the data array of field0
    # ----------------------------------------------------------------
    if m0._hasData:
        data_axes0 = field0.data_axes()
        data_axes1 = field1.data_axes()

        # Ensure that both data arrays span the same axes, including
        # the aggregating axis.
        for axis1 in data_axes1:
            axis0 = dim1_name_map[axis1]
            if axis0 not in data_axes0:
                field0.expand_dims(0, axis0, i=True)
                data_axes0.append(axis0)

        for axis0 in data_axes0:
            axis1 = dim0_name_map[axis0]
            if axis1 not in data_axes1:
                field1.expand_dims(0, axis1, i=True)
                
        # Find the position of the concatenating axis
        if adim0 not in data_axes0:
            # Insert the aggregating axis at position 0 because is not
            # already spanned by either data arrays
            field0.expand_dims(0, adim0, i=True)
            field1.expand_dims(0, adim1, i=True)
            axis = 0
        else:            
            axis = data_axes0.index(adim0)

        # Ensure that the axis orders are the same in both fields
        transpose_axes1 = [dim0_name_map[axis0] for axis0 in data_axes0]
        if transpose_axes1 != data_axes1:
            field1.transpose(transpose_axes1, i=True)

        if direction0:
            # The fields are increasing along the aggregating axis
            field0.Data = Data.concatenate((field0.Data, field1.Data), axis,
                                           _preserve=False)
        else:
            # The fields are decreasing along the aggregating axis
            field0.Data = Data.concatenate((field1.Data, field0.Data), axis,
                                           _preserve=False)
    #--- End: if

    # Update the size of the aggregating axis in field0
#    domain0._axes_sizes[adim0] += domain1._axes_sizes[adim1]
#    field0.Axes[adim0] += field1.axis_size(adim1)
    field0.axes()[adim0] += field1.axis_size(adim1)

    # Make sure that field0 has a standard_name, if possible.
    if getattr(field0, 'id', None) is not None:
        standard_name = field1.getprop('standard_name', None)
        if standard_name is not None:
            field0.standard_name = standard_name
            del field0.id
    #--- End: if

    #-----------------------------------------------------------------
    # Update the properties in field0
    #-----------------------------------------------------------------
    for prop in set(field0._simple_properties()) | set(field1._simple_properties()):
        value0 = field0.getprop(prop, None)
        value1 = field1.getprop(prop, None)
        
        if prop in ('valid_min', 'valid_max', 'valid_range'):
            if not m0.respect_valid:
                try:
                    field0.delprop(prop) 
                except AttributeError:
                    pass
            #--- End: if
            continue
        #--- End: if
             
        if prop == '_FillValue' or prop == 'missing_value':
            continue
        
        # Still here?  
        if equals(value0, value1):
            continue
               
        if concatenate:
            if value1 is not None:
                if value0 is not None:
                    field0.setprop(prop, '%s :AGGREGATED: %s' % (value0, value1))
                else:
                    field0.setprop(prop, ' :AGGREGATED: %s' % value1)
        else:
            if value0 is not None:
                field0.delprop(prop)            
    #--- End: for

    #-----------------------------------------------------------------
    # Update the attributes in field0
    #-----------------------------------------------------------------
    for attr in m0.attributes | m1.attributes:
        value0 = getattr(field0, attr, None)
        value1 = getattr(field1, attr, None)
        if equals(value0, value1):
            continue

        if concatenate:
            if value1 is not None:
                if value0 is not None:
                    setattr(field0, attr, '%s :AGGREGATED: %s' % (value0, value1))
                else:
                    setattr(field0, attr, ' :AGGREGATED: %s' % value1)
        else:
            m0.attributes.discard(attr)
            if value0 is not None:
                delattr(field0, attr)
    #--- End: for

    # Note that the field in this _Meta object has already been
    # aggregated
    m0.aggregated_field = True

    # ----------------------------------------------------------------
    # Return the _Meta object containing the aggregated field
    # ----------------------------------------------------------------
    return m0
#--- End: def

def _aggregate_coordrefs(m0, m1,
                         axis=None,
                         rtol=None, atol=None, 
                         respect_valid=False,
                         relaxed_units=False,
                         no_overlap=False,
                         info=0,
                         contiguous=False,
                         relaxed_identities=False,
                         ncvar_identities=False,
                         shared_nc_domain=False):
    '''

Aggregate fields in coordinate references.

:Parameters:

    m0 : _Meta

    m1 : _Meta

    no_overlap: `bool`, optional
        See the `aggregate` function for details.

    contiguous: `bool`, optional
        See the `aggregate` function for details.
   
    rtol : float, optional
        See the `aggregate` function for details.

    atol : float, optional
        See the `aggregate` function for details.
   
    info : int, optional
        See the `aggregate` function for details.
   
    relaxed_units: `bool`, optional
        See the `aggregate` function for details.

:Returns:

    out : dict

'''
#    axis = m0.a_identity

    field0 = m0.field
    field1 = m1.field

    out = {}

    for signature in m0.coordref_signatures:
        name = signature[0]

        key, coordref0 = field0.refs(name, exact=True).popitem()

        coordref1 = field1.ref(name, exact=True)

        # Initialize the new coordinate reference
        new_coordref = CoordinateReference(name=name)
          
        for term in set(coordref0).union(coordref1):

            value0 = coordref0.get(term, None)
            value1 = coordref1.get(term, None)

            if value1 is None and value0 is None:
                # ----------------------------------------------------
                # Both terms are undefined
                # ----------------------------------------------------
                continue

            if value1 is None:
                t, u, m, value = coordref0, coordref1, m0, value0
            elif value0 is None:
                t, u, m, value = coordref1, coordref0, m1, value1
            else:
                t = None

            if t is not None:
                # ----------------------------------------------------
                # Exactly one term is undefined
                # ----------------------------------------------------
                if term in t.coord_terms:
                    # Term is a coordinate
                    value = m.field.item(t[term], exact=True)
                    if value is None:
                        continue
                #--- End: if

                default = t.default_value(term)
                if default is None:
                    if info:
                        m1.message = \
"%r %s %r parameter has no default value" % (name, t.type, term)
                    return

                if isinstance(value, Field):
                    x = _Meta(value, info=info,
                              relaxed_units=relaxed_units,
                              allow_no_identity=True,
                              relaxed_identities=relaxed_identities,
                              ncvar_identities=ncvar_identities,
                              respect_valid=respect_valid)
                        
                    if not x:
                        if info:
                            m1.message = \
"%r %s %r parameter is a field with no structural signature" % \
(name, t.type, term)
                        return
                #--- End: if

                if not allclose(value, default, rtol=rtol, atol=atol):
                    if info:
                        m1.message = \
"%r %s %r parameters have non-equivalent values" % (name, t.type, term)
                    return

                # Update the new coordinate reference
                if term in t.coord_terms:
                    new_coordref.setcoord(term, t[term])
                else:
                    new_coordref[term] = value

                continue

            else:
                t = coordref0
            #--- End: if

            coord0 = term in coordref0.coord_terms
            coord1 = term in coordref1.coord_terms

            if coord0 and coord1:
                # ----------------------------------------------------
                # Both terms are coordinates
                # ---------------------------------------------------- 
                coord0 = field0.item(value0, exact=True)
                coord1 = field1.item(value1, exact=True)

                coord0_name = coord0.name(identity=m0.strict_identities,
                                          ncvar=m0.ncvar_identities)
                coord1_name = coord1.name(identity=m1.strict_identities,
                                          ncvar=m1.ncvar_identities)

                if (coord0 is None or
                    coord1 is None or
                    coord0_name != coord1_name):
                    if info:
                        m1.message = \
"%r %s %r parameters are unaggregatable coordinates" % \
(name, t.type, term)
                    return

                # Update the new coordinate reference
                new_coordref.setcoord(term, value0)
                continue

            if coord0 or coord1:
                # ----------------------------------------------------
                # Exactly one term is a coordinate
                # ----------------------------------------------------
                if info:
                    m1.message = \
"%r %s %r parameters are not all coordinates" % (name, t.type, term)
                return
            
            is_field0 = isinstance(value0, Field)
            is_field1 = isinstance(value1, Field)

            if not is_field0 and not is_field1:
                # ----------------------------------------------------
                # Neither term is a field
                # ----------------------------------------------------
                if not allclose(value0, value1, rtol=rtol, atol=atol):
                    # The values are not equivalent                    
                    if info:
                        m1.message = \
"%r %s %r parameters have non-equivalent values" % (name, t.type, term)
                    return

                # Update the new coordinate reference
                new_coordref[term] = value0
                continue

            if is_field0 != is_field1:
                # ----------------------------------------------------
                # Exactly one term is a field
                # ----------------------------------------------------
                if info:
                    m1.message = \
"%r %s %r parameters are not all fields" % (name, t.type, term)
                return
            
            # --------------------------------------------------------
            # Both terms are fields
            # --------------------------------------------------------

            if shared_nc_domain:
                role = '%r %s %r' % (name, t.type, term)
                value0, message0 = _share_nc_domain(value0, field0, role)
                if message0:
                    if info:
                        m0.message = message0
                    return
                #--- End: if
                value1, message1 = _share_nc_domain(value1, field1, role)
                if message1:
                    if info:
                        m1.message = message1
                    return
                #--- End: if
            #--- End: if

            x0 = _Meta(value0, info=info,
                       relaxed_units=relaxed_units,
                       allow_no_identity=True,
                       relaxed_identities=relaxed_identities,
                       ncvar_identities=ncvar_identities,
                       respect_valid=respect_valid)
            x1 = _Meta(value1, info=info,
                       relaxed_units=relaxed_units, 
                       allow_no_identity=True,
                       relaxed_identities=relaxed_identities,
                       ncvar_identities=ncvar_identities,
                       respect_valid=respect_valid)

            if not (x0 and x1):
                # At least one field doesn't have a structual
                # signature
                if info:
                    m1.message = \
"%r %s %r parameter is a field with no structural signature" % \
(name, t.type, term)
                return
            #--- End: if

            if axis not in x0.axis and axis not in x1.axis:
                # Neither field spans the aggregating axis ...
                if value0.equivalent_data(value1, rtol=rtol, atol=atol):
                    # ... and the fields have equivalent data
                    # arrays. Therefore we don't need to do any
                    # aggregation.
                    # Update the new coordinate reference
                    new_coordref[term] = value0
                    continue
                else:
                    # ... and the fields do not have equivalent data
                    if info:
                        m1.message = \
"%r %s %r parameters are fields with non-equivalent values" % \
(name, t.type, term)
                    return
            #--- End: if

            if not (axis in x0.axis and axis in x1.axis):
                # Only one of the fields spans the aggregating axis
                if info:
                    m1.message = \
"%r %s %r parameters are unaggregatable fields" % (name, t.type, term)

                return
            #--- End: if
            
            # Both fields span the aggregating axis, so try to
            # aggregate them.
            new_value = aggregate((value0, value1),
                                  info=info,
                                  no_overlap=no_overlap,
                                  contiguous=contiguous,
                                  respect_valid=respect_valid,
                                  relaxed_units=relaxed_units,
                                  allow_no_identity=True,
                                  axes=axis,
                                  relaxed_identities=relaxed_identities,
                                  ncvar_identities=ncvar_identities)

            if len(new_value) == 2:
                # Couldn't aggregate them (because we got two fields
                # back instead of one)
                if info:
                    m1.message = \
"%r %s %r parameters are unaggregatable fields" % (name, t.type, term)

                return
            #--- End: if

            # Successfully aggregated the coordinate reference fields
            coordref0[term] = new_value[0]             # DCH: Why?????????
            # Update the new coordinate reference
            new_coordref[term] = new_value[0]
        #---End: for

        out[key] = new_coordref
    #---End: for

    return out
#--- End: def

#def _aggregate_ancillary_variables(m0, m1,
#                                   axis=None,
#                                   rtol=None, atol=None,
#                                   respect_valid=False,
#                                   relaxed_units=False,
#                                   no_overlap=False,
#                                   info=0,
#                                   contiguous=False,
#                                   relaxed_identities=False,
#                                   ncvar_identities=False,
#                                   shared_nc_domain=False):
#    '''
#
#Aggregate the ancillary variable fields.
#
#:Parameters:
#
#    m0 : _Meta
#
#    m1 : _Meta
#
#    no_overlap: `bool`, optional
#        See the `aggregate` function for details.
#
#    contiguous: `bool`, optional
#        See the `aggregate` function for details.
#   
#    rtol : float, optional
#        See the `aggregate` function for details.
#
#    atol : float, optional
#        See the `aggregate` function for details.
#   
#    info : int, optional
#        See the `aggregate` function for details.
#   
#    relaxed_units: `bool`, optional
#        See the `aggregate` function for details.
#
#    relaxed_identities: `bool`, optional
#        See the `aggregate` function for details.
#
#    ncvar_identities: `bool`, optional
#        See the `aggregate` function for details.
#
#:Returns:
#
#    out : cf.FieldList or bool
#
#'''
#    field0 = m0.field
#    field1 = m1.field
#
#    ancillary_variables = m0.ancillary_variables
#
##    new_ancillary_variables = AncillaryVariables()
#    new_ancillary_variables = FieldList()
#
#    for identity, ancil0 in ancillary_variables.iteritems():
#        ancil1 = m1.ancillary_variables[identity]
#
#        if shared_nc_domain:
#            ancil0, message0 = _share_nc_domain(ancil0, field0, 'ancillary variable')
#            if message0:
#                if info:
#                    m0.message = message0
#                return
#            #--- End: if
#            ancil1, message1 = _share_nc_domain(ancil1, field1, 'ancillary variable')
#            if message1:
#                if info:
#                    m1.message = message1
#                return
#            #--- End: if
#        #--- End: if
#
#        x0 = _Meta(ancil0, info=info, relaxed_units=relaxed_units,
#                   allow_no_identity=False,
#                   relaxed_identities=relaxed_identities,
#                   ncvar_identities=ncvar_identities,
#                   respect_valid=respect_valid)
#        x1 = _Meta(ancil1, info=info, relaxed_units=relaxed_units,
#                   allow_no_identity=False,
#                   relaxed_identities=relaxed_identities,
#                   ncvar_identities=ncvar_identities,
#                   respect_valid=respect_valid)
#        
#        if not (x0 and x1):
#            # At least one field doesn't have a structual signature
#            if info:
#                m1.message = \
#"%r ancillary variable is a field with no structural signature" % \
#ancil0.name('')
#            return
#        #--- End: if
#            
#        if axis not in x0.axis and axis not in x1.axis:
#            # Neither field spans the aggregating axis ...
#            if ancil0.equivalent_data(ancil1, rtol=rtol, atol=atol,
#                                      traceback=False):
#                # ... and the fields are equivalent
#                new_ancillary_variables.append(ancil0)
#                continue
#            else:
#                # ... and the fields are not equivalent
#                if info: 
#                    m1.message = \
#"2 %r ancillary variable fields have non-equivalent values" % ancil0.name('')
#
#                return
#        #--- End: if
#
#        # Still here?    
#        if not (axis in x0.axis and axis in x1.axis):
#            if info:
#                m1.message = \
#"3 %r ancillary variable fields are unaggregatable" % ancil0.name('')
#
#            return
#        #--- End: if
#            
#        # Both fields span the aggregating axis
#        if (ancil0.axis_size(axis, exact=True) == 1 and
#            ancil1.axis_size(axis, exact=True) == 1 and
#            field0.axis_size(axis, exact=True) > 1 or
#            field1.axis_size(axis, exact=True) > 1):
#            # The aggregating axis has size 1 in both ancillary fields
#            # and size > 1 in at least one parent field
#            if ancil0.equivalent(ancil1, rtol=rtol, atol=atol):
#                ancillary_variables[identity] = ancil0 ### WHY??
#                new_ancillary_variables.append(ancil0)
#                continue
#        #--- End: if
#
#        # Still here? Then try to aggregate the ancillary fields.
#        new_value = aggregate((ancil0, ancil1), info=info, 
#                              no_overlap=no_overlap, contiguous=contiguous,
#                              respect_valid=respect_valid,
#                              relaxed_units=relaxed_units,
#                              allow_no_identity=True,
#                              axes=axis,
#                              relaxed_identities=relaxed_identities,
#                              ncvar_identities=ncvar_identities)
#        
#        if len(new_value) == 2:
#            # We got two fields back instead of one, therefore they
#            # couldn't be aggregated.
#            if info:
#                m1.message = \
#"4 %r ancillary variable fields are unaggregatable" % ancil0.name('')
#
#            return
#        #--- End: if
#
#        # Update the m0.ancillary_variable dictionary, because it
#        # needs to contain the aggregated field.
#        ancillary_variables[identity] = new_value[0]
#
#        new_ancillary_variables.append(new_value[0])
#    #---End: for
#
#    return new_ancillary_variables
##--- End: def

def _share_nc_domain(child, field, role):
    '''

perhaps this should be `cf.Field.share_nc_domain`, as it may be useful
in general.

'''
    child_axis_to_ncdim = getattr(child, 'ncdimensions', {})
    if len(set(child_axis_to_ncdim.values())) != len(child_axis_to_ncdim):
        message = \
"%s %s field can't share domain with its parent field (ambiguous netCDF dimension names)" % \
(role, child.name(''))
        return None, message
    #--- End: if

    field_axis_to_ncdim = getattr(field, 'ncdimensions', {})
    n_axes = len(field_axis_to_ncdim)
    field_ncdim_to_axis = dict([(v, k) for k, v in field_axis_to_ncdim.iteritems()])
    if len(field_ncdim_to_axis) != n_axes:
        message = \
"%s %s field can't share domain with its parent field (ambiguous netCDF dimension names)" % \
(role, child.name(''))
        return None, message
    #--- End: if

    # Remove all items from the childlary field
    new_child = child.copy()
    new_child.remove_items()

    for c_axis in child.data_axes():
        # Find the parent field axis (f_axis) which correposnds to the
        # child field axis (c_axis)

        c_ncdim = child_axis_to_ncdim.get(c_axis, None)
        f_axis = field_ncdim_to_axis.get(c_ncdim, None)
        if f_axis is None:
            message = \
"%s %s field can't share domain with its parent field (axis has no netCDF dimension name)" % \
(role, child.name(''))
            return None, message
        #--- End: if
            
        # Copy 1-d dimension and auxiliary coordinates from the parent
        # field to the child field
        for coord in field.coords(axes=f_axis, ndim=1).itervalues():
            if coord.isdimension:
                new_child.insert_dim(coord, axis=c_axis)
            else:                        
                new_child.insert_aux(coord, axes=(c_axis,))
        #--- End: for
    #--- End: for

    return new_child, None
#--- End: def

def ensemble(f, prop, **kwargs):
    '''
'''
    kwargs.pop('dimension', None)

    # Check that the fields are all compatible
    kwargs['copy'] = True
    if len(cf.aggregate(f, **kwargs)) != len(f):
           raise ValueError("")

    f = f.copy()

    all_props = set()

    for i, g in enumerate(f):
        if not g.hasprop(prop):
            j = i
            while str(j) in all_props:
                j += 1
            j = str(j)
        else:
            j = str(g.getprop(prop))

        g.setprop(prop, j)
        all_props.add(j)
    #--- End: for

    kwargs['dimension'] = (prop,)
 
    kwargs['copy'] = False
    f = aggregate(f, **kwargs)
    
    # Check that the fields were aggreageted down to one field
    if len(f) != 1:
        raise ValueError("sd ;oo08 z;kln poih [")
    
    return f
#--- End: def
