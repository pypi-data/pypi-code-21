from glob    import glob
from os      import walk as os_walk
from os.path import isdir, isfile
from os.path import join as os_path_join
from os.path import expandvars as os_path_expandvars
from os.path import expanduser as os_path_expanduser

from .field     import Field, FieldList
from .functions import flat
from .aggregate import aggregate as cf_aggregate

from .netcdf.read import read as netcdf_read
from .netcdf.read import is_netcdf_file
from .um.read     import read as um_read
from .um.read     import is_um_file

def read(files, verbose=False, ignore_read_error=False,
         aggregate=True, nfields=None, squeeze=False, unsqueeze=False,
         fmt=None, select=None, select_options={}, field=None,
         height_at_top_of_model=None, recursive=False,
         follow_symlinks=False, um=None, chunk=True, _debug=False):
    '''Read fields from netCDF, PP or UM fields files.

Files may be on disk or on a OPeNDAP server.

Any amount of any combination of CF-netCDF and CFA-netCDF files (or
URLs if DAP access is enabled), Met Office (UK) PP files and Met
Office (UK) fields files format files may be read.

**Notes for PP and UM fields files**
   * The *aggregate* option ``'relaxed_units'`` is set to True for all
     input files.
    
   * STASH code to standard conversion uses the table in
     ``cf/etc/STASH_to_CF.txt``.

**Notes for files on OPeNDAP servers**
   * All files on OPeNDAP servers are assumed to be netCDF files.

.. seealso:: `cf.read_field`, `cf.write`

:Examples 1:

>>> f = cf.read('file.nc')

:Parameters:

    files: (arbitrarily nested sequence of) `str`

        A string or arbitrarily nested sequence of strings giving the
        file names or OPenDAP URLs from which to read fields. Various
        type of expansion are applied to the file names:
        
          ====================  ======================================
          Expansion             Description
          ====================  ======================================
          Tilde                 An initial component of ``~`` or
                                ``~user`` is replaced by that *user*'s
                                home directory.
           
          Environment variable  Substrings of the form ``$name`` or
                                ``${name}`` are replaced by the value
                                of environment variable *name*.

          Pathname              A string containing UNIX file name
                                metacharacters as understood by the
                                :py:obj:`glob` module is replaced by
                                the list of matching file names. This
                                type of expansion is ignored for
                                OPenDAP URLs.
          ====================  ======================================
    
        Where more than one type of expansion is used in the same
        string, they are applied in the order given in the above
        table.

          Example: If the environment variable *MYSELF* has been set
          to the "david", then ``'~$MYSELF/*.nc'`` is equivalent to
          ``'~david/*.nc'``, which will read all netCDF files in the
          user david's home directory.
  
    verbose: `bool`, optional
        If True then print information to stdout.
    
    umversion:
        Deprecated. Use the *um* parameter instead.

    ignore_read_error: `bool`, optional
        If True then ignore any file which raises an IOError whilst
        being read, as would be the case for an empty file, unknown
        file format, etc. By default the IOError is raised.
    
    fmt: `str`, optional
        Only read files of the given format, ignoring all other
        files. Valid formats are ``'NETCDF'`` for CF-netCDF files,
        ``'CFA'`` for CFA-netCDF files and ``'PP'`` for PP files and
        'FF' for UM fields files. By default files of any of these
        formats are read.  default files of any of these formats are
        read.

    aggregate: `bool` or `dict`, optional
        If True (the default) or a (possibly empty) dictionary then
        aggregate the fields read in from all input files into as few
        fields as possible using the CF aggregation rules. If
        *aggregate* is a dictionary then it is passed as keyword
        arguments to the `cf.aggregate` function. If False then the
        fields are not aggregated.

    squeeze: `bool`, optional
        If True then remove size 1 axes from each field's data array.

    unsqueeze: `bool`, optional
        If True then insert size 1 axes from each field's domain into
        its data array.

    select, select_options: optional
        Only return fields which satisfy the given conditions on their
        property values. Only fields which, prior to any aggregation,
        satisfy ``f.match(description=select, **select_options) ==
        True`` are returned. See `cf.Field.match` for details.

    field: (sequence of) `str`, optional
        Create independent fields from field components. The *field*
        parameter may be one, or a sequence, of:

          ======================  ====================================
          *field*                 Field components
          ======================  ====================================
          ``'field_ancillary'``   Field ancillary objects
          ``'domain_ancillary'``  Domain ancillary objects
          ``'dimension'``         Dimension coordinate objects
          ``'auxiliary'``         Auxiliary coordinate objects
          ``'measure'``           Cell measure objects
          ``'all'``               All of the above
          ======================  ====================================

            *Example:*
              To create fields from auxiliary coordinate objects:
              ``field='auxiliary'`` or ``field=['auxiliary']``.

            *Example:*
              To create fields from domain ancillary and cell measure
              objects: ``field=['domain_ancillary', 'measure']``.

        .. versionadded:: 1.0.4

    recursive: `bool`, optional
        If True then allow directories to be specified by the *files*
        parameter and recursively search the directories for files to
        read.

        .. versionadded:: 1.1.9

    follow_symlinks: `bool`, optional
        If True, and *recursive* is True, then also search for files
        in directories which resolve to symbolic links. By default
        directories which resolve to symbolic links are
        ignored. Ignored of *recursive* is False. Files which are
        symbolic links are always followed.

        Note that setting ``recursive=True, follow_symlinks=True`` can
        lead to infinite recursion if a symbolic link points to a
        parent directory of itself.

        .. versionadded:: 1.1.9

    um: `dict`, optional
        For Met Office (UK) PP files and Met Office (UK) fields files
        only, provide extra decoding instructions. This option is
        ignored for input files which are not PP or fields files. In
        most cases, how to decode a file is inferrable from the file's
        contents, but if not then each key/value pair in the
        dictionary sets a decoding option as follows:

          ===============  ===========================================
          Key              Value
          ===============  ===========================================
          ``'fmt'``        The file format (``'PP'`` or ``'FF'``)

          ``'word_size'``  The word size in bytes (``4`` or ``8``)

          ``'endian'``     The byte order (``'big'`` or ``'little'``)

          ``'version'``    The Unified Model version to be used when
                           decoding the header. Valid versions are,
                           for example, ``4.2``, ``'6.6.3'`` and
                           ``'8.2'``. The default version is
                           ``4.5``. In general, a given version is
                           ignored if it can be inferred from the
                           header (which is usually the case for files
                           created by the UM at versions 5.3 and
                           later). The exception to this is when the
                           given version has a third element (such as
                           the 3 in 6.6.3), in which case any version
                           in the header is ignored.
          ===============  ===========================================

        If format is specified as PP then the word size and byte order
        default to ``4`` and ``'big'`` repsectively.

          *Example:*
            To specify that the input files are 32-bit, big-endian
            PP files: ``um={'fmt': 'PP'}``

          *Example:*
            To specify that the input files are 32-bit,
            little-endian PP files from version 5.1 of the Unified
            Model: ``um={'fmt': 'PP', 'endian': 'little', 'version':
            5.1}``

        .. versionadded:: 1.5


:Returns:
    
    out: `cf.FieldList`
        A list of the fields found in the input file(s). The list may
        be empty.

:Examples 2:

>>> f = cf.read('file*.nc')
>>> f
[<CF Field: pmsl(30, 24)>,
 <CF Field: z-squared(17, 30, 24)>,
 <CF Field: temperature(17, 30, 24)>,
 <CF Field: temperature_wind(17, 29, 24)>]

>>> cf.read('file*.nc')[0:2]
[<CF Field: pmsl(30, 24)>,
 <CF Field: z-squared(17, 30, 24)>]

>>> cf.read('file*.nc')[-1]
<CF Field: temperature_wind(17, 29, 24)>

>>> cf.read('file*.nc', select='units:K)
[<CF Field: temperature(17, 30, 24)>,
 <CF Field: temperature_wind(17, 29, 24)>]

>>> cf.read('file*.nc', select='ncvar%ta')
<CF Field: temperature(17, 30, 24)>

>>> cf.read('file*.nc', select={'standard_name': '.*pmsl*', 'units':['K', 'Pa']})
<CF Field: pmsl(30, 24)>

>>> cf.read('file*.nc', select={'units':['K', 'Pa']})
[<CF Field: pmsl(30, 24)>,
 <CF Field: temperature(17, 30, 24)>,
 <CF Field: temperature_wind(17, 29, 24)>]

    '''
    if squeeze and unsqueeze:
        raise ValueError("squeeze and unsqueeze can not both be True")

    if follow_symlinks and not recursive:
        raise ValueError(
            "Can't set follow_symlinks={0} when recursive={1}".format(
                follow_symlinks, recursive))

    # Initialize the output list of fields
    field_list = FieldList()

    if isinstance(aggregate, dict):
        aggregate_options = aggregate.copy()
        aggregate         = True
    else:
        aggregate_options = {}

    aggregate_options['copy'] = False
    
    # Parse the field parameter
    if field is None:
        field = ()
    elif isinstance(field, basestring):
        field = (field,)

    # Count the number of fields (in all files) and the number of
    # files
    field_counter = -1
    file_counter  = 0

    for file_glob in flat(files):

        # Expand variables
        file_glob = os_path_expanduser(os_path_expandvars(file_glob))

        if file_glob.startswith('http://'):
            # Do not glob a URL
            files2 = (file_glob,)
        else:
            # Glob files on disk
            files2 = glob(file_glob)
            
            if not files2 and not ignore_read_error:
                open(file_glob, 'rb')
                
            if recursive:
                files3 = []
                for x in files2:
                    if isdir(x):
                        # Recursively walk through directories
                        for path, subdirs, filenames in os_walk(x, followlinks=True):
                            files3.extend(os_path_join(path, f) for f in filenames)
                    else:
                        files3.append(x)
                files2 = files3
            else:
                for x in files2:
                    if isdir(x) and not ignore_read_error:
                        raise IOError(
"Can't read directory {0} recursively unless recursive=True".format(x))
        #--- End: if

        for filename in files2:
            if verbose:
                print 'File: {0}'.format(filename)
                
            # --------------------------------------------------------
            # Read the file into fields
            # --------------------------------------------------------
            fields = _read_a_file(filename,
                                  ignore_read_error=ignore_read_error,
                                  verbose=verbose,
                                  aggregate=aggregate,
                                  aggregate_options=aggregate_options,
                                  selected_fmt=fmt,
                                  um=um,
                                  field=field,
                                  height_at_top_of_model=height_at_top_of_model,
                                  chunk=chunk,
                                  _debug=_debug)
            
            # --------------------------------------------------------
            # Select matching fields
            # --------------------------------------------------------
            if select or select_options:
                fields = fields.select(select, **select_options)

            # --------------------------------------------------------
            # Add this file's fields to those already read from other
            # files
            # --------------------------------------------------------
            field_list.extend(fields)
   
            field_counter = len(field_list)
            file_counter += 1
        #--- End: for            
    #--- End: for     

