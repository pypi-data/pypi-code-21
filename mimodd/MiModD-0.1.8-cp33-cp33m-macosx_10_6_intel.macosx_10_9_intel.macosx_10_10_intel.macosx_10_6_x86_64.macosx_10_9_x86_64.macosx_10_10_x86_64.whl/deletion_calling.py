import sys
import os
import signal
import itertools
import random

from math import log10

from . import encoding_base
from . import tmpfiles, index, samheader, pysamtools, pysam, pyvcf
from . import MetadataIncompatibilityError

from .encoding_base import DEFAULTENCODING
from .stats_base import fisher as fisher_exact
from .bioobj_base import Chromosome, Deletion


threshold = 0.01
            
def get_default_rgs (headers):
    # for each header, if it defines just one single read group, record its ID or
    # otherwise store False
    return [header['RG'][0]['ID'] if len(header['RG']) == 1 else False for header in headers]


@tmpfiles.allow_cleanup_on_sigterm
def delcall (ibams, icov, index_files = None, ofile = None, max_cov = None, min_size = None, window = 100,
             include_uncovered = False, group_by_id = False, verbose = False):
    """Calls deletions in paired-end NGS data based on coverage and insert sizes.

    Uses find_lowcov_regions() to identify candidate regions based on low coverage, then
    calls del_stats() to compute significance scores for potential deletions
    based on the insert size distributions around the candidate region and
    elsewhere in the genome. It uses sample_insert_sizes() to obtain an
    estimate of the insert size distributions across the genome."""

    original_bams, ibams = ibams, []
    try:
        # open the coverage file and retrieve the sample information
        coverage = pyvcf.open (icov, 'rb')
        samples = set(coverage.info.samples)
        
        headers = []
        for ibam in original_bams:
            try:
                headers.append(samheader.Header.frombam(ibam))
            except RuntimeError:
                raise RuntimeError(
                    'Aligned reads input file {0} does not seem to be a BAM file'
                    .format(ibam))
        chrm_lengths = {sq['SN']: sq['LN'] for hdr in headers for sq in hdr['SQ']}
        # compare chrm dicts from coverage and bam files
        if chrm_lengths != {contig: info['length'] for contig, info in coverage.info.meta['contig'].items()}:
            raise MetadataIncompatibilityError(
                'Non-matching contig information in the input files.\n' +
                'Are you sure the aligned reads and the variant call file come from the same analysis?'
                )
        # get the read groups of all input files as a flat object
        # using set here ensures that if data for one read group is
        # spread over several input files, that read group won't be used twice
        all_read_groups = [rg for hdr in headers for rg in hdr['RG']]
  
        # check bam RGs and bcf header line to see if we have matching sample names
        # if not, try if we can make them match by appending _<RGID> to the
        # sample names in the bam file (this would indicate that the bam file names
        # were made unique by varcall before SNP calling
        for n in range(2):
            rgid_sm_mapping = {}
            for sample in samples:
                # this loop builds the matching_read_groups list
                matches = {rg['ID']:rg['SM'] for rg in all_read_groups if rg['SM'] == sample}
                if not matches:
                    rgid_sm_mapping = {}
                    break
                if len(matches) > 1 and group_by_id:
                    # the sample name from the bcf file had several matches in the bam file(s)
                    # this is dealt with if deletions are to be called by sample name,
                    # but is inacceptable for calling them by read group id
                    raise RuntimeError('Ambiguous mapping of the sample names between the coverage and the bam input files.')
                rgid_sm_mapping.update(matches)
            if rgid_sm_mapping:
                # we're ok, proceed
                break
            elif n == 0:
                # some samples could not be found in the bam file headers
                # lets extend the header SM tags with the ID tag information
                # then check again
                for hdr in headers:
                    hdr.uniquify_sm()
                all_read_groups = [rg for hdr in headers for rg in hdr['RG']] # recalculate all_read_groups
        else:
            # neither the original headers nor the extended ones gave us a
            # successful mapping of all bcf file sample names
            print('Matching sample names between bam file and coverage file:', file = sys.stderr)
            print(', '.join([sm for sm in samples & {rg['SM'] for rg in all_read_groups}] or ['---']), file = sys.stderr)
            print('sample names found ONLY in coverage file:', file = sys.stderr)
            print(', '.join([sm for sm in samples - {rg['SM'] for rg in all_read_groups}]), file = sys.stderr)
            raise RuntimeError ('Some samples in the coverage file could not be matched to entries in the bam file.')


        # start indexing the input bam files
        ibams = [tmpfiles.tmp_hardlink(ibam, 'tmp_indexed_bam', '.bam') for ibam in original_bams]
        for ibam, index_file in index.validate_index_files(ibams,
                                                           index_files,
                                                           'bai'):
            if index_file:
                index.clone_index(ibam, index_file, 'bai')
            else:
                call, results, errors = pysamtools.index(ibam)
                if errors:
                    raise RuntimeError(
                        'The following error message was raised by '
                        'samtools index: {0}'.format(errors)
                        )


        # estimate the insert size distribution in the input bam
        sizes = sample_insert_sizes (ibams, rgid_sm_mapping)

        bam_input = [pysam.Samfile(ibam, 'rb') for ibam in ibams]
        default_rgs = get_default_rgs(headers)

        if ofile:
            outdel = open(ofile, 'w', encoding=DEFAULTENCODING)
        else:
            outdel = encoding_base.get_custom_std(sys.stdout)

        if verbose:
            print('Starting prediction for the following samples')
            print(', '.join(coverage.info.samples))
            uncallable_samples = {rg:sm for rg,sm in rgid_sm_mapping.items() if not sizes[rg]}
            if uncallable_samples:
                print('The following samples have been excluded from deletion calling (only Uncovered Regions will be reported for them):')
                print(','.join(['{0} [RG_ID:{1}]'.format(sm, rg) for sm,rg in uncallable_samples.items()]))
                
        last_start = 0
        for sample, deletion in find_lowcov_regions(coverage, max_cov, min_size):
            affected_rgs = [rgid for rgid, sm in rgid_sm_mapping.items() if sm == sample]
            if deletion.start-window <= 0 or deletion.stop == chrm_lengths[deletion.chromosome]:
                for rg in affected_rgs:
                    p_value = float('Nan')
                    outdel.write(write_region(deletion, p_value, sample, rg if len(affected_rgs) > 1 else None, include_uncovered))
            else:
                if deletion.start != last_start:
                    # get all reads within the interval defined by window
                    # upstream of the deletion and
                    # store them in a dictionary based on the read group
                    # they belong to
                    nearby_reads = {rgid: [] for rgid in rgid_sm_mapping}
                    for default_rg, inbam in zip(default_rgs, bam_input):
                        for read in inbam.fetch(deletion.chromosome,
                                                deletion.start-window,
                                                deletion.start):
                            if (read.flag & 0x905 == 1) and read.mapq > 0:
                                # this is a primary alignment of a mapped read
                                # from a multi-segment template (i.e. not a
                                # single-end read) and there is some chance
                                # that the alignment is correct
                                nearby_reads[default_rg or dict(read.tags)['RG']].append(read)
                # for every read group affected by the deletion
                # retrieve all associated nearby reads from
                # the dictionary and compute stats from them
                for rg in affected_rgs:
                    if not sizes[rg]:
                        p_value = float('Nan')
                    else:
                        p_value = del_stats(deletion,
                                            nearby_reads[rg],
                                            sizes[rg])
                    outdel.write(write_region(deletion, p_value, sample, rg if len(affected_rgs) > 1 else None, include_uncovered))
                    last_start = deletion.start
                
    finally:
        try:
            coverage.close()
        except:
            pass
        if locals().get('bam_input'):
            for inbam in bam_input:
                try:
                    inbam.close()
                except:
                    pass
        try:
            if outdel is not sys.stdout:
                outdel.close()
        except:
            pass
        for ibam in ibams:
            try:
                os.remove(ibam)
            except:
                pass
            try:
                os.remove(ibam + '.bai')
            except:
                pass


