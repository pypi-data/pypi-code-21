from __future__ import absolute_import
from __future__ import print_function
from builtins import map
import sys
import logging
from argtools import command, argument
from itertools import groupby
from collections import defaultdict
from .. import sh
import vcf
import cyvcf2 as VCF
import numpy as np
import pandas as pd
import pysam
from ..utils import memoize, iter_tabs
from ..io import open


@command.add_sub
@argument('vcf', help='VCF or gzipped VCF')
def vcf_header(args):
    vcffile = '/dev/stdin' if args.vcf == '-' else args.vcf
    with open(vcffile) as fp:
        r = vcf.Reader(fp)
        print ('category', 'id', 'num', 'type', 'desc', sep='\t')
        for (key, rec) in r.filters.items():
            print ('FILTER', rec.id, '', '', rec.desc, sep='\t')

        for (key, rec) in r.infos.items():
            print ('INFO', rec.id, rec.num, rec.type, rec.desc, sep='\t')

        for (key, rec) in r.formats.items():
            print ('FORMAT', rec.id, rec.num, rec.type, rec.desc, sep='\t')

        for (key, rec) in r.alts.items():
            print ('ALT', rec.id, '', '', rec.desc, sep='\t')

        for (key, rec) in r.metadata.items():
            print ('METADATA', key, '', '', rec, sep='\t')


@command.add_sub
@argument('vcf', help='VCF or gzipped VCF')
def vcf_samples(args):
    vcffile = '/dev/stdin' if args.vcf == '-' else args.vcf
    with open(vcffile) as fp:
        r = vcf.Reader(fp)
        for sample in r.samples:
            print (sample, sep='\t')


def _get_sample_flags(reader, args):
    sample_set = set()
    if args.samples:
        sample_set = set(args.samples.split(','))
    if args.samples_file:
        sample_set = set([line.rstrip() for line in open(args.samples_file)])

    if sample_set:
        sample_flags = np.array([s in sample_set for s in reader.header.samples], dtype=bool)
    else:
        sample_flags = np.ones(len(reader.header.samples), dtype=bool)

    return sample_flags


@memoize
def get_gt_hom_idxs(alt_num):
    """
    >>> get_gt_hom_idxs(0)  # 0/0
    [0]
    >>> get_gt_hom_idxs(1)  # 0/0, 0/1, 1/1
    [0, 2]
    >>> get_gt_hom_idxs(2)  # 0/0, 0/1, 1/1, 0/2, 1/2, 2/2
    [0, 2, 5]
    >>> get_gt_hom_idxs(3)
    [0, 2, 5, 9]
    """
    last = -1
    hom_idxs = []
    for a in range(alt_num + 1):
        last = last + (a + 1)
        hom_idxs.append(last)
    return hom_idxs


@memoize
def get_default_gl(alt_num):
    """
    >>> get_default_gl(1)
    '-0.301,0,-0.301'
    >>> get_default_gl(2)
    '-0.301,0,-0.301,0,0,-0.301'
    """
    het_gl = '0'
    hom_gl = '{0:.3f}'.format(- np.log10(2))
    gt_num = (alt_num + 1) * (alt_num + 2) / 2
    gl = [het_gl] * gt_num
    hom_idxs = get_gt_hom_idxs(alt_num)
    for idx in hom_idxs:
        gl[idx] = hom_gl
    return ','.join(gl)


@command.add_sub
@argument('vcf', help='VCF or gzipped VCF')
@argument.exclusive(
    argument('-s', '--samples', help='comma separated sample list'),
    argument('-S', '--samples-file', help='sample list file'),
)
def vcf_reset_gl(args):
    """ whitening format tag for specified samples

    # TODO also reset PL
    """
    vcffile = '/dev/stdin' if args.vcf == '-' else args.vcf
    import pysam
    reader = pysam.VariantFile(vcffile)
    sample_flags = _get_sample_flags(reader, args)
    print (reader.header, end='')
    sample_offset = 9

    # hom: log10 p**2 = 2 log10 p
    # het: log10 2p**2 = 2 log10 p + log10 2

    def replace_fmt(alt_num, gl_index, fmt_info):
        splt = fmt_info.split(':')
        splt[gl_index] = get_default_gl(gt_num)
        return ':'.join(splt)

    for rec in reader:
        srec = str(rec).split('\t')
        fmts = rec.format.keys()
        alt_num = len(rec.alts)
        gl_index = fmts.index('GL')

        fmt_rec = [(replace_fmt(alt_num, gl_index, s) if flg else s) for flg, s in zip(sample_flags, srec[sample_offset:])]
        print (*(srec[:sample_offset] + fmt_rec), sep='\t', end='')


