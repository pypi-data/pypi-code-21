# modified from:
#
# https://github.com/konstantint/pyliftover,
# a pure-python implementation of UCSC "liftover" genome coordinate conversion.
#
#   Copyright 2013, Konstantin Tretyakov.
#   http://kt.era.ee/
#
#   Licensed under MIT license.
#
#   PyLiftover is a library for quick and easy conversion of genomic (point)
#   coordinates between different assemblies.
#
#   It uses the same logic and coordinate conversion mappings as the UCSC
#   `liftOver tool<http://genome.ucsc.edu/cgi-bin/hgLiftOver>`_.


import sys
import os
import gzip
import shutil
import urllib.request, urllib.error

from . import config, tmpfiles
from . import ArgumentValidationError

from .encoding_base import DEFAULTENCODING, FALLBACKENCODING
from .intervaltree import IntervalTree


CACHE_DIR = os.path.expanduser("~/.pyliftover")
UCSC_LINK_TEMPLATE = 'http://hgdownload.cse.ucsc.edu/goldenPath/{0}/liftOver/{1}.gz'


class LiftOver:
    """
    The class, which loads and indexes USCS's .over.chain files.
    
    Specification of the chain format can be found here: http://genome.ucsc.edu/goldenPath/help/chain.html
    """
    
    def __init__ (self, f, reverse = False):
        """
        Reads chain data from the file and initializes an interval index.
        f must be a file object open for reading.
        If any errors are detected, an Exception is thrown.
        """
        self.reverse = reverse
        self.chains = self._load_chains(f, self.reverse)
        self.chain_index = self._index_chains(self.chains)
        
    @staticmethod
    def _load_chains (f, reverse):
        """
        Loads all LiftOverChain objects from a file into an array. Returns the result.
        """
        chains = []
        while True:
            line = f.readline()
            if not line:
                break
            if line.startswith(b'#') or not line.strip():
                # skip comment and empty lines
                continue
            # read chain
            chains.append(LiftOverChain(line, f, reverse))
        return chains

    @staticmethod
    def _index_chains (chains):
        """
        Given a list of LiftOverChain objects, creates a
         dict: source_name --> 
            IntervalTree: <source_from, source_to> -->
                (target_from, target_to, chain)
        Returns the resulting dict.
        Throws an exception on any errors or inconsistencies among chains (e.g. different sizes specified for the same chromosome in various chains).
        """
        chain_index = {}
        source_size = {}
        target_size = {}
        for c in chains:
            # Verify that sizes of chromosomes are consistent over all chains
            source_size.setdefault(c.source_name, c.source_size)
            if source_size[c.source_name] != c.source_size:
                raise FormatParseError(
                    'Chains have inconsistent specification of source '
                    'chromosome size for {0} ({1} vs {2})'
                    .format(
                        c.source_name,
                        source_size[c.source_name],
                        c.source_size
                        )
                    )
            target_size.setdefault(c.target_name, c.target_size)
            if target_size[c.target_name] != c.target_size:
                raise FormatParseError(
                    'Chains have inconsistent specification of target '
                    'chromosome size for {0} ({1} vs {2})'
                    .format(
                        c.target_name,
                        target_size[c.target_name],
                        c.target_size
                        )
                    )
            chain_index.setdefault(c.source_name, IntervalTree(0, c.source_size))
            # Register all blocks from the chain in the corresponding interval tree
            tree = chain_index[c.source_name]
            for (sfrom, sto, tfrom, tto) in c.blocks:
                tree.add_interval(sfrom, sto, (tfrom, tto, c))

        # Sort all interval trees
        for k in chain_index:
            chain_index[k].sort()
        return chain_index

    def query(self, chromosome, position):
        """
        Given a chromosome and position, returns all matching records from the chain index.
        Each record is an interval (source_from, source_to, data)
        where data = (target_from, target_to, chain).
        Note that depending on chain.target_strand, the target values may need
        to be reversed (e.g. pos --> chain.target_size - pos).
        
        If chromosome is not found in the index, None is returned.
        """
        if chromosome not in self.chain_index:
            return None
        else:
            return self.chain_index[chromosome].query(position)

    def convert_coordinate(self, chromosome, position):
        """
        Returns a *list* of possible conversions for a given chromosome position.
        The list may be empty (no conversion), have a single element (unique conversion), or several elements (position mapped to several chains).
        The list contains tuples (target_chromosome, target_position, target_strand, conversion_chain_score),
        where conversion_chain_score is the "alignment score" field specified at the chain used to perform conversion. If there
        are several possible conversions, they are sorted by decreasing conversion_chain_score.
        
        IF chromosome is completely unknown to the LiftOver, None is returned.
        
        Note that coordinates are 0-based, and even at negative strand are relative to the beginning of the genome.
        I.e. position 0 strand + is the first position of the genome. Position 0 strand - is also the first position of the genome
        (and the last position of the reverse-complemented genome).
        """
        query_results = self.query(chromosome, position)
        if query_results is None:
            return None
        else:
            # query_results contain intervals which contain the query point.
            # We simply have to remap to corresponding targets.
            results = []
            for (source_start, source_end, data) in query_results:
                target_start, target_end, chain = data
                result_position = target_start + (position - source_start)
                if chain.target_strand == '-':
                    result_position = chain.target_size - 1 - result_position
                result_strand = chain.target_strand
                results.append((chain.target_name, result_position, result_strand, chain.score))
            if len(results) > 1:
                results.sort(key=lambda x: x[3], reverse=True)
            return results