#    # Error check
#    if not ignore_read_error:
#        if not file_counter:
#            raise RuntimeError('No files found')
#        if not field_list:
#            raise RuntimeError('No fields found from '+str(file_counter)+' files')
#    #--- End: if

    # Print some informative messages
    if verbose:
        print("Read {0} field{1} from {2} file{3}".format( 
            field_counter, _plural(field_counter),
            file_counter , _plural(file_counter)))
    #--- End: if
   
    # ----------------------------------------------------------------
    # Aggregate the output fields
    # ----------------------------------------------------------------
    if aggregate and len(field_list) > 1:
        if verbose:
            org_len = len(field_list)
            
        field_list = cf_aggregate(field_list, **aggregate_options)
        
        if verbose:
            n = len(field_list)
            print('{0} input field{1} aggregated into {2} field{3}'.format(
                org_len, _plural(org_len), 
                n, _plural(n)))
    #--- End: if

#    # ----------------------------------------------------------------
#    # Add standard names to UM fields
#    # ----------------------------------------------------------------
#    for f in field_list:
#        standard_name = getattr(f, '_standard_name', None)
#        if standard_name is not None:
#            f.standard_name = standard_name
#            del f._standard_name
#    #--- End: for

    # ----------------------------------------------------------------
    # Squeeze size one dimensions from the data arrays. Do one of:
    # 
    # 1) Squeeze the fields, i.e. remove all size one dimensions from
    #    all field data arrays
    #
    # 2) Unsqueeze the fields, i.e. Include all size 1 domain
    #    dimensions in the data array.
    #
    # 3) Nothing
    # ----------------------------------------------------------------
    if squeeze:
        for f in field_list:
            f.squeeze(i=True) 
    elif unsqueeze:
        for f in field_list:
            f.unsqueeze(i=True)
            
    if nfields is not None and len(field_list) != nfields:
        raise ValueError(
"{} field{} requested but {} fields found in file{}".format(
    nfields, _plural(nfields), len(field_list), _plural(file_counter)))

    return field_list
