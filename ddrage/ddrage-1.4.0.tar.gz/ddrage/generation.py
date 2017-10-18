# -*- coding: utf-8 -*-
"""
This module contains all functions that handle 
- (base) sequence generation,
- quality score generation.

"""
import os
import sys
import numpy as np
from numba import njit, int64, float64
import dinopy as dp

BASES = np.array([65, 67, 71, 84], dtype=np.uint8)

def random_seq(length, p=None, excluded_motif=None,
      _BASES=BASES, _choice=np.random.choice):
    """
    Create a random sequence of given length from ACGT with given probabilities p.
    Use p=None for the uniform distribution.
    Use a single float (e.g. 0.5) to specify a GC-content (0.5 is equivalent to uniform).
    Use a numpy float64 array of length 4 to specify an arbitrary distribution.

    Optionally, ensure that the sequence does not contain a given excluded motif.
    Specify excluded_motif=None (default) if no motif exclusion is desired.
    NOTE: Specifying a short (frequent) motif for exclusion may lead to long running times!

    Return a bytes object with the nucleotide sequence (from b'ACGT')
    that does not contain the excluded motif.
    """
    if isinstance(p, float): 
        p = get_p_from_gc_content(p)
    # now p is either None or an np.ndarray of size 4
    seq = _choice(_BASES, length, p=p).tobytes()
    if excluded_motif is None:
        return seq
    motiflength = len(excluded_motif)
    while True:
        if excluded_motif not in seq:
            return seq
        newpart = _choice(_BASES, motiflength, p=p).tobytes()
        seq = seq.replace(excluded_motif, newpart)


def random_fragment(length, p=None, excluded_motifs=None,
      _BASES=BASES, _choice=np.random.choice):
    """
    """
    if isinstance(p, float): 
        p = get_p_from_gc_content(p)
    # now p is either None or an np.ndarray of size 4
    seq = _choice(_BASES, length, p=p).tobytes()
    
    if excluded_motifs is None:
        return seq

    m1, m2, m3, m4 = excluded_motifs
    l_m1, l_m2, l_m3, l_m4 = [len(m) for m in (m1, m2, m3, m4)]
    while True:
        if m1 in seq:
            newpart = _choice(_BASES, l_m1, p=p).tobytes()
            seq = seq.replace(m1, newpart)
        elif m2 in seq:
            newpart = _choice(_BASES, l_m2, p=p).tobytes()
            seq = seq.replace(m2, newpart)
        elif m3 in seq:
            newpart = _choice(_BASES, l_m3, p=p).tobytes()
            seq = seq.replace(m3, newpart)
        elif m4 in seq:
            newpart = _choice(_BASES, l_m4, p=p).tobytes()
            seq = seq.replace(m4, newpart)
        else:
            return seq


def p5_seq_from_fragment(length, fragment):
    """Get first length bases from the fragment."""
    return fragment[:length]


def rev_comp(seq):
    """Compute reverse complement of a sequence."""
    comp = {
        65: 84,
        84: 65,
        67: 71,
        71: 67,
        78: 78,
        }
    return bytes(reversed([comp[base] for base in seq]))

def p7_seq_from_fragment(length, fragment):
    """Get reverse complement of the last length bases of the fragment."""
    return rev_comp(fragment[-length:])


class FragmentGenerator:
    def __init__(self, args):
        # check if loci points to a 
        path = args.loci
        if isinstance(path, str) and os.path.exists(path):
            self.from_file = True
            self.fragment_file = dp.FastaReader(path).entries()
            self.min_length = args.read_length
            # self.get_fragment = self.read_fragment_from_file
        else:
            self.from_file = False
            self.fragment_file = None
            # self.get_fragment = self.random_fragment
        self.p = args.gc_content
        self.excluded_motifs = (args.p5_rec_site, args.p7_rec_site,
                                dp.reverse_complement(args.p5_rec_site),
                                dp.reverse_complement(args.p7_rec_site),
                                )

    def read_fragment_from_file(self):
        fragment = self.fragment_file.__next__()
        while fragment.length < self.min_length:
            print("Fragment '{}' too short to produce reads. Skipped.".format(fragment.name.decode()), file=sys.stderr)
            fragment = self.fragment_file.__next__()
        return fragment.sequence, fragment.name

    def random_fragment(self, length):
        return random_fragment(length, self.p, self.excluded_motifs)


