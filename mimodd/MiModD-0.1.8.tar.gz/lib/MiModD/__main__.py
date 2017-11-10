# this is the complete command line parser and tool dispatcher for the MiModD
# Python package

import os
import argparse
import importlib

from . import __version__, terms
from . import auxparsers, help
from . import MiModDError, FormatParseError

from .encoding_base import DEFAULTENCODING, FALLBACKENCODING


if os.path.exists(
    os.path.join(
        os.path.dirname(__file__),
        '__first_run__.py')):
    print(terms)
    raise MiModDError(
        """This is a fresh installation of the package.

You MUST run the config tool once before you can start using it."""
        )


# argparse.Action subclasses
def str_or_None (string):
    """Convert empty strings to None.

    Used to convert empty command line arguments to None before passing them
    to underlying Python functions."""
    
    if string:
        return string
    else:
        return None


class Extend(argparse.Action):
    """Custom action similar to the 'append' action.

    Useful for optional arguments parsed with nargs='*' or nargs='+' if you do
    not want the nested lists produced by 'append'."""
    
    def __call__ (self, parser, namespace, values, option_string = None):
        setattr(namespace, self.dest,
                getattr(namespace, self.dest, []) + values)


# subclass for exclusive use by the annotate subparser
class LinkFormatter(argparse.Action):
    def __call__ (self, parser, namespace, formatter_file, option_string=None):
        try:
            with open(formatter_file, 'r', encoding=DEFAULTENCODING) as f:
                lines = f.readlines()
        except UnicodeDecodeError:
            with open(formatter_file, 'r', encoding=FALLBACKENCODING) as f:
                lines = f.readlines()
        # ignore comments and empty lines
        try:
            first_line, *lines = [
                x for x in (line.split('##')[0].strip() for line in lines)
                if x
                ]
        except ValueError:
            raise FormatParseError(
                'No significant lines found in formatter file.',
                help='The file is empty or has its lines commented out.'
                )
        known_keys = set(['pos', 'gene'])
        invalid_file_msg = '{0} is not a valid formatter file.'.format(
            formatter_file
            )
        invalid_line_msg = 'Invalid line in formatter file {0}.'.format(
            formatter_file
            )
        attribute, _, species = first_line.partition(':')
        if attribute.rstrip() != 'species' or not species:
            raise FormatParseError(
                invalid_file_msg,
                help='Need a species declared on first significant line.'
                )
        species = species.lstrip()
        formatter_dict = {species: {}}
        for line in lines:
            attribute, _, value = line.partition(':')
            if not _:
                raise FormatParseError(
                    invalid_line_msg,
                    help='For species {0}, line "{1}" does not specify a '
                         'key : value pair.'.format(species, attribute[:30])
                    )
            attribute = attribute.rstrip()
            value = value.lstrip()
            if attribute == 'species':
                if not formatter_dict[species]:
                    # no attributes declared in previous species section
                    break
                species = value
                if not species:
                    raise FormatParseError(
                        invalid_line_msg,
                        help='"species :" token without value found.'
                        )
                if species in formatter_dict:
                    raise FormatParseError(
                        invalid_line_msg,
                        help='Species {token} found twice in formatter file.',
                        token=species
                        )
                formatter_dict[species] = {}
            elif attribute in known_keys:
                if attribute in formatter_dict[species]:
                    raise FormatParseError(
                        invalid_line_msg,
                        help='Attribute {0} declared twice for species {1}.'
                        .format(attribute, species)
                        )
                if not value:
                    raise FormatParseError(
                        invalid_line_msg,
                        help='No value found for attribute {0} of species {1}.'
                             .format(attribute, species)
                        )
                formatter_dict[species][attribute] = value
            else:
                raise FormatParseError(
                    invalid_line_msg,
                    help='"{token}" is not a valid attribute.',
                    token=attribute[:50]
                    )
        if not formatter_dict[species]:
            raise FormatParseError(
                invalid_file_msg,
                help='Found a truncated record for species {token}.',
                token=species
                )
        setattr(namespace, 'link_formatter', formatter_dict)


# COMMAND LINE PARSERS FOR MIMODD MODULES
parser = argparse.ArgumentParser(
    usage=argparse.SUPPRESS,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description=terms + """

general command line usage:

  %(prog)s <tool> [OPTIONS]     to run a specific tool

  %(prog)s <tool> --help        for more detailed help on a specific tool
  
"""
    )

subparsers = parser.add_subparsers(title='available tools', metavar='')


# ++++++++++ version +++++++++++
p_info = subparsers.add_parser('version')
p_info.add_argument(
    '-q', '--quiet',
    action='store_true', default=argparse.SUPPRESS,
    help='print version number only'
    )
p_info.set_defaults(version=True)


# ++++++++++ info +++++++++++
p_info = subparsers.add_parser('info', help=help.help_commands['info'])
p_info.add_argument(
    'ifile',
    metavar='input file',
    help='input file (supported formats: sam, bam, vcf, bcf, fasta)'
    )
p_info.add_argument(
    '-o', '--ofile',
    help='redirect the output to the specified file (default: stdout)'
    )
p_info.add_argument(
    '-v', '--verbose',
    action='store_true', default=argparse.SUPPRESS, help='verbose output'
    )
p_info.add_argument(
    '--oformat',
    metavar='html|txt', default=argparse.SUPPRESS,
    help='format for the output (default: txt)'
    )
p_info.set_defaults(module='fileinfo', func=['fileinfo'])