class LiftOverChain:
    """
    Represents a single chain from an .over.chain file.
    A chain basically maps a set of intervals from "source" coordinates to corresponding coordinates in "target" coordinates.
    The "source" and "target" are somehow referred to in the specs (http://genome.ucsc.edu/goldenPath/help/chain.html)
    as "target" and "query" respectively.
    """
    def __init__ (self, header, f, reverse = False):
        """
        Reads the chain from a stream given the first line and a file opened at all remaining lines.
        On error throws an exception.
        """

        # The header line is the only thing in a chain that we need to decode
        # because the rest is just encoding integers that int() can give us
        # directly.
        try:
            header = header.decode(DEFAULTENCODING)
        except UnicodeDecodeError:
            header = header.decode(FALLBACKENCODING)
        # example header line:
        # chain 4900 chrY 58368225 + 25985403 25985638 chr5 151006098 - 43257292 43257528 1
        fields = header.split()
        if fields[0] != 'chain' and len(fields) not in [12, 13]:
            raise FormatParseError(
                'Invalid chain format. ({0})'.format(header)
                )

        if not reverse:
            self.score = int(fields[1])        # Alignment score
            self.source_name = fields[2]       # E.g. chrY
            self.source_size = int(fields[3])  # Full length of the chromosome
            self.source_strand = fields[4]     # Must be +
            if self.source_strand != '+':
                raise FormatParseError(
                    'Source strand in an .over.chain file must be "+". ({0})'
                    .format(header)
                    )
            self.source_start = int(fields[5]) # Start of source region
            self.source_end = int(fields[6])   # End of source region
            self.target_name = fields[7]       # E.g. chr5
            self.target_size = int(fields[8])  # Full length of the chromosome
            self.target_strand = fields[9]     # + or -
            if self.target_strand not in ['+', '-']:
                raise FormatParseError(
                    'Target strand must be "-" or "+". ({0})'
                    .format(header)
                    )
            self.target_start = int(fields[10])
            self.target_end = int(fields[11])
            self.id = None if len(fields) == 12 else fields[12].strip()
                        
            # Now read the alignment chain from the file and store it as a list (source_from, source_to) -> (target_from, target_to)
            sfrom, tfrom = self.source_start, self.target_start
            self.blocks = []
            fields = f.readline().split()
            while len(fields) == 3:
                size, sgap, tgap = int(fields[0]), int(fields[1]), int(fields[2])
                self.blocks.append((sfrom, sfrom+size, tfrom, tfrom+size))
                sfrom += size + sgap
                tfrom += size + tgap
                fields = f.readline().split()
            if len(fields) != 1:
                raise FormatParseError(
                    'Expecting one number on the last line of alignments '
                    'block. ({0})'
                    .format(header)
                    )
            size = int(fields[0])
            self.blocks.append((sfrom, sfrom+size, tfrom, tfrom+size))
            if (sfrom + size) != self.source_end  or (tfrom + size) != self.target_end:
                raise FormatParseError(
                    'Alignment blocks do not match specified block sizes. '
                    '({0})'.format(header)
                    )
        else:
            self.score = int(fields[1])        # Alignment score
            self.target_name = fields[2]       # E.g. chr5
            self.target_size = int(fields[3])  # Full length of the chromosome
            self.target_strand = fields[4]     # Must be +
            if self.target_strand != '+':
                raise FormatParseError(
                    'Source strand in an .over.chain file must be "+". ({0})'
                    .format(header)
                    )
            self.target_start = int(fields[5])
            self.target_end = int(fields[6])
            self.source_name = fields[7]       # E.g. chrY
            self.source_size = int(fields[8])  # Full length of the chromosome
            self.source_strand = fields[9]     # + or -
            self.source_start = int(fields[10]) # Start of source region
            self.source_end = int(fields[11])   # End of source region
            if self.source_strand not in ['+', '-']:
                raise FormatParseError(
                    'Target strand must be "-" or "+". ({0})'
                    .format(header)
                    )
            self.id = None if len(fields) == 12 else fields[12].strip()    

            # see if we need to reorient the strands
            if self.source_strand == '-':
                # source strand is required to have '+' orientation
               	self.source_strand = '+'
               	# target_strand has to be '+' at this time so change it to '-'
               	self.target_strand = '-'
               	self.source_start, self.source_end = (
                    self.source_size - self.source_end,
                    self.source_size - self.source_start
                    )
               	self.target_start, self.target_end = (
                    self.target_size - self.target_end,
                    self.target_size - self.target_start
                    )

            # Now read the alignment chain from the file and store it as
            # tuples of (source_from, source_to) -> (target_from, target_to)
            sfrom, tfrom = self.source_start, self.target_start
            self.blocks = []
            fields = f.readline().split()
            while len(fields) == 3:
                size, sgap, tgap = int(fields[0]), int(fields[2]), int(fields[1])
                self.blocks.append((sfrom, sfrom+size, tfrom, tfrom+size))
                sfrom += size + sgap
                tfrom += size + tgap
                fields = f.readline().split()
            if len(fields) != 1:
                raise FormatParseError(
                    'Expecting one number on the last line of alignments '
                    'block. ({0})'
                    .format(header)
                    )
            size = int(fields[0])
            self.blocks.append((sfrom, sfrom+size, tfrom, tfrom+size))