#--- End: def

def read1(*args, **kwargs):
    '''Read a single field from netCDF, PP or UM fields files.

.. versionadded:: 2.0

.. seealso:: `cf.read`

    '''
    print "WARNING: Use cf.read_field in favour of cf.read1. cf.read1 will be deprecated at a later version"
    return read_field(*args, **kwargs)
#--- End: def


def read_field(*args, **kwargs):
    '''Read a single field from netCDF, PP or UM fields files.

If not exactly one field is found in the input files then an error is
raised. Files should be read with `cf.read` unless it is known that
only one field will be created from them.

Note that if field aggregation is on (as is it by default), then the
number of fields is that after teh inputs have been aggregated.

Files may be on disk or on a OPeNDAP server.

Any amount of any combination of CF-netCDF and CFA-netCDF files (or
URLs if DAP access is enabled), Met Office (UK) PP files and Met
Office (UK) fields files format files may be read.

**Notes for PP and UM fields files**
   * The *aggregate* option ``'relaxed_units'`` is set to True for all
     input files.
    
   * STASH code to standard conversion uses the table in
     ``cf/etc/STASH_to_CF.txt``.

**Notes for files on OPeNDAP servers**
   * All files on OPeNDAP servers are assumed to be netCDF files.

Note that ``f=cf.read_field(*args, **kwargs)`` is equivalent to
``f=cf.read(*args, nfields=1, **kwargs)[0]``.

.. versionadded:: 2.0.3

.. seealso:: `cf.read`, `cf.write`

:Examples 1:

>>> f = cf.read_field('file.nc')

:Parameters:

    args, kwargs: optional
        Any arguments and keyword arguments accepted by `cf.read`.

:Returns:

    out `cf.Field`
        The unique field from the input file(s).

:Examples 2:

>>> f = cf.read_field('file.nc')
>>> f = cf.read_field('file[1-9].nc', select='air_temperature')

    '''
    kwargs['nfields'] = 1
    return read(*args, **kwargs)[0]