# +++++++++++ header +++++++++++++
p_samheader = subparsers.add_parser(
    'header', help=help.help_commands['header']
    )
rg_group = p_samheader.add_argument_group('read group description')
rg_group.add_argument(
    '--rg-id',
    dest='rg_id', nargs='+', action=Extend, default=[],
    help='one or more unique read group identifiers'
    )
rg_group.add_argument(
    '--rg-sm',
    dest='rg_sm', nargs='+', type=str_or_None, action=Extend,
    default=argparse.SUPPRESS, help='one sample name per read group identifier'
    )
rg_group.add_argument(
    '--rg-cn',
    dest='rg_cn', nargs='+', type=str_or_None, action=Extend,
    default=argparse.SUPPRESS, help='one sequencing center name per read group'
    )
rg_group.add_argument(
    '--rg-ds',
    dest='rg_ds', nargs='+', type=str_or_None, action=Extend,
    default=argparse.SUPPRESS, help='one description line per read group'
    )
rg_group.add_argument(
    '--rg-dt',
    dest='rg_dt', nargs='+', type=str_or_None, action=Extend,
    default=argparse.SUPPRESS,
    help='date runs were produced (YYYY-MM-DD); one date per read group'
    )
rg_group.add_argument(
    '--rg-lb',
    dest='rg_lb', nargs='+', type=str_or_None, action=Extend,
    default=argparse.SUPPRESS, help='library identifier for each read group'
    )
rg_group.add_argument(
    '--rg-pl',
    dest='rg_pl', nargs='+', type=str_or_None, action=Extend,
    default=argparse.SUPPRESS,
    help='sequencing platform/technology used to produce each read group'
    )
rg_group.add_argument(
    '--rg-pi',
    dest='rg_pi', nargs='+', type=str_or_None, action=Extend,
    default=argparse.SUPPRESS,
    help='predicted median insert size for the reads of each read group'
    )
rg_group.add_argument(
    '--rg-pu',
    dest='rg_pu', nargs='+', type=str_or_None, action=Extend,
    default=argparse.SUPPRESS,
    help='platform unit, e.g., flowcell barcode or slide identifier, '
         'for each read group'
    )
oth_group = p_samheader.add_argument_group('other information')
oth_group.add_argument(
    '--co',
    nargs='*', metavar='COMMENT', dest='comments', default=argparse.SUPPRESS,
    help='an arbitrary number of one-line comment strings'
    )
p_samheader.add_argument(
    '-o', '--ofile',
    metavar='OFILE', dest='outputfile', default=argparse.SUPPRESS,
    help='redirect the output to the specified file (default: stdout)'
    )
p_samheader.add_argument(
    '-x', '--relaxed',
    dest='optional_sm', action='store_true', default=argparse.SUPPRESS,
    help='do not enforce a sample name to be specified for every read group'
    )
p_samheader.set_defaults(module='samheader', func=['run_as_main'])


# ++++++++++ convert ++++++++++
p_convert = subparsers.add_parser(
    'convert', help=help.help_commands['convert'], conflict_handler='resolve'
    )
p_convert.add_argument(
    'input1',
    metavar='input_file(s)', nargs='+',
    help='a list of input files (alternating r1 and r2 files for paired-end '
         'data'
    )
p_convert.add_argument(
    '--iformat',
    choices=('fastq', 'fastq_pe', 'gz', 'gz_pe', 'sam', 'bam'),
    default=argparse.SUPPRESS,
    help='the format of the input file(s) (default: bam)'
    )
p_convert.add_argument(
    '-o', '--ofile',
    metavar='OFILE', dest='outputname', default=argparse.SUPPRESS,
    help='redirect the output to the specified file (default: stdout)'
    )
p_convert.add_argument(
    '--oformat',
    choices=('sam', 'bam', 'fastq', 'gz'), default=argparse.SUPPRESS,
    help='the output format (default: sam)'
    )
p_convert.add_argument(
    '-h', '--header',
    default=argparse.SUPPRESS,
    help='optional SAM file, the header information of which should be used '
         'in the output (will overwrite pre-existing header information from '
         'the input file); not allowed for input in SAM/BAM format'
    )
p_convert.add_argument(
    '-r', '--split-on-rgs',
    action='store_true', default=argparse.SUPPRESS,
    help='if the input file has reads from different read groups, write '
         'them to separate output files (using --ofile OFILE as a file name '
         'template); implied for conversions to fastq format'
    )
p_convert.add_argument(
    '-t', '--threads',
    type=int, default=argparse.SUPPRESS,
    help='the number of threads to use (overrides config setting; ignored if '
         'not applicable to the conversion)'
    )
p_convert.set_defaults(module='convert', func=['clparse_convert'])


# ++++++++++ reheader ++++++++++++++++++++
p_reheader = subparsers.add_parser(
    'reheader', help=help.help_commands['reheader']
    )
p_reheader.add_argument(
    'template',
    nargs='?', help='template SAM file providing header information'
    )
p_reheader.add_argument(
    'inputfile',
    metavar='input_file', help='input BAM file to reheader'
    )