def chain_file_from_versions (from_db, to_db):
    to_db = to_db[0].upper() + to_db[1:]
    return '{0}To{1}.over.chain'.format(from_db, to_db)


def versions_from_chain_file (fn):
    a_to_b = os.path.basename(fn).split('.')[0]
    a, b = a_to_b.split('To')
    return a, b[0].lower() + b[1:]

    
def find_chain_file (fn):
    fn_gz = fn + '.gz'
    if os.path.isfile(fn):
        return fn
    elif os.path.isfile(fn_gz):
        return fn_gz
    else:
        return None


class NamedTemporaryChainFile ():
    def __init__ (self, from_db, to_db = None):
        if to_db:
            fn = chain_file_from_versions(from_db, to_db)
        else:
            fn = from_db
            from_db, to_db = versions_from_chain_file(fn)
        self.remote = UCSC_LINK_TEMPLATE.format(from_db, fn)
        self.local = tmpfiles.NamedTemporaryMiModDFile(suffix='.chain.gz')
        try:
            # Download file content from UCSC.
            req = urllib.request.Request(self.remote)
            with urllib.request.urlopen(req) as remote:
                shutil.copyfileobj(remote, self.local)
            self.remote_exists = True
            self.local.seek(0)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                self.remote_exists = False
            else:
                raise
        except:
            self.local.close()
            raise

    def __enter__ (self):
        return self

    def __exit__ (self, *error_desc):
        self.local.close()
        

