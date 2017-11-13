def ncread(file, vars=None, dims=False, noisy=False, atts=False):
    """
    Read in the FVCOM results file and spit out numpy arrays for each of the
    variables specified in the vars list.

    Optionally specify a dict with keys whose names match the dimension names
    in the NetCDF file and whose values are strings specifying alternative
    ranges or lists of indices. For example, to extract the first hundred time
    steps, supply dims as:

        dims = {'time':'0:100'}

    To extract the first, 400th and 10,000th values of any array with nodes:

        dims = {'node':'[0, 3999, 9999]'}

    Any dimension not given in dims will be extracted in full.

    Specify atts=True to extract the variable attributes.

    Parameters
    ----------
    file : str, list
        If a string, the full path to an FVCOM NetCDF output file. If a list,
        a series of files to be loaded. Data will be concatenated into a single
        dict.
    vars : list, optional
        List of variable names to be extracted. If omitted, all variables are
        returned.
    dims : dict, optional
        Dict whose keys are dimensions and whose values are a string of either
        a range (e.g. {'time':'0:100'}) or a list of individual indices (e.g.
        {'time':'[0, 1, 80, 100]'}). Slicing is supported (::5 for every fifth
        value) but it is not possible to extract data from the end of the array
        with a negative index (e.g. 0:-4).
    noisy : bool, optional
        Set to True to enable verbose output.
    atts : bool, optional
        Set to True to enable output of the attributes (defaults to False).

    Returns
    -------
    FVCOM : dict
        Dict of data extracted from the NetCDF file. Keys are those given in
        vars and the data are stored as ndarrays.
    attributes : dict, optional
        If atts=True, returns the attributes as a dict for each
        variable in vars. The key 'dims' contains the array dimensions (each
        variable contains the names of its dimensions) as well as the shape of
        the dimensions defined in the NetCDF file. The key 'global' contains
        the global attributes.

    See Also
    --------
    read_probes : read in FVCOM ASCII probes output files.

    """

    # If we have a list, assume it's lots of files and load them all.
    if isinstance(file, list):
        try:
            try:
                rootgrp = MFDataset(file, 'r')
            except IOError as msg:
                raise IOError('Unable to open file {} ({}). Aborting.'.format(file, msg))
        except:
            # Try aggregating along a 'time' dimension (for POLCOMS, for example)
            try:
                rootgrp = MFDataset(file, 'r', aggdim='time')
            except IOError as msg:
                raise IOError('Unable to open file {} ({}). Aborting.'.format(file, msg))

    else:
        rootgrp = Dataset(file, 'r')

    # Create a dict of the dimension names and their current sizes
    read_dims = {}
    for key, var in list(rootgrp.dimensions.items()):
        # Make the dimensions ranges so we can use them to extract all the
        # values.
        read_dims[key] = '0:' + str(len(var))

    # Compare the dimensions in the NetCDF file with those provided. If we've
    # been given a dict of dimensions which differs from those in the NetCDF
    # file, then use those.
    if dims:
        commonKeys = set(read_dims).intersection(list(dims.keys()))
        for k in commonKeys:
            read_dims[k] = dims[k]

    if noisy:
        print("File format: {}".format(rootgrp.file_format))

    if not vars:
        vars = iter(list(rootgrp.variables.keys()))

    FVCOM = {}

    # Save the dimensions in the attributes dict.
    if atts:
        attributes = {}
        attributes['dims'] = read_dims
        attributes['global'] = {}
        for g in rootgrp.ncattrs():
            attributes['global'][g] = getattr(rootgrp, g)

    for key, var in list(rootgrp.variables.items()):
        if noisy:
            print('Found ' + key, end=' ')
            sys.stdout.flush()

        if key in vars:
            vDims = rootgrp.variables[key].dimensions

            toExtract = [read_dims[d] for d in vDims]

            # If we have no dimensions, we must have only a single value, in
            # which case set the dimensions to empty and append the function to
            # extract the value.
            if not toExtract:
                toExtract = '.getValue()'

            # Thought I'd finally figured out how to replace the eval approach,
            # but I still can't get past the indexing needed to be able to
            # subset the data.
            # FVCOM[key] = rootgrp.variables.get(key)[0:-1]
            # I know, I know, eval() is evil.
            getData = 'rootgrp.variables[\'{}\']{}'.format(key, str(toExtract).replace('\'', ''))
            FVCOM[key] = eval(getData)

            # Add the units and dimensions for this variable to the list of
            # attributes.
            if atts:
                attributes[key] = {}
                try:
                    attributes[key]['units'] = rootgrp.variables[key].units
                except:
                    pass

                try:
                    attributes[key]['dims'] = rootgrp.variables[key].dimensions
                except:
                    pass

            if noisy:
                if len(str(toExtract)) < 60:
                    print('(extracted {})'.format(str(toExtract).replace('\'', '')))
                else:
                    print('(extracted given indices)')

        elif noisy:
                print()

    # Close the open file.
    rootgrp.close()

    if atts:
        return FVCOM, attributes
    else:
        return FVCOM