p_reheader.add_argument(
    '--rg',
    nargs='+', metavar=('ignore|update|replace [RG_TEMPLATE]', 'RG_MAPPING'),
    default=argparse.SUPPRESS,
    help='how to compile the read group section of the new header;\n'
         'ignore: do not use template information -> keep original read '
         'groups, update: use template information to update original header '
         'content, replace: use only template read group information -> '
         'discard original (default: replace if a general template is '
         'specified, ignore if not);\n'
         'the optional RG_TEMPLATE is used instead of the general template to '
         'provide the template read group information;\n'
         'by default, update mode uses template information about read-groups '
         'to add to / overwrite the original information of read-groups with '
         'the same ID, keeps all read-groups found only in the original header '
         'and adds read-groups found only in the template;\n'
         'replace overwrites all original information about a read-group if a '
         'read-group with the same ID is found in the template, discards all '
         'read-groups found only in the original header and adds read-groups '
         'found only in the template;\n'
         'to update or replace the information of a read group with that of a '
         'template read-group with a different ID, a RG_MAPPING between old '
         'and new ID values can be provided in the format old_id : new_id '
         '[old_id : new_id, ..]'
    )
p_reheader.add_argument(
    '--sq',
    nargs='+', metavar=('ignore|update|replace [SQ_TEMPLATE]', 'SQ_MAPPING'),
    default=argparse.SUPPRESS,
    help='how to compile the sequence dictionary of the new header;\n'
         'ignore: do not use template information -> keep original sequence '
         'dictionary, update: use template information to update original '
         'header content, replace: use only template sequence information -> '
         'discard original (default: replace if a general template is '
         'specified, ignore if not);\n'
         'the optional SQ_TEMPLATE is used instead of the general template to '
         'provide the template sequence dictionary;\n'
         'by default, update mode uses template sequence information to add '
         'to / overwrite the original information of sequences with the same '
         'name (SN tag value), keeps all sequences found only in the original '
         'header and adds sequences found only in the template;\n'
         'replace overwrites all original information about a sequence if a '
         'sequence with the same name is found in the template, discards all '
         'sequences found only in the original header and adds sequences found '
         'only in the template;\n' 
         'to update or replace the information about a sequence with that of '
         'a template sequence with a different name, a SQ_MAPPING between old '
         'and new sequence names (SN values) can be provided in the format '
         'old_sn : new_sn [old_sn : new_sn, ..];\n'
         'to protect against file format corruption, the tool will NEVER '
         'modify the recorded LENGTH (LN tag) nor the MD5 checksum (M5 tag) '
         'of any sequence'
    )
p_reheader.add_argument(
    '--co',
    nargs='+', metavar=('ignore|update|replace', 'CO_TEMPLATE'),
    default=argparse.SUPPRESS,
    help='how to compile the comments (CO lines) of the new header;\n'
         'ignore: do not use template comments -> keep original comments, '
         'update: append template comment lines to original comments, '
         'replace: use only template comments -> discard original (default: '
         'replace if a general template is specified, ignore if not);\n'
         'the optional CO_TEMPLATE is used instead of the general template to '
         'provide the template comments'
    )
p_reheader.add_argument(
    '--rgm', nargs='+', dest='rg_mapping', default=argparse.SUPPRESS,
    help='optional mapping between read group ID values in the format '
         'old_id : new_id [old_id : new_id, ..];\n'
         'used to rename read groups and applied AFTER any other modifications '
         'to the read group section (i.e., every old_id must exist in the '
         'modified header)'
    )
p_reheader.add_argument(
    '--sqm',
    nargs='+', dest='sq_mapping', default=argparse.SUPPRESS,
    help='optional mapping between sequence names (SN field values) in the '
         'format old_sn : new_sn [old_sn : new_sn, ..];\n'
         'used to rename sequences in the sequence dictionary and applied '
         'AFTER any other modifications to the sequence dictionary (i.e., '
         'every old_sn must exist in the modified header)'
    )
p_reheader.add_argument(
    '-o', '--ofile',
    metavar='OFILE', dest='outputfile',
    help='redirect the output to the specified file (default: stdout)'
    )
p_reheader.add_argument(
    '-H',
    dest='header_only', action='store_true', default=False,
    help='output only the resulting header'
    )
p_reheader.add_argument(
    '-v', '--verbose', action='store_true', default=False
    )
p_reheader.set_defaults(module='convert', func=['clparse_reheader'])


# ++++++++++ sort ++++++++++++
p_sort = subparsers.add_parser(
    'sort', help=help.help_commands['sort']
    )
p_sort.add_argument(
    'ifile',
    metavar='input_file', help='the unsorted input file in SAM/BAM format'
    )
p_sort.add_argument(
    '-o', '--ofile',
    metavar='OFILE', default=argparse.SUPPRESS,
    help='redirect the output to the specified file (default: stdout)'
    )
p_sort.add_argument(
    '--iformat',
    metavar='bam|sam', default=argparse.SUPPRESS,
    help='the format of the input file (default: assume bam)'
    )
p_sort.add_argument(
    '--oformat',
    metavar='bam|sam', default=argparse.SUPPRESS,
    help='specify whether the output should be in sam or bam format '
         '(default: bam)'
    )
p_sort.add_argument(
    '-n', '--by-name',
    dest='by_read_name', action='store_true', default=argparse.SUPPRESS,
    help='sort by read name'
    )
p_sort.add_argument(
    '-l',
    dest='compression_level', type=int, default=argparse.SUPPRESS,
    help='compression level, from 0 to 9'
    )
p_sort.add_argument(
    '-m', '--memory',
    type=int, dest='maxmem', metavar='MEMORY', default=argparse.SUPPRESS,
    help='maximal amount of memory to be used in GB (overrides config setting)'
    )
p_sort.add_argument(
    '-t', '--threads',
    type=int, default=argparse.SUPPRESS,
    help='the number of threads to use (overrides config setting)'
    )
