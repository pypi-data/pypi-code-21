import os

from . import config, tmpfiles, pysamtools, snap
from . import ArgumentParseError


def clone_index (file_to_index, index_file_to_clone, index_format):
    """Make an existing index file usable with a differently named
    sequence file by creating an appropriately named clone of the index.

    Autodetects the cheapest possible cloning operation by trying
    hard linking, soft linking and copying of the index in this order.
    """
    
    if index_format not in ('bai', 'fai'):
        raise ValueError('index format needs to be "bai" or "fai".')
    index_name = '{0}.{1}'.format(file_to_index, index_format)
    # let the tmpfiles module do all the hard work
    tmpfiles.conditional_hardlink(index_file_to_clone, index_name)
    return index_name


def validate_index_files (files_to_index, index_files, index_format):
    """Given two iterables, of sequence and index file names, respectively,
    returns a zipped list of permissive [sequence, index file] or
    [sequence file, None] pairs.

    For a permissive pair, the index file must exist and, if the index file
    list was created from a Galaxy tool  wrapper the package configuration
    must allow the use of Galaxy-generated index files.
    """
    
    if index_format not in ('bai', 'fai'):
        raise ValueError('index format needs to be "bai" or "fai".')
    if index_files and len(index_files) != len(files_to_index):
        # if any index files are provided, require equal length of
        # the two iterables
        raise ArgumentParseError(
            'The number of index files provided (if any) '
            'must match the number of BAM input files.'
            )
    if not index_files or (not config.use_galaxy_index_files
                           and config.galaxy_context):
        # with no index files given we want to return pairs of
        # [sequence file, None] only
        index_files = [None] * len(files_to_index)
    zipped_answer = []
    for file_to_index, index_file in zip(files_to_index, index_files):
        if (
          index_file and os.path.isfile(index_file)
          and os.path.getmtime(index_file) > os.path.getmtime(file_to_index)
          ):
            zipped_answer.append([file_to_index, index_file])
        else:
            zipped_answer.append([file_to_index, None])
    return zipped_answer

    
def index (idxformat, ifile, opath=None, threads=None,
           quiet=False, verbose=False, **snap_options):
    if not os.path.isfile(ifile):
        raise FileNotFoundError(
            'File to index does not seem to exist: {0}'.format(ifile)
            )
    known_formats = ['fai', 'bai', 'snap']
    if idxformat not in known_formats:
        raise ArgumentParseError(
            'Unknown index format "{0}". Expected one of: {1}.'
            .format(idxformat, ', '.join(known_formats))
            )
    if idxformat == 'fai':
        pysamtools.faidx(ifile, opath, verbose=verbose)
    elif idxformat == 'bai':
        pysamtools.index(ifile, opath, reindex=True, verbose=verbose)
    else:
        if opath is None:
            opath = ifile + '.snap_index'
        snap.snap_index(
            ifile, opath,
            threads=threads, verbose=verbose, quiet=quiet,
            **snap_options
            )