def get_p_from_gc_content(gc_content):
    """
    return None if p=0.5, 
    or otherwise an np.array with four probabilities for ACGT
    """
    if gc_content == 0.5:
        p = None  # optimize uniform case
    else:
        pcg = gc_content / 2.0
        pat = 0.5 - pcg
        p = np.array([pat, pcg, pcg, pat], dtype=np.double)
    return p





class QualityModel:

    def __init__(self, path, read_length):
        """
        read model from given path on disk,
        this should be a text file with matrix of size `|qualityvalues| x 100`
        containing one quality distribution per column,
        i.e., column j corresponds to read position j.
        """
        # initialize quality_profile by reading it from disk;
        # Adjust it later to a matrix of dimensions readlength x |qualityvalues|,
        # such that row i contains quality distribution at read position i.
        self.path = path
        profile = np.load(path)
        profile_p5 = profile["p5"].T
        profile_p7 = profile["p7"].T
        
        self.cumprofile_p5 = self.compute_cumulative_profile(profile_p5, read_length)
        self.cumprofile_p7 = self.compute_cumulative_profile(profile_p7, read_length)
        # prepare quality values to choose from: 33, 34, ...
        # this is an implicit PHRED -> Sanger conversion
        assert(len(profile_p5[0] == len(profile_p7[0])))
        qnumber = len(profile_p5[0])
        self.values_p5 = np.arange(33, 33+qnumber, dtype=np.int8)
        self.values_p7 = np.arange(33, 33+qnumber, dtype=np.int8)


    def compute_cumulative_profile(self, profile, read_length):
        # find the first row that does not sum to 1;
        # the row before is the last valid probability vector!
        plength = len(profile)
        for pos, probs in enumerate(profile):
            if not np.isclose(np.sum(probs), 1.0):
                plength = pos
                break
        # store the last valid row (if it exists)
        if plength == 0:
            raise RuntimeError("ERROR: quality model '{}' doesn't contain probabilities in first column".format(self.path))
        profile = profile[:plength,:]
        if plength > read_length:
            # trim model down to read length
            profile = profile[:read_length,:]
        elif plength < read_length:
            # fill missing positions with last model
            last = profile[plength-1,:]
            profile = np.vstack( (profile, np.tile(last, (read_length-plength, 1))) )
        assert profile.shape[0] == read_length, (profile.shape[0], read_length)
        return np.cumsum(profile, axis=1)

    def get_quality_values(self, read):
        """return bytes with printable quality values"""

        plength = self.cumprofile_p5.shape[0]  # same length for p5 and p7 are asserted in constructor
        u = np.random.rand(plength)  # random numbers
        qualities = np.zeros(plength, dtype=np.uint8)
        if read == "p5":
            _find_quality_values(u, self.cumprofile_p5, self.values_p5, qualities)
        else:
            _find_quality_values(u, self.cumprofile_p7, self.values_p7, qualities)

        return qualities.tobytes()            


@njit(locals=dict(m=int64, n=int64, pos=int64, q=int64, x=float64))
def _find_quality_values(u, cumprofile, values, outbuffer):
    m = len(u)
    n = len(values)
    for pos in range(m):
        x = u[pos]
        for q in range(n):
            if cumprofile[pos,q] >= x:
                break
        outbuffer[pos] = values[q]


# global interface to quality generation
def initialize_quality_model(path, read_length):
    global _QUALITY_MODEL
    if os.path.exists(path):
        _QUALITY_MODEL = QualityModel(path, read_length)
    elif path in ("L100-Q70-A", "L100-Q70-B", "L126-Q70", "L150-Q70"):
        quality_model_path = os.path.join(os.path.dirname(__file__), "quality_profiles")
        _QUALITY_MODEL = QualityModel(os.path.join(quality_model_path, "{}.qmodel.npz".format(path)), read_length)
    else:
        raise ValueError("Invalid quality model. The quality model has to be either a predefined model ('L100-Q70', 'L101-Q70', 'L110-Q70') or a path to a .qmodel file.")

def generate_qualities(read):
    return _QUALITY_MODEL.get_quality_values(read)


def count_fragments(fa_path):
    """Count the number of entries in a fasta file
    """
    fragments = 0
    with open(fa_path, "rb") as fa_file:
        for l in fa_file.readlines():
            if l[0] == 62:
                fragments += 1
    return fragments