p_sort.set_defaults(module='pysamtools', func=['sort'])


# +++++++++++ index ++++++++++++
p_index = subparsers.add_parser(
    'index', help=help.help_commands['index'],
    conflict_handler='resolve'
    )
p_index.add_argument(
    'idxformat',
    metavar='INDEX_TYPE', choices=('fai', 'bai', 'snap'),
    help='the type of index to be generated; use "snap" to create a reference '
         'genome index for the snap alignment tool, "fai" to produce a '
         'samtools-style reference index, "bai" for a bam file index that can '
         'be used, e.g., with the varcall tool and is required by third-party '
         'tools like IGV.'
    )
p_index.add_argument(
    'ifile',
    metavar='FILE_TO_INDEX',
    help='the fasta (reference genome) or bam (aligned reads) input file to '
         'index'
    )
p_index.add_argument(
    '-o', '--output',
    dest='opath', metavar='PATH', default=argparse.SUPPRESS,
    help='specifies the location at which to save the index (default: save '
         'the index alongside the input file as <input file>.<INDEX_TYPE> for '
         'indices of type "fai" and "bai", or in a directory '
         '<input file>.snap_index)'
    )
p_index.add_argument(
    '-t', '--threads',
    type=int, default=argparse.SUPPRESS,
    help='maximum number of threads to use (overrides config setting)'
    )
p_index.add_argument(
    '-q', '--quiet',
    action='store_true', default=False,
    help='suppress original messages from underlying tools'
    )
p_index.add_argument(
    '-v', '--verbose',
    action='store_true', default=False,
    help='verbose output'
    )
snap_group = p_index.add_argument_group('snap-specific options')
snap_group.add_argument(
    '-s', '--seedsize', '--idx-seedsize',
    type=int, default=argparse.SUPPRESS,
    help='Seed size used in building the index (default: 20)'
    )
snap_group.add_argument(
    '-h', '--slack', '--idx-slack',
    type=float, default=argparse.SUPPRESS,
    help='Hash table slack for indexing (default: 0.3)'
    )
snap_group.add_argument(
    '-O', '--overflow', '--idx-overflow',
    dest='ofactor', metavar='FACTOR', type=int, default=argparse.SUPPRESS,
    help='factor (between 1 and 1000) to set the size of the index build '
         'overflow space (default: 40)'
    )
p_index.set_defaults(module='index', func=['index'])


# +++++++++++ snap ++++++++++++++++++
p_snap = subparsers.add_parser(
    'snap', help=help.help_commands['snap'],
    parents=[auxparsers.SnapCLParser], conflict_handler='resolve'
    )
p_snap.set_defaults(module='snap', func=['snap_call'])


# +++++++++++ snap_batch ++++++++++++
p_snap_batch = subparsers.add_parser(
    'snap-batch', help=help.help_commands['snap-batch']
    )
xor = p_snap_batch.add_mutually_exclusive_group(required=True)
xor.add_argument(
    '-s',
    metavar='"COMMAND"', dest='commands', nargs='+',
    help='one or more completely specified command line calls to the snap tool '
         '(use "" to enclose individual lines)'
    )
xor.add_argument(
    '-f',
    metavar='FILE', dest='ifile',
    help='an input file of completely specified command line calls to the snap '
         'tool'
    )
p_snap_batch.set_defaults(
    module='snap', func=['snap_batch','make_snap_argdictlist']
    )


# +++++++++++ varcall +++++++++++++
p_varcall = subparsers.add_parser(
    'varcall', help=help.help_commands['varcall']
    )
p_varcall.add_argument(
    'ref_genome',
    metavar='reference_genome', help='the reference genome (in fasta format)'
    )
p_varcall.add_argument(
    'inputfiles',
    metavar='input_file(s)', nargs='+',
    help='one or more BAM input files of aligned reads from one or more '
         'samples (will be indexed automatically)'
    )
p_varcall.add_argument(
    '--index-files',
    dest='index_files', metavar='INDEX FILE', nargs='+',
    default=argparse.SUPPRESS,
    help='pre-computed index files for all input files'
    )
p_varcall.add_argument(
    '-o', '--ofile',
    metavar='OFILE', dest='output_vcf',
    help='redirect the output (variant sites) to the specified file '
         '(default: stdout)'
    )
p_varcall.add_argument(
    '-i', '--group-by-id',
    dest='group_by_id', action='store_true', default=False,
    help='optional flag to control handling of multi-sample input; '
         'if enabled, reads from different read groups are analyzed as '
         'separate samples even if the sample names associated with the read '
         'groups are identical; otherwise, the samtools default is used '
         '(reads are grouped based on the sample names of their read groups)'
    )
p_varcall.add_argument(
    '-x', '--relaxed',
    dest='md5check', action='store_false',
    help='turn off md5 checksum comparison between sequences in the reference '
         'genome and those specified in the BAM input file header(s)'
    )
p_varcall.add_argument(
    '-d', '--max-depth',
    dest='max_depth', type=int, default=250,
    help='average sample depth cap applied to input with extraordinarily '
         'large numbers of samples sequenced at high coverage '
         'to limit memory usage (default: 250)'
    )
p_varcall.add_argument(
    '-q', '--quiet',
    action='store_true', default=False,
    help='suppress original messages from samtools mpileup and bcftools call'
    )
p_varcall.add_argument(
    '-v', '--verbose',
    action='store_true', default=False,
    help='verbose output independent of samtools/bcftools'
    )