def find_lowcov_regions(coviter, max_cov = None, min_size = None):
    if not max_cov:
        max_cov = 0
    if not min_size:
        min_size=100
    contig_lengths = {contig: info['length']
                      for contig, info in coviter.info.meta['contig'].items()}
    regions_pending = [[None, 1, sample] for sample in coviter.info.samples]
    for cov_info in coviter.field_iter('DP'):
        for region, coverage in zip(regions_pending, cov_info[2]):
            if region[0] != cov_info[0]:
                if region[0] and min_size <= contig_lengths[region[0]] - region[1]:
                    yield region[2], Deletion(region[0], region[1], contig_lengths[region[0]])
                region[0] = cov_info[0]
                region[1] = 1                    
            if int(coverage) > max_cov:
                current_pos = int(cov_info[1])
                if min_size <= current_pos - region[1]:
                    yield region[2], Deletion(region[0], region[1], current_pos - 1)
                region[1] = current_pos + 1
    # done, but need to process pending deletions
    for region in regions_pending:
        if region[0] and min_size <= contig_lengths[region[0]] - region[1]:
            yield region[2], Deletion(region[0], region[1], contig_lengths[region[0]])


def sample_insert_sizes (ibams, rgid_sm_mapping, sampling_depth = 100):
    headers = []
    for ibam in ibams:
        headers.append(samheader.Header.frombam(ibam))
    # merge header SQ information into a list of Chromosome instances
    # to do: move the merging part to samheader module (merge function or method)
    # to do: the code below could be more elegant if bioobj_base.Chromosome
    # instances were hashable
    # Note: it is important that the order of the chromosomes is reproducible
    # or the random.seed call below is pointless
    chrms = []
    chrms_seen = set()
    for hdr in headers:
        for sq in hdr['SQ']:
            if sq['SN'] not in chrms_seen:
                chrms_seen.add(sq['SN'])
                chrms.append(Chromosome(sq['SN'], sq['LN']))
    # ensure constant results for same set of bam input files
    random.seed(sum(ord(c) for hdr in headers for c in str(hdr)))
    default_rgs = get_default_rgs(headers)
    try:
        bam_input = [pysam.Samfile(ibam, 'rb') for ibam in ibams]
        sizes = {rg:[] for rg in rgid_sm_mapping}
        
        for chrm in chrms:
            given_up_rgs = set()
            for x in range (sampling_depth):
                samples_to_treat = {rg:sm for rg,sm in rgid_sm_mapping.items() if rg not in given_up_rgs}
                if not samples_to_treat:
                    break
                trials = 0
                # keep repeating sampling for samples for which no appropriate read
                # was found up to 50 trials, then exclude the sample for this chromosome
                for trial in range (500):
                    randpos = chrm.randpos()
                    for default_rg, fetcher in zip(default_rgs,
                                                   (inbam.fetch(chrm.name,
                                                               randpos,
                                                               randpos+1)
                                                    for inbam in bam_input)):
                        for read in fetcher:
                            if not read.flag & 0x904 and read.tlen > 0:
                                # This is a primary alignment of a mapped read.
                                # A positive observed template length ensures
                                # that a mate exists and is mapped to the same
                                # reference and that we are not counting mate
                                # pairs twice (because the mate will have a
                                # negative tlen).
                                # What we are not checking is whether there are
                                # more than two segments in which case our
                                # algorithm may produce buggy results
                                rgid = default_rg or dict(read.tags)['RG']
                                # equally fast, but less readable:
                                # rgid = default_rg or read.tags[[tag[0] for tag in read.tags].index('RG')][1]
                                if rgid in samples_to_treat:
                                    # append the insert size
                                    sizes[rgid].append(read.pnext-read.pos-read.alen)
                                    del samples_to_treat[rgid]
                                    if not samples_to_treat:
                                        break
                    if not samples_to_treat:
                        break
                for rg in samples_to_treat:
                    given_up_rgs.add(rg)
    finally:
        try:
            for inbam in bam_input:
                try:
                    inbam.close()
                except:
                    pass
        except:
            pass

    return sizes

