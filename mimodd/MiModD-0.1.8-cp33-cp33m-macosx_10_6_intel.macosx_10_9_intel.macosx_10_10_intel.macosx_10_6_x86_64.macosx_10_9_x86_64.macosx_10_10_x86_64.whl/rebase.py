import sys

from collections import OrderedDict

from . import liftover, pyvcf, bioobj_base
from . import ArgumentParseError


def rebase_vcf (input_file, chain_file, ofile = None, reverse = False,
                filter = 'unique', verbose = False):
    if filter not in ('unique', 'best', 'all'):
        raise ArgumentParseError(
            'Unknown filter argument "{0}".'.format(filter)
            )
    # use liftover.load to autodetect whether the chain file is
    # gzipped or uncompressed
    lift = liftover.load(chain_file, reverse=reverse)
    with pyvcf.open(
        input_file, 'r'
        ) if input_file else pyvcf.VCFReader(sys.stdin) as invcf:
        # turn contig sizes encoded in chain file into vcf header meta data
        newcontigs = OrderedDict()
        for contig, size in sorted(
            {
                (chain.target_name, chain.target_size)
                for chain in lift.chains
                }
            ):
            newcontigs[contig] = OrderedDict([('length', size)])
        invcf.info.meta['contig'] = newcontigs
        with pyvcf.VCFWriter(
            open(ofile, 'w', encoding=pyvcf.defaultencoding)
            if ofile else sys.stdout,
            invcf.info
        ) as f:
            # remap all records in the input and gather the results
            remapped = []
            unique = multiple = unmapped = unknown = 0
            unknown_contigs = set()
            for entry in invcf:
                convert = lift.convert_coordinate(
                    entry.chrom,
                    entry.pos - 1, # VCF-positions are 1-, chain files 0-based
                    )
                if convert is None:
                    unknown += 1
                    unknown_contigs.add(entry.chrom)
                    convert = []
                elif convert == []:
                    unmapped += 1
                elif len(convert) > 1:
                    multiple += 1
                    if filter == 'best':
                        convert = convert[:1]
                    elif filter == 'unique':
                        convert = []
                else:
                    unique += 1
                for conversion in convert:
                    entry.chrom = conversion[0]
                    entry.pos = conversion[1] + 1 # VCF positions are 1-based
                    if conversion[2] == '-':
                        # The source maps to the reverse complement of the
                        # target sequence.
                        # We need to reverse-complement the REF and ALT
                        # sequences of the VCF record.
                        entry.ref_list = [
                            bioobj_base.nt_reverse_complement(allele)
                            for allele in entry.ref_list
                            ]
                        entry.alt_list = [
                            bioobj_base.nt_reverse_complement(allele)
                            for allele in entry.alt_list
                            ]
                        # If the REF alelle has a length greater one,
                        # we also need to subtract that surplus from the
                        # variant position.
                        entry.pos -= len(entry.ref_list[0])-1
                    remapped.append(entry)
            mapped = unique if filter == 'unique' else unique+multiple
            total = unique + multiple + unmapped + unknown
            # sort the remapped records by position and write the results
            remapped.sort(key=lambda x: (x.chrom, x.pos))
            for entry in remapped:
                f.write(entry)

            if verbose:
                percent_mapped = format(mapped / total, '.1%')
                if percent_mapped == '100.0%' and mapped < total:
                    percent_mapped = '> 99.9%'
                print(
                    '{0} of {1} input variants ({2}) got remapped to new '
                    'coordinates.'
                    .format(
                        mapped,
                        total,
                        percent_mapped
                        )
                    )
                if multiple == 0:
                    if mapped > 0:
                        print(
                            'All of these were mapped to unique positions in '
                            'the target coordinate system.'
                            )
                elif filter == 'unique':
                    print(
                        '{0} additional variants mapped to multiple locations '
                        'in the target coordinate system and were ignored.'
                        .format(multiple)
                        )
                else:
                    print(
                        '{0} of these variants mapped to multiple locations '
                        'in the target coordinate system.'
                        .format(multiple)
                        )
                if unknown or unmapped:
                    print(
                        '{2} variants could not be remapped.\n'
                        '    {0} of these variants reside on one of {3} '
                        'contigs for which no mapping is defined in the chain '
                        'file and\n'
                        '    {1} variants have positions that are not defined '
                        'in the chain file.'
                        .format(
                            unknown,
                            unmapped,
                            unknown + unmapped,
                            len(unknown_contigs)
                            )
                        )