p_varcall.add_argument(
    '-t', '--threads',
    type=int, default=argparse.SUPPRESS,
    help='the number of threads to use (overrides config setting)'
    )
p_varcall.set_defaults(module='variant_calling', func=['varcall'])


# +++++++++++ varextract +++++++
p_varex = subparsers.add_parser(
    'varextract', help=help.help_commands['varextract']
    )
p_varex.add_argument(
    'inputfile', metavar='input file', help='BCF output from varcall'
    )
p_varex.add_argument(
    '-p', '--pre-vcf', metavar='VCF_INPUT', nargs='+', dest='vcf_pre'
    )
p_varex.add_argument(
    '-a', '--keep-alts',
    action='store_true', default=argparse.SUPPRESS,
    help='keep all alternate allele candidates even if they do not appear in '
         'any genotype'
    )
p_varex.add_argument(
    '-v', '--verbose',
    action='store_true', default=False, help='verbose output'
    )
p_varex.add_argument(
    '-o', '--ofile',
    metavar='OFILE', dest='output_vcf',
    help='redirect the output (variant sites) to the specified file '
         '(default: stdout)'
    )
p_varex.set_defaults(module='variant_calling', func=['varextract'])


# +++++++++++ covstats +++++++++
p_stats = subparsers.add_parser(
    'covstats', help=help.help_commands['covstats']
    )
p_stats.add_argument(
    'inputfile',
    metavar='input file', help='BCF output from varcall'
    )
p_stats.add_argument(
    '-o', '--ofile',
    metavar='OFILE',
    help='redirect the output to the specified file (default: stdout)'
    )
p_stats.set_defaults(module='variant_calling', func=['get_coverage_from_vcf'])


# ++++++++++ delcall ++++++++
p_delcall = subparsers.add_parser('delcall', help=help.help_commands['delcall'])
p_delcall.add_argument(
    'ibams',
    metavar='BAM input file(s)', nargs='+',
    help='one or more BAM input files of aligned reads from one or more samples'
    )
p_delcall.add_argument(
    'icov',
    metavar='BCF file with coverage information',
    help='coverage input file (as generated by the varcall tool)'
    )
p_delcall.add_argument(
    '--index-files',
    dest='index_files', metavar='INDEX FILE', nargs='+',
    default=argparse.SUPPRESS,
    help='pre-computed index files for all input files'
    )
p_delcall.add_argument(
    '-o', '--ofile',
    help='redirect the output to the specified file (default: stdout)'
    )
p_delcall.add_argument(
    '--max-cov',
    metavar='COVERAGE THRESHOLD', dest='max_cov', type=int,
    default=argparse.SUPPRESS,
    help='maximal coverage allowed at any site within an uncovered region '
         '(default: 0)'
    )
p_delcall.add_argument(
    '--min-size',
    metavar='SIZE THRESHOLD', dest='min_size', type=int,
    default=argparse.SUPPRESS,
    help='minimal size in nts for an uncovered region to be reported '
         '(default: 100)'
    )
p_delcall.add_argument(
    '-u', '--include-uncovered',
    dest='include_uncovered', action='store_true', default=argparse.SUPPRESS,
    help='include uncovered regions in the output that did not get called as '
         'deletions'
    )
p_delcall.add_argument(
    '-i', '--group-by-id',
    dest='group_by_id', action='store_true', default=False,
    help='optional flag to control handling of multi-sample input; '
         'if enabled, reads from different read groups will be treated '
         'strictly separate. If turned off, read groups with identical sample '
         'names are used together for identifying uncovered regions, but are '
         'still treated separately for the prediction of deletions.'
    )
p_delcall.add_argument(
    '-v', '--verbose',
    action='store_true', default=False, help='verbose output'
    )
p_delcall.set_defaults(module='deletion_calling', func=['delcall'])


# ++++++++++ vcf-filter ++++++++++++++++++
p_vcf_filter = subparsers.add_parser(
    'vcf-filter', help=help.help_commands['vcf-filter'],
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog="""Example filters:
-s sample1 --gt 0/1,1/1
\t\tretain all entries of the vcf input file for which
\t\tsample1's genotype is 0/1 (heterozygous) or
\t\t1/1 (homozygous variant)
-s sample1 sample2 --gt 0/1,1/1 0/0
\t\tretain all entries for which sample1's genotype is 0/1 or 1/1
\t\tAND for which sample2's genotype is 0/0
-s sample1 sample2 --gt 0/1,1/1 ANY --dp 3 3
\t\tretain all entries for which sample1's genotype is 0/1 or 1/1
\t\tAND for which sample1 and sample2 show at least 3-fold coverage
\t\t(sample2's genotype doesn't matter)
"""
)
p_vcf_filter.add_argument(
    'ifile',
    nargs='?', metavar='input_file', help='a vcf input file (default: stdin)'
    )
p_vcf_filter.add_argument(
    '-o', '--ofile',
    metavar='OFILE', default=argparse.SUPPRESS,
    help='redirect the output to the specified file (default: stdout)'
    )
p_vcf_filter.add_argument(
    '-s', '--samples',
    metavar='SAMPLE_NAME', nargs='+', default=argparse.SUPPRESS,
    help='one or more sample names that the sample-specific filters --gt, '
         '--dp, and --gq should work on.'
    )
p_vcf_filter.add_argument(
    '--gt',
    metavar='GT_PATTERN', nargs='+', default=argparse.SUPPRESS,
    help='genotype patterns (one per sample, use ANY to skip the requirement '
         'for a given sample) to be included in the output; format: x/x where '
         'x = 0 and x = 1 stand for the reference and the variant allele, '
         'respectively; multiple allowed genotypes for a sample can be '
         'specified as a comma-separated list'
    )