def load (from_db, to_db=None, search_dir='.', cache_dir=CACHE_DIR,
          use_web=False, reverse=False):
    """Generate a LiftOver from a file obtained and opened in a "smart" way.

    Test providing filename:
    >>> lo = load('tests/data/mds42.to.mg1655.liftOver')
    >>> lo.convert_coordinate('AP012306.1', 16000)
    [('Chromosome', 21175, '+', 378954552...)]

    Test providing from_db and to_db:
    >>> lo = load('hg17', 'hg18')
    >>> lo.convert_coordinate('chr1', 1000000)
    [('chr1', 949796, '+', 21057807908...)]
    >>> lo.convert_coordinate('chr1', 0)
    [('chr1', 0, '+', 21057807908...)]
    >>> lo.convert_coordinate('chr1', 0, '-')
    [('chr1', 0, '-', 21057807908...)]
    >>> lo.convert_coordinate('chr1', 103786442)
    [('chr20', 20668001, '-', 14732...)]
    >>> lo.convert_coordinate('chr1', 103786443, '-')
    [('chr20', 20668000, '+', 14732...)]
    >>> lo.convert_coordinate('chr1', 103786441, '+')
    []
    """

    # A "smart" way of obtaining liftover chain files.
    # By default acts as follows:
    #  1. If the file ``<from_db>To<to_db>.over.chain.gz`` exists in
    #  <search_dir>, opens it for reading via gzip.open.
    #  2. Otherwise, if the file ``<from_db>To<to_db>.over.chain`` exists
    #     in the <search_dir> opens it (as uncompressed file).
    #     Steps 1 and 2 may be disabled if search_dir is set to None.
    #  3. Otherwise, checks whether ``<cache_dir>/<from_db>To<to_db>.over.chain.gz`` exists.
    #     This step may be disabled by specifying cache_dir = None.
    #  4. If file still not found attempts to download the file from UCSC
    #     to a temporary location.
    #     This step may be disabled by specifying use_web=False. In this
    #     case the operation fails and the function returns None.
    #  5. At this point, if write_cache=True and cache_dir is not None
    #     and writable, the file is copied to cache_dir and opened from
    #     there. Otherwise it is opened from the temporary location.
    # In case of errors (e.g. URL cannot be opened), None is returned.

    if to_db:
        # Assume a from_db and to_db string have been provided and
        # try to locate the corresponding chain file.
        basename = chain_file_from_versions(from_db, to_db)
        chain_file = None
        if search_dir is not None:
            chain_file = find_chain_file(
                os.path.join(search_dir, basename)
                )
        if not chain_file and cache_dir is not None:
            chain_file = find_chain_file(
                os.path.join(cache_dir, basename)
                )
    else:
        # The chain file name itself has been provided.
        chain_file = from_db

    if chain_file:
        # We've found a chain file, either because its name was provided
        # directly or because we discovered one from genome versions.
        # Now lets see if we need to open the file using gzip or or
        # built-in open
        # We try gzip.open first and if that fails - possibly because
        # the file is not a gzipped file after all - retry with
        # built-in open
        with gzip.open(chain_file, 'rb') as f:
            try:
                return LiftOver(f, reverse)
            except OSError:
                pass
        with open(chain_file, 'rb') as f:
            return LiftOver(f, reverse)
    elif use_web:
        with NamedTemporaryChainFile(basename) as f:
            if not f.remote_exists:
                raise ArgumentValidationError(
                    'No remote chain file could be found for '
                    'remapping between genome versions "{0}" and '
                    '"{1}" at {2}.'
                    .format(from_db, to_db, f.remote)
                    )
            lo = LiftOver(
                gzip.GzipFile(fileobj=f.local),
                reverse
                )
            # At this point, we verified that the downloaded data could
            # be parsed into a LiftOver object so it's worthwhile
            # consider caching it
            if cache_dir is not None:
                dest = os.path.join(cache_dir, basename + '.gz')
                try:
                    try:
                        os.mkdir(cache_dir)
                    except FileExistsError:
                        pass
                    with open(dest, 'wb') as o:
                        # rewind the temporary file which we read over
                        # once before
                        f.local.seek(0)
                        shutil.copyfileobj(f.local, o)
                except OSError:
                    try:
                        os.remove(dest)
                    except:
                        pass
            return lo
    else:
        # If we reach this point then the from_db and to_db were both
        # provided, could not be found locally (looking in search_dir and
        # possibly cache_dir) and remote lookup was disabled.
        raise ArgumentValidationError(
            'No UCSC chain file could be found on your system for '
            'remapping between genome versions "{0}" and "{1}".'
            .format(from_db, to_db)
            )