#--- End: def


def _plural(n):
    '''Return a suffix which reflects a word's plural.

    '''
    return 's' if n !=1 else ''

def _read_a_file(filename,
                 aggregate=True,
                 aggregate_options={},
                 ignore_read_error=False,
                 verbose=False,
                 selected_fmt=None,
                 um=None,
                 field=(),
                 height_at_top_of_model=None,
                 chunk=True,
                 _debug=False):
    '''

Read the contents of a single file into a field list.

:Parameters:

    filename: `str`
        The file name.

    aggregate_options: `dict`, optional
        The keys and values of this dictionary may be passed as
        keyword parameters to an external call of the aggregate
        function.

    ignore_read_error : bool, optional
        If True then return an empty field list if reading the file
        produces an IOError, as would be the case for an empty file,
        unknown file format, etc. By default the IOError is raised.
    
    verbose : bool, optional
        If True then print information to stdout.
    
:Returns:

    out : FieldList
        The fields in the file.

:Raises:

    IOError :
        If *ignore_read_error* is False and

        * The file can not be opened.

        * The file can not be opened.

'''
    # Find this file's type
    fmt       = None
    word_size = None
    endian    = None
    umversion = 405

    if um:
        ftype = 'UM' 
        fmt         = um.get('fmt')
        word_size   = um.get('word_size')
        endian      = um.get('endian')
        umversion   = um.get('version')
        if fmt in ('PP', 'pp'):
            fmt = fmt.upper()
            # For PP format, there is a default word size and
            # endian-ness
            if word_size is None:
                word_size = 4
            if endian is None:
                endian = 'big'
        #--- End: if
        if umversion is not None:
            umversion = float(str(umversion).replace('.', '0', 1))
    else:
        try:
            ftype = file_type(filename)        
        except Exception as error:
            if ignore_read_error: 
                if verbose:
                    print('WARNING: %s' % error)
                return FieldList()
            raise Exception(error)
    #--- End: if
    
    # ----------------------------------------------------------------
    # Still here? Read the file into fields.
    # ----------------------------------------------------------------
    if ftype == 'netCDF' and (selected_fmt in (None, 'NETCDF', 'CFA')):
        fields = netcdf_read(filename, fmt=selected_fmt, field=field,
                             verbose=verbose, chunk=chunk,
                             _debug=_debug)
        
    elif ftype == 'UM' and (selected_fmt in (None, 'PP', 'FF')):
        fields = um_read(filename, um_version=umversion,
                         verbose=verbose, set_standard_name=True,
                         height_at_top_of_model=height_at_top_of_model,
                         fmt=fmt, word_size=word_size, endian=endian,
                         chunk=chunk, _debug=_debug)

        # PP fields are aggregated intrafile prior to interfile
        # aggregation
        if aggregate:
            # For PP fields, the default is strict_units=False
            if 'strict_units' not in aggregate_options:
                aggregate_options['relaxed_units'] = True
        #--- End: if

    # Add more file formats here ...

    else:
        fields = FieldList()

    # ----------------------------------------------------------------
    # Return the fields
    # ----------------------------------------------------------------
    return fields
#--- End: def

def file_type(filename):
    '''

:Parameters:

    filename : str
        The file name.

:Returns:

    out : str
        The format type of the file.

:Raises:
 
    IOError :
        If the file has an unsupported format.

:Examples:

>>> ftype = file_type(filename)

''' 
    # ----------------------------------------------------------------
    # Assume that URLs are in netCDF format
    # ----------------------------------------------------------------
    if filename.startswith('http://'):
       return 'netCDF'

    # ----------------------------------------------------------------
    # netCDF
    # ----------------------------------------------------------------
    if is_netcdf_file(filename):
        return 'netCDF'

    # ----------------------------------------------------------------
    # PP or FF
    # ----------------------------------------------------------------
    if is_um_file(filename):
        return 'UM'

    # ----------------------------------------------------------------
    # Developers: Add more file formats here ...
    # ----------------------------------------------------------------

    # Still here?
    raise IOError("Can't determine format of file {}".format(filename))
#--- End: def