p_vcf_filter.add_argument(
    '--dp',
    metavar='DP_THRESHOLD', nargs='+', default=argparse.SUPPRESS, type=int,
    help='minimal coverage (one per sample, use 0 to skip the requirement for '
         'a given sample) required to include a site in the output'
    )
p_vcf_filter.add_argument(
    '--gq',
    metavar='GQ_THRESHOLD', nargs='+', default=argparse.SUPPRESS, type=int,
    help='minimal genotype quality (one per sample, use 0 to skip the '
         'requirement for a given sample) required to include a site in the '
         'output'
    )
p_vcf_filter.add_argument(
    '--af',
    metavar='ALLELE#:MIN_FRACTION:MAX_FRACTION', nargs='+',
    default=argparse.SUPPRESS,
    help='the fraction of reads supporting a specific ALLELE# must be between '
         'MIN_FRACTION and MAX_FRACTION to include the site in the output'
    )
p_vcf_filter.add_argument(
    '-r', '--region',
    nargs='*', dest='region_filter', default=argparse.SUPPRESS,
    help='keep only variants that fall in one of the given chromsomal regions '
         '(specified in the format CHROM:START-STOP or CHROM: for a whole '
         'chromosome)'
    )
group = p_vcf_filter.add_mutually_exclusive_group()
group.add_argument(
    '-I', '--no-indels',
    dest='type_filter', action='store_const', const=1, default=0,
    help='skip indels in the output'
    )
group.add_argument(
    '-i', '--indels-only',
    dest='type_filter', action='store_const', const=2, default=0,
    help='keep only indels in the output'
    )
p_vcf_filter.add_argument(
    '--vfilter',
    dest='v_filter', nargs='+', default=argparse.SUPPRESS,
    help='vertical sample names filter; if given, only sample columns '
         'specified by name will be retained in the output'
    )
p_vcf_filter.set_defaults(module='vcf_filter', func=['filter'])


# ++++++++++++ rebase +++++++++++++++++
p_rebase = subparsers.add_parser(
    'rebase', help=help.help_commands['rebase']
    )
p_rebase.add_argument('input_file', help='the VCF file to rebase')
p_rebase.add_argument(
    'chain_file',
    help='the UCSC chain file to calculate new coordinates from '
         '(the file may be gzipped or uncompressed)' 
    )
p_rebase.add_argument(
    '-o', '--ofile',
    metavar='OFILE', default=argparse.SUPPRESS,
    help='redirect the output to the specified file (default: stdout)'
    )
p_rebase.add_argument(
    '-r', '--reverse',
    action='store_true', default=False,
    help='swap the genome versions specified in the chain file, i.e., assume '
         'the coordinates in the input file are based on the chain file '
         'target genome version and should be mapped to the source genome '
         'version'
    )
p_rebase.add_argument(
    '-f', '--filter',
    default=argparse.SUPPRESS,
    help='define which mapped variants to report: '
         '"unique": report only unambiguously mapped variants, '
         '"best": for ambiguously mapping variants, report the mapping with '
         'the highest score, '
         '"all": for ambiguously mapping variants, report all mappings '
         '(default: unique)'
    )
p_rebase.add_argument(
    '-v', '--verbose',
    action='store_true', default=False,
    help='report remap statistics'
    )

p_rebase.set_defaults(module='rebase', func=['rebase_vcf'])


# +++++++++++ annotate ++++++++++++++++        
p_annotate = subparsers.add_parser(
    'annotate', help=help.help_commands['annotate']
    )
p_annotate.add_argument(
    'inputfile', metavar='input_file', help='a vcf input file'
    )
p_annotate.add_argument(
    'genome',
    metavar='annotation_source',
    help='the name of an installed SnpEff genome annotation file '
         '(the snpeff-genomes tool can be used to get a list of all such names)'
    )
# optional args
p_annotate.add_argument(
    '-o', '--ofile',
    default=argparse.SUPPRESS,
    help='redirect the output to the specified file (default: stdout)'
    )
p_annotate.add_argument(
    '--codon-tables',
    metavar='TABLE_SPEC', nargs='+', action=Extend,
    default=argparse.SUPPRESS,
    help='specify custom codon tables to be used in assessing variant effects '
         'at the protein level; if a codon table should be used for only a '
         'specific chromosome, use the format CHROM:TABLE_NAME. '
         'Use TABLE_NAME alone to specify a codon table to be used for all '
         'chromosomes, for which no chromosome-specific table is provided. '
         'Valid TABLE_NAMEs are those defined in the Codon tables section of '
         'the SnpEff config file. '
         'NOTE: It is also possible to associate chromosomes with a codon '
         'table permanently by editing the SnpEff config file.'
	)
p_annotate.add_argument(
    '--stats',
    metavar='SUMMARY_FILE', default=argparse.SUPPRESS,
    help='generate a results summary file of the specified name'
    )
p_annotate.add_argument(
    '--no-downstream',
    dest='no_downstream', action='store_true', default=argparse.SUPPRESS,
    help='do not include downstream effects in the output'
    )
p_annotate.add_argument(
    '--no-upstream',
    dest='no_upstream', action='store_true', default=argparse.SUPPRESS,
    help='do not include upstream effects in the output'
    )