@command.add_sub
@argument('vcf', help='VCF or gzipped VCF')
@argument.exclusive(
    argument('-s', '--samples', help='comma separated sample list'),
    argument('-S', '--samples-file', help='sample list file'),
)
def vcf_untype(args):
    """ whitening format tag for specified samples

    # TODO also reset PL
    """
    vcffile = '/dev/stdin' if args.vcf == '-' else args.vcf
    import pysam
    reader = pysam.VariantFile(vcffile)
    sample_flags = _get_sample_flags(reader, args)
    print (reader.header, end='')
    sample_offset = 9

    import re
    gt_sep = re.compile('/|')
    def replace_fmt(gt_index, fmt_info):
        splt = fmt_info.split(':')
        gt = splt[gt_index]
        ngt = len(gt_sep.split(gt))
        splt[gt_index] = '/'.join(('.',) * ngt)
        return ':'.join(splt)

    for rec in reader:
        srec = str(rec).split('\t')
        fmts = rec.format.keys()
        gt_index = fmts.index('GT')

        fmt_rec = [(replace_fmt(gt_index, s) if flg else s) for flg, s in zip(sample_flags, srec[sample_offset:])]
        print (*(srec[:sample_offset] + fmt_rec), sep='\t', end='')


def _load_pos_sets(poslist):
    chrom_pos_sets = defaultdict(set)
    with open(poslist) as fp:
        for row in iter_tabs(fp):
            chrom = row[0]
            pos = int(row[1])
            chrom_pos_sets[chrom].add(pos)
    return chrom_pos_sets


@command.add_sub
@argument('vcf', help='VCF or gzipped VCF')
@argument('poslist', help='chrom:pos')
@argument('-r', '--region', help='VCF or gzipped VCF')
def vcf_pick(args):
    """ poslist: chrom:pos
    """
    vcffile = '/dev/stdin' if args.vcf == '-' else args.vcf
    import pysam
    reader = pysam.VariantFile(vcffile)

    # iteration
    if args.region:
        it = reader.fetch(region=args.region)
    else:
        it = reader

    logging.info('Loading poslist: %s', args.poslist)
    chrom_pos_sets = _load_pos_sets(args.poslist)
    for chrom in sorted(chrom_pos_sets):
        logging.info('Loaded %s pos from chrom: %s', len(chrom_pos_sets[chrom]), chrom)

    print (reader.header, end='')
    for chrom, recs in groupby(it, lambda x: x.contig):
        pos_sets = chrom_pos_sets[chrom]
        for rec in recs:
            if rec.pos in pos_sets:
                print (str(rec), end='')


@command.add_sub
@argument('vcf', help='VCF or gzipped VCF')
@argument('-r', '--region')
@argument('-c', '--check-variant', action='store_true', help='consider duplicated if check ref and alts are concordant')
def vcf_list_dup(args):
    """
    Emit:
        chrom, pos, id, ref, alt
    """
    vcffile = '/dev/stdin' if args.vcf == '-' else args.vcf
    import pysam
    reader = pysam.VariantFile(vcffile)

    # iteration
    if args.region:
        it = reader.fetch(region=args.region)
    else:
        it = reader

    if args.check_variant:
        def get_id(rec):
            return ':'.join((rec.chrom, str(rec.pos), rec.ref, ','.join(rec.alts)))
    else:
        def get_id(rec):
            return ':'.join((rec.chrom, str(rec.pos)))

    print ('chrom', 'pos', 'id', 'ref', 'alt', sep='\t')
    checked = set()  # pos ':' ref ':' ','.join(alts)
    for chrom, recs in groupby(it, lambda x: x.contig):
        last_pos = 0
        for rec in recs:
            rec_id = get_id(rec)
            if rec_id in checked:
                print (rec.chrom, rec.pos, rec.id, rec.ref, ','.join(rec.alts), sep='\t')
                continue
            checked.add(rec_id)


@memoize
def mendel_check(child, father, mother):
    """
    >>> mendel_check((0, 0), (0, 0), (0, 0))
    True
    >>> mendel_check((0,), (0,), (0, 0))
    True
    >>> mendel_check((1,), (0,), (0, 0))
    False
    >>> mendel_check((1,), (0,), (1, 2))
    True
    >>> mendel_check((2, 0), (0,), (1, 2))
    True
    >>> mendel_check((1, 2), (0,), (1, 2))
    False
    >>> mendel_check((0, 1), (1, 1), (0, 0))
    True
    >>> mendel_check((0, 1), (1, 1), (0, 1))
    True
    >>> mendel_check((1, 1), (1, 1), (0, 1))
    True
    """
    assert len(child) <= 2
    assert len(mother) <= 2
    assert len(father) <= 2
    if len(child) == 0:
        return True
    if len(child) == 1:
        return child[0] in mother or child[0] in father
    # child is diploid
    if child[0] in mother and child[1] in father:
        return True
    if child[0] in father and child[1] in mother:
        return True
    return False