def del_stats (deletion, adjacent_reads, sizes):
    without_mate = with_mate = short_seq = large_seq = 0

    effective_lengths = []
    for read in adjacent_reads:
        if read.tlen >= 0:
            # excluding negative tlens prevents us from including
            # mate pairs in the analysis that lie to the left of
            # the uncovered region
            if read.mate_is_unmapped:
                without_mate += 1
            elif read.tlen > 0 and read.pnext >= deletion.stop:
                # a positive tlen implies the mate aligning
                # to the same reference
                with_mate +=1
            effective_lengths.append(deletion.stop - (read.pos+read.alen+1)) # deletion coordinates are 1-based, but pysam uses 0-based system
    if with_mate + without_mate == 0:
        return float('Nan')
    for length in sizes:
        if length < random.choice(effective_lengths):
            short_seq += 1
        else:
            large_seq += 1
    p_value = fisher_exact(with_mate, without_mate, large_seq, short_seq)
    return p_value

def write_region(deletion, p_value, sample, rg = None, include_uncovered = False):
    if p_value < threshold:
        region_type = 'Deletion'
        try:
            region_score = int(-10*log10(p_value))
        except ValueError:
            assert p_value == 0
            region_score = 9999
    elif include_uncovered:
        region_type = 'Uncovered_Region'
        region_score = '.'
    else:
        return ''
    return '\t'.join([deletion.chromosome, 'MiModD', region_type,
                      str(deletion.start), str(deletion.stop),
                      str(region_score), '.', '.',
                      'sample={0}{1};p_value={2:e}\n'
                      .format(sample,
                              ' [RG_ID:{0}]'.format(rg) if rg else '',
                              p_value)
                     ])