p_annotate.add_argument(
    '--no-intron',
    dest='no_intron', action='store_true', default=argparse.SUPPRESS,
    help='do not include intron effects in the output'
    )
p_annotate.add_argument(
    '--no-intergenic',
    dest='no_intergenic', action='store_true', default=argparse.SUPPRESS,
    help='do not include intergenic effects in the output'
    )
p_annotate.add_argument(
    '--no-utr',
    dest='no_utr', action='store_true', default=argparse.SUPPRESS,
    help='do not include UTR effects in the output'
    )
p_annotate.add_argument(
    '--ud',
    metavar='DISTANCE', type=int, default=argparse.SUPPRESS,
    help='specify the upstream/downstream interval length, i.e., variants '
         'more than DISTANCE nts from the next annotated gene are considered '
         'to be intergenic'
    )
p_annotate.add_argument(
    '-c', '--config',
    dest='snpeff_path', metavar='PATH', default=argparse.SUPPRESS,
    help='location of the SnpEff installation directory. '
         'Will override MiModD SNPEFF_PATH config setting if provided.'
    )
p_annotate.add_argument(
    '-m', '--memory',
    type=int, default=argparse.SUPPRESS,
    help='maximal memory to use in GB (overrides config setting)'
    )
p_annotate.add_argument(
    '-q', '--quiet',
    action='store_true', default=False,
    help='suppress original messages from SnpEff'
    )
p_annotate.add_argument(
    '-v', '--verbose',
    action='store_true', default=False,
    help='verbose output (independent of SnpEff)'
    )
p_annotate.set_defaults(module='variant_annotation', func=['cl_annotate'])


# ++++++++++++ snpeff_genomes ++++++++++++
p_snpeff_genomes = subparsers.add_parser(
    'snpeff-genomes', help=help.help_commands['snpeff-genomes']
    )
p_snpeff_genomes.add_argument(
    '-c', '--config',
    dest='snpeff_path', metavar='PATH', default=argparse.SUPPRESS,
    help='location of the SnpEff installation directory. Will override '
         'MiModD config settings if provided.'
    )
p_snpeff_genomes.add_argument(
    '-o', '--ofile',
    metavar='OFILE', dest='output', default=argparse.SUPPRESS,
    help='redirect the output to the specified file (default: stdout)'
    )
p_snpeff_genomes.set_defaults(
    module='variant_annotation', func=['get_installed_snpeff_genomes']
    )


# ++++++++++++ varreport ++++++++++++
p_varreport = subparsers.add_parser(
    'varreport', help=help.help_commands['varreport']
    )
p_varreport.add_argument(
    'inputfile', metavar='input_file', help='a vcf input file'
    )
# optional args
p_varreport.add_argument(
    '-o', '--ofile',
    default=argparse.SUPPRESS,
    help='redirect the output to the specified file (default: stdout)'
    )
p_varreport.add_argument(
    '-f', '--oformat',
    metavar='html|text', choices=('html', 'text'), default=argparse.SUPPRESS,
    help='the format of the output file (default: html)'
    )
p_varreport.add_argument(
    '-s', '--species',
    default=argparse.SUPPRESS,
    help='the name of the species to be assumed when generating annotations'
    )
p_varreport.add_argument(
    '-l', '--link',
    metavar='link_formatter_file', action=LinkFormatter,
    default=argparse.SUPPRESS,
    help='file to read species-specific hyperlink formatting instructions from'
    )
p_varreport.set_defaults(module='variant_annotation', func=['report'])


# ++++++++++++ map +++++++++++++++
p_cm = subparsers.add_parser('map', help=help.help_commands['map'])
p_cm.add_argument(
    'mode',
    metavar='analysis_mode',
    help='specify "SVD" for Simple Variant Density analysis, "VAF" for '
         'Variant Allele Frequency analysis or "VAC" for Variant Allele '
         'Contrast analysis.'
    )
p_cm.add_argument(
    'ifile',
    metavar='input_file',
    help='valid input files are VCF files or per-variant report files '
         '(as generated by this tool with the "-t" option or by the CloudMap '
         'Hawaiian Variant Density Mapping tool).'
    )
p_cm.add_argument(
    '-o', '--ofile',
    default=argparse.SUPPRESS,
    help='redirect the binned variant counts to this file (default: stdout).'
    )
p_cm.add_argument(
    '-q', '--quiet',
    action='store_true', default=False,
    help='suppress warning messages about plotting problems.'
    )
ana_group = p_cm.add_argument_group('analysis control')
ana_group.add_argument(
    '-b', '--bin-sizes',
    metavar='SIZE', nargs='+', default=argparse.SUPPRESS,
    help='list of bin sizes to be used for histogram plots and linkage reports '
         '(default: 1Mb and 500Kb)'
    )
ana_group.add_argument(
    '-m', '--mapping-sample',
    metavar='sample_name',
    help='name of the sample (as appearing in the input vcf file) for which '
         'variants should be mapped (cannot be used in SVD mode)'
    )
vaf_group = p_cm.add_argument_group('VAF mode-specific options')
vaf_group.add_argument(
    '-r', '--related-parent',
    metavar='parent_name',
    help='name of the sample to provide related parent strain (mutagenesis '
         'strain) variants for the analysis in Variant Allele Frequency (VAF) '
         'mode.'
    )
vaf_group.add_argument(
    '-u', '--unrelated-parent',
    metavar='parent_name',
    help='name of the sample to provide unrelated parent strain '
         '(mapping strain) variants for the analysis in Variant Allele '
         'Frequency (VAF) mode.'
    )