class PedFile(object):
    """
    Family ID
    Individual ID
    Paternal ID
    Maternal ID
    Sex (1=male; 2=female; other=unknown)
    Phenotype ...
    """
    def __init__(self, pedfile):
        columns = ['family', 'sample_id', 'father', 'mother', 'sex']
        self._ped_tab = pd.read_table(pedfile, header=None, sep=' ')
        self._ped_tab.columns = columns + list(self._ped_tab.columns[len(columns):])
        self._recs = {t.sample_id: t for t in self._ped_tab.itertuples()}

    def __len__(self):
        return len(self._ped_tab)

    def get_sex(self, sample):
        return self._recs[sample].sex

    def iter_trios(self):
       """
       Returns (sample_id, father, mother)
       """
       for row in self._ped_tab.itertuples():
           yield (row.sample_id, row.father, row.mother)


@command.add_sub
@argument('vcf', help='VCF or gzipped VCF')
@argument('-p', '--pedigree', help='ped file')
@argument('-r', '--regions', nargs='+')
def vcf_mendel_check(args):
    """
    """
    ped = PedFile(args.pedigree)
    trios = list(ped.iter_trios())

    # VCF
    if args.regions:
        reader = pysam.VariantFile(args.vcf)
        def gen():
            for region in args.regions:
                for rec in reader.fetch(region=region):
                    yield rec
        it = gen()
    else:
        fp = open(args.vcf)
        reader = pysam.VariantFile(fp)
        it = reader

    headers = ['chrom', 'pos', 'end', 'ref', 'alt', 'is_snp', 'al_count', 'ok', 'gt_c', 'gt_f', 'gt_m', 'sex', 'trio']
    print (*headers, sep='\t')
    sample_idxs = {sample: i for i, sample in enumerate(reader.header.samples)}
    sample_set = set(reader.header.samples)
    logging.debug(trios)
    logging.debug(sample_set)
    trio_samples = [trio for trio in trios if all(sid in sample_set for sid in trio)]
    logging.info('Trios in ped: %s (%s)', len(trios), args.pedigree)
    logging.info('Trios in the VCF: %s (%s)', len(trio_samples), args.vcf)

    def check_is_snp(ref, alts):
        return len(ref) == 1 and all(len(alt) == 1 for alt in alts)

    class VCFSampleData(object):
        #logging.info((dir(sample_data),
        #    sample_data['GT'],
        #    str(sample_data['GT']),
        #    str(sample_data),
        #    sample_data.items(),
        #    sample_data.index,
        #    sample_data.alleles,
        #    sample_data.allele_indices,
        #    sample_data.phased))

        def __init__(self, d):
            self._d = d
            self.gt = self._d['GT']

        @property
        def gt_filled(self):
            return tuple('.' if index is None else index for index in self.gt)

        @property
        def gt_str(self):
            sep = '|' if self._d.phased else '/'
            return sep.join('.' if index is None else str(index) for index in self.gt)

    for row in it:
        info = row.info
        ref = row.ref
        alts = row.alts
        end = row.pos + len(ref) - 1
        is_snp = int(check_is_snp(ref, alts))
        al_count = 1 + len(alts)
        for c, f, m in trio_samples:
            sex = ped.get_sex(c)
            c_idx = sample_idxs[c]
            f_idx = sample_idxs[f]
            m_idx = sample_idxs[m]
            #logging.info(dir(row.format['GT']))
            dat_c = VCFSampleData(row.samples[c_idx])
            dat_f = VCFSampleData(row.samples[f_idx])
            dat_m = VCFSampleData(row.samples[m_idx])
            ok = mendel_check(dat_c.gt_filled, dat_f.gt_filled, dat_m.gt_filled)
            print (row.chrom,
                    row.pos,
                    info.get('END', end),
                    ref,
                    ','.join(alts),
                    is_snp,
                    al_count,
                    int(ok),
                    dat_c.gt_str,
                    dat_c.gt_str,
                    dat_c.gt_str,
                    sex,
                    ','.join((c, f, m)),
                    sep='\t')


@command.add_sub
@argument('mendel_tab')
def vcf_mendel_summary(args):
    """
    """
    group_key = ('chrom', 'is_snp', 'al_count', 'sex', 'gt_f', 'gt_m')
    level = list(range(len(group_key)))
    tab = pd.read_table(open(args.mendel_tab),
            dtype={'gt_c': 'str', 'gt_f': 'str', 'gt_m': 'str'})
    gtab = tab.groupby(group_key).apply(lambda tab: pd.DataFrame({
        'count': pd.Series([len(tab)]),
        'ok': pd.Series([tab.ok.sum()]),
        'rate': pd.Series([1. * tab.ok.sum() / len(tab)]),
        },
        columns=['count', 'ok', 'rate'])
    ).reset_index(level=level)
    gtab.to_csv(sys.stdout, sep='\t', index=False)
