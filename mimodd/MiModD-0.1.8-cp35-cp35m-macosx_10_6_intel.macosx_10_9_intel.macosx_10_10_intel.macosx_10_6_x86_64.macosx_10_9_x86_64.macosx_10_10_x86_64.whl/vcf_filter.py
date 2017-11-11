import sys
from . import pyvcf
from . import encoding_base
from . import ArgumentParseError, ArgumentValidationError


SNP_TYPE = 1
INDEL_TYPE = 2


def filter(ifile, ofile = None, type_filter = None, region_filter = None,
           v_filter = None, **h_filter_args):
    """Filter the records in a vcf file by various criteria.

    Write out the records that pass all filter criteria."""
    
    h_filters = generate_hfilter_dict(**h_filter_args)
    if region_filter:
        region_filter = generate_region_filter_dict(region_filter)
    
    if ifile is not None:
        in_vcf = pyvcf.open(ifile, 'r')
    else:
        # read stdin with the pyvcf default encoding,
        # handle decoding errors according to config settings
        in_vcf = pyvcf.VCFReader(encoding_base.get_custom_std(
                                     sys.stdin,
                                     encoding=pyvcf.defaultencoding,
                                     errors=pyvcf.handle_decoding_errors)
                                 )
    if ofile:
        out_vcf = open(ofile, 'w', encoding=pyvcf.defaultencoding)
    else:
        out_vcf = encoding_base.get_custom_std(sys.stdout,
                                               encoding=pyvcf.defaultencoding)

    try:
        rec_iterator = get_filtered_record_iterator(in_vcf,
                                                    gts=h_filters,
                                                    samples=v_filter,
                                                    regions=region_filter,
                                                    types=type_filter)
        # write metadata
        if v_filter:
            out_vcf.write(str(in_vcf.info.sample_slice(v_filter)))
        else:
            out_vcf.write(str(in_vcf.info))
        out_vcf.write('\n')
        # process the vcf file entries
        for rec in rec_iterator:
            out_vcf.write(str(rec))
            out_vcf.write('\n')
    finally:
        if out_vcf is not sys.stdout:
            try:
                out_vcf.close()
            except:
                pass
        if in_vcf is not sys.stdin:
            try:
                in_vcf.close()
            except:
                pass


def get_filtered_record_iterator (in_vcf, gts, samples, regions, types):
    # set up filters for variant types and chromosomes
    if not types:
        rec_iterator = in_vcf.filter(gts, samples)
    elif types == INDEL_TYPE:
        rec_iterator = (rec for rec in in_vcf.filter(gts, samples) if 'INDEL' in rec.info)
    elif types == SNP_TYPE:
        rec_iterator = (rec for rec in in_vcf.filter(gts, samples) if 'INDEL' not in rec.info)
    else:
        raise ValueError ('Unrecognized variant type filter {0}'.format(types))
    if regions:
        rec_iterator = (rec for rec in rec_iterator
                        if rec.chrom in regions and
                        any(interval[0] <= rec.pos <= interval[1] for interval in regions[rec.chrom]))
    return rec_iterator


def generate_hfilter_dict (samples = (), gt = (), dp = (), gq = (), af = ()):
    # parameter sanity checks
    sample_no = len(samples)
    if gt == ():
        gt = ('ANY',) * sample_no
    if af == ():
        af = ('::',) * sample_no
    if dp == ():
        dp = (0,) * sample_no
    if gq == ():
        gq = (0,) * sample_no
    if not all(len(param) == len(samples) for param in (gt, dp, gq, af)):
        raise ArgumentValidationError('The number of samples must match the number of genotype filters.')
    # prepare filter dictionary    
    filters = {sample: {'GT': [g.strip() for g in _gt.split(',')],
                        'DP': _dp,
                        'GQ': _gq,
                        'DPR': get_allele_fraction_tuple(_af)}
               for sample, _gt, _dp, _gq, _af in zip(samples, gt, dp, gq, af)}
    # remove wildcards from filters dict
    for f in filters.values():
        if 'ANY' in f['GT']:
            if len(f['GT'])>1:
                raise ArgumentValidationError('If "ANY" is used as a genotype filter, it has to be the only argument')
            else:
                del f['GT']
        if f['DP'] == 0:
            del f['DP']
        if f['GQ'] == 0:
            del f['GQ']
        if f['DPR'] == ():
            del f['DPR']
    return filters


def generate_region_filter_dict (region_strings):
    """Parse a sequence of region strings into a chromosome-based dictionary."""

    region_dict ={}
    for r in region_strings:
        chrom, start, stop = get_region_tuple(r)
        if chrom not in region_dict:
            region_dict[chrom] = [(start, stop)]
        else:
            region_dict[chrom].append((start, stop))
    return region_dict


def get_region_tuple (region_string):
    """Parse a region string.

    Returns a tuple of chromosome, start and end position."""
    
    try:
        chrom, posinfo = region_string.rsplit(':', 1)
    except ValueError:
        raise ArgumentParseError(
            'Expected colon (only) after chromosome identifier. Region filters must be specified in the format CHROM:[[START]-[STOP]]')
    if not chrom:
        raise ArgumentParseError(
            'A chromosome identifier is required. Specify region filters in the format CHROM:[[START]-[STOP]]')
    if not posinfo:
        # filter specifies a whole chromosome
        return region_string[:-1], 0, float('inf')
    try:
        start, stop = posinfo.split('-')
    except ValueError:
        raise ArgumentParseError(
            'Expected exactly one minus in interval specification. Region filters must be specified in the format CHROM:[[START]-[STOP]]')
    try:
        start = int(start or 0)
        if stop == '':
            stop = float('inf')
        else:
            stop = int(stop)
    except ValueError:
        raise ArgumentParseError(
            'Region filter start and stop positions must be integral numbers and be specified in the format [START]-[STOP]. Got {0}-{1} instead',
            start, stop)
    if start > stop:
        raise ArgumentValidationError(
            '{0} > {1}. The left end of a region filter chromosomal interval cannot be greater than the right end.',
            start, stop)
    return chrom, start, stop


def get_allele_fraction_tuple (af_string):
    """Parse an allele fraction string.

    Returns a tuple of allele number, miminal fraction, maximal fraction."""
    
    try:
        allele_no, fmin, fmax = af_string.split(':', 2)
    except ValueError:
        raise ArgumentParseError(
            'Expected allele fraction filter with elements separated by colons. General format: [allele number]:[minimal fraction]:[maximal fraction]')
    try:
        allele_no = int(allele_no or -1)
    except ValueError:
        raise ArgumentParseError(
            'The first element of an allele fraction filter must be an integral allele number, not "{0}".',
            allele_no)
    try:
        fmin, fmax = float(fmin or 0), float(fmax or 1)
    except ValueError:
        raise ArgumentParseError(
            'The second and third element of an allele fraction filter must be numbers between 0 and 1, got "{0}" and "{1}" instead',
            fmin, fmax)
    if fmin <= 0 and fmax >= 1:
        # fmin and/or fmax have not been specified
        # or were explicitly passed with ineffectively low or high values
        # => we speed up filtering by omitting the ineffective filter
        return tuple()
    if fmin > fmax:
        raise ArgumentValidationError(
            '{0} > {1}. The second value of an allele fraction filter cannot be greater than the third element.',
            fmin, fmax)
    return allele_no, fmin, fmax