vaf_group.add_argument(
    '-i', '--infer', '--infer-missing',
    dest='infer_missing_parent', action='store_true', default=argparse.SUPPRESS,
    help='if variant data for either the related or the unrelated parent '
         'strain is not provided, the tool can try to infer the alleles '
         'present in that parent from the allele spectrum found in the '
         'mapping sample. Use with caution on carefully filtered variant '
         'lists only!'
    )
vac_group = p_cm.add_argument_group('VAC mode-specific options')
vac_group.add_argument(
    '-c', '--contrast-sample',
    metavar='sample_name',
    help='name of the sample (as appearing in the input vcf file) that '
         'provides the contrast for the mapping sample'
    )
compat_group = p_cm.add_argument_group('file format and compatibility options')
compat_group.add_argument(
    '-t', '--text-file',
    default=argparse.SUPPRESS,
    help='generate text-based output for every variant position and save it '
         'to the specified file. This file can be used as input during later '
         'runs of the tool, which will speed up replotting.'
    )
compat_group.add_argument(
    '-s', '--seqinfo',
    metavar='SEQINFO_FILE', dest='seqinfo_external', default=argparse.SUPPRESS,
    help='if an input file does not specify required contig information '
         '(chromosome names and sizes), extract this information from '
         'SEQINFO_FILE. This file can be a reference genome file in fasta '
         'format or a CloudMap-style sequence dictionary file. This option '
         'is never necessary with MiModD-generated input, but can be useful '
         'with input files generated by third-party tools that do not record '
         'contig information in their output.'
    )
compat_group.add_argument(
    '--cloudmap',
    dest='cloudmap_mode', action='store_true', default=argparse.SUPPRESS,
    help='generate valid input for the original CloudMap Mapping tools and '
         'save it to the text output file specified by the "-t" option. '
         'This option can only be used in "SVD" or "VAF" mode, which have '
         'an equivalent in CloudMap.'
    )
plot_group = p_cm.add_argument_group('general plotting options')
plot_group.add_argument(
    '-p', '--plot-file',
    metavar='FILE', default=argparse.SUPPRESS,
    help='generate graphical output and store it in the given file '
         '(default: no graphical output)'
    )
plot_group.add_argument(
    '--fit-width',
    action='store_true', default=argparse.SUPPRESS,
    help='do not autoscale x-axes to size of largest contig'
    )
scatter_group = p_cm.add_argument_group('scatter plot parameters')
scatter_group.add_argument(
    '--no-scatter',
    action='store_true', default=argparse.SUPPRESS,
    help='do not produce scatter plots of observed segregation rates; '
         'just plot histograms'
    )
scatter_group.add_argument(
    '-l', '--loess-span',
    metavar='FLOAT', type=float, default=argparse.SUPPRESS,
    help='span parameter for the Loess regression line through the linkage '
         'data (default: 0.1, specify 0 to skip calculation)'
    )
scatter_group.add_argument(
    '--ylim-scatter',
    metavar='FLOAT', type=float, default=argparse.SUPPRESS,
    help='upper limit for scatter plot y-axis (default: 1)'
    )  
scatter_group.add_argument(
    '-z', '--points-colors',
    nargs='+', metavar='COLOR', default=argparse.SUPPRESS,
    help='color(s) for scatter plot data points'
    )
scatter_group.add_argument(
    '-k', '--loess-colors',
    nargs='+', metavar='COLOR', default=argparse.SUPPRESS,
    help='color(s) for regression line(s) through scatter plot data'
    )
hist_group = p_cm.add_argument_group('histogram plot parameters')
hist_group.add_argument(
    '--no-hist', action='store_true', default=argparse.SUPPRESS,
    help='do not produce linkage histogram plots; only generate scatter plots'
    )
hist_group.add_argument(
    '--no-kde', action='store_true', default=argparse.SUPPRESS,
    help='do not add kernel density estimate lines to histogram plots'
    )
hist_group.add_argument(
    '--ylim-hist',
    metavar='FLOAT', type=float, default=argparse.SUPPRESS,
    help='upper limit for histogram plot y-axis (default: auto)'
    )
hist_group.add_argument(
    '--hist-colors',
    nargs='+', metavar='COLOR', default=argparse.SUPPRESS,
    help='list of colors to be used for plotting histogram bars of different '
         'width (default: darkgrey and red)'
    )
p_cm.set_defaults(module='cloudmap', func=['delegate'])


# ++++++++++++ help +++++++++++++++
p_help = subparsers.add_parser('help')
p_help.add_argument(
    'topic',
    nargs='?',
    help='topic or command for which help is requested. '
         'Show command overview if not given.'
    )
p_help.set_defaults(module='help')


def parse (argv=None):
    args = parser.parse_args(argv)
    if 'module' in args:
        if args.module == 'help':
            # mimodd help
            help.help(args, parser)
        else:
            # regular mimodd subcommand
            module = importlib.import_module('MiModD.'+args.module)

            funcs = [getattr(module, f) for f in args.func]
            del args.func, args.module
            args = vars(args)

            result = funcs[-1](**args)

            for f in funcs[-2::-1]:
                result = f(result)
    elif 'func' not in args:
        if 'version' in args:
            # inline implementation of mimodd version command
            if 'quiet' in args:
                print(__version__)
            else:
                print(terms)
        else:
            # Treat a bare mimodd call like mimodd --help.
            args = parser.parse_args(['--help'])


if __name__ == '__main__':
    parse()
