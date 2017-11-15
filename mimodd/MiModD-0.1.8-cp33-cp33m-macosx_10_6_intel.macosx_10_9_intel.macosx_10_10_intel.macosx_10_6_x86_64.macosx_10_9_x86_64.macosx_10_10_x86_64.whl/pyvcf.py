import sys
import io
import copy
import shlex

from collections import OrderedDict
from itertools import zip_longest

from .encoding_base import RecordBasedFormatReader, RecordBasedFormatWriter
from .encoding_base import vcf_defaultencoding as defaultencoding
from .encoding_base import vcf_handle_decoding_errors as handle_decoding_errors

from . import pybcftools, bioobj_base, converters
from . import FormatParseError


class VCFcols:
    chrom, pos, id, ref, alt, qual, filter, info, format, first_sample = range(10)
    names = 'CHROM', 'POS', 'ID', 'REF', 'ALT', 'QUAL', 'FILTER', 'INFO'
    format_name = 'FORMAT'

    
class EscapedMetaString (str):
    def __str__ (self):
        return '"' + ''.join('\\' + c if c in '\\"' else c for c in self) + '"'


class MetaList (object):
    def __init__ (self, valuestring):
        self.values = [v.strip() for v in valuestring.split(',')]
    def __str__ (self):
        return '[' + ', '.join(self.values) + ']'
    

def parse_header_line (line):
    """Validate a vcf header line and return the sample names found in it.

    Returns a tuple of the sample names or ('',) if no names are found."""
    
    if line[0] != '#':
        raise FormatParseError(
            'Could not obtain vcf header information.',
            help='A header line starting with a single "#" must precede '
                 'the body of a vcf file.'
            )

    header_fields = line[1:].rstrip('\t\r\n').split('\t')
    if VCFcols.names != tuple(header_fields[0:8]):
        raise FormatParseError(
            'Could not parse vcf header information: Unrecognized header fields.',
            help='The first eight column names specified on the vcf header line are mandatory and must be {0}.'
                 .format(', '.join(VCFcols.names))
            )
    if len(header_fields) > 8:
        if header_fields[8] != 'FORMAT':
            raise FormatParseError(
                'Could not parse vcf header information: unrecognized column title {token} instead of FORMAT.',
                token=header_fields[8],
                help='The ninth vcf header line column name, if specified, must be FORMAT.'
                )
        sample_names = tuple(header_fields[9:])
        if not sample_names:
            raise FormatParseError(
                'Could not parse vcf header information: FORMAT column must be followed by at least one additional column.'
                )
        # TO DO: check for duplicate sample names,
        # but make sure this does not break any MiModD vcf handling
    else:
        sample_names = ('',)
    return sample_names


class VCFEntry (object):
    """Object-based equivalent of a single body line of a vcf file.

    Tab-separated fields of the input line are stored as instance attributes.
    chrom:         CHROM field as string
    pos:           POS field as integer
    id:            ID field as string (None if undefined, i.e., '.' in vcf)
    ref:           REF field as string
    alt:           ALT field as string (None if undefined)
    qual:          QUAL field as float (None if undefined)
    filter:        FILTER field as string (None if undefined)
    info:          INFO field as OrderedDict of tag:value pairs, flags are represented by entries with a None value
    sampleinfo:    sample-specific fields; organized in an OrderedDict with keys taken from the FORMAT field and
                   values being dictionaries of sample names:sample-specific information."""
    
    na = '.'
    
    def __init__(self, vcfline, samplenames):
        """Generate a VCFEntry instance from a vcf line string.

        samplenames should be an ordered iterable of the sample names present
        in the vcf file. The genotype fields extracted from the vcfline string
        get stored internally under these names. None objects in samplenames
        signify that the corresponding genotype field should be ignored in the
        generation of the VCFEntry instance."""
        
        fields = vcfline.rstrip('\t\r\n').split('\t')
        self.samplenames = tuple(name for name in samplenames if name is not None)
        try:
            self.chrom = fields[0]
            self.pos = int(fields[1])
            self.id = fields[2] if fields[2] != '.' else None
            self.ref = fields[3] if fields[3] != '.' else None
            self.alt = fields[4] if fields[4] != '.' else None
            self.qual = float(fields[5]) if fields[5] != '.' else None
            self.filter = fields[6] if fields[6] != '.' else None
            # the INFO field needs conditional parsing for key/value pairs and flags (which have no '=')
            if fields[7] == '.':
                self.info = OrderedDict()
            else:
                self.info = OrderedDict(kvpair if len(kvpair)>1 else (kvpair[0], None) for kvpair in (elem.split('=') for elem in fields[7].split(';')))

            if any(samplenames):
                formatkeys = fields[8].split(':')
                self.sampleinfo = OrderedDict(zip(formatkeys, ({} for i in formatkeys)))
                for sample, item in zip(samplenames, fields[9:]):
                    if samplenames is not None:
                        for key, info in zip_longest(formatkeys, item.split(':'), fillvalue=''):
                            self.sampleinfo[key][sample] = info
            else:
                self.sampleinfo = OrderedDict()
        except IndexError:
            # this line does not have the right number of columns
            # or some other parsing problem, 
            # however, we want to check the possibility that it is
            # a blank line or a line consisting of whitespace only.
            # If that is the case, then we want to raise a fatal error
            # only if the line is followed by any non-empty content.
            # This has to be detected at a higher level so
            # here we just transform the error to make it unique.
            if vcfline.strip():
                raise
            else:
                raise RuntimeError ('Unexpected blank line in VCF file body.')

    @property
    def ref_list(self):
        if self.ref:
            return self.ref.split(',')
        else:
            return []

    @ref_list.setter
    def ref_list(self, allele_list):
        seen = set()
        self.ref = ','.join(al for al in allele_list if al not in seen and not seen.add(al))

    @property
    def alt_list(self):
        if self.alt:
            return self.alt.split(',')
        else:
            return []

    @alt_list.setter
    def alt_list(self, allele_list):
        seen = set()
        self.alt = ','.join(al for al in allele_list if al not in seen and not seen.add(al))

    def alt_as_num(self, allele):
        return self.alt_list.index(allele)+1

    def alt_from_num(self, num):
        return self.alt_list[num-1]
    
    def __str__(self):
        # None values need to be replaced by '.', and flags in the INFO field need special treatment again
        items_to_join = [self.chrom,
                         str(self.pos),
                         self.id or self.na,
                         self.ref or self.na,
                         self.alt or self.na,
                         str(self.qual or self.na),
                         self.filter or self.na,
                         ';'.join(k if v is None else '='.join((k,v))
                                  for k,v in self.info.items()
                                  ) or self.na]
        if any(self.samplenames):
            items_to_join.extend([':'.join(k for k in self.sampleinfo)])
            per_sample_info = self.sampleinfo.values()
            items_to_join.extend([':'.join(d[sample] for d in per_sample_info if d[sample]!='') for sample in self.samplenames])
        return '\t'.join(items_to_join)

    def copy (self):
        copy_of_self = copy.copy(self)
        copy_of_self.info = copy_of_self.info.copy()
        copy_of_self.sampleinfo = copy_of_self.sampleinfo.copy()
        return copy_of_self
    
    def sample_slice (self, samples = []):
        """Return a fake slice of the VCFEntry instance by samples.
        Original data is preserved, but the str representation looks like a slice."""

        for sample in samples:
            if sample not in self.samplenames:
                raise KeyError('{0} is not a valid sample in the input'.format(sample))

        vcf_slice = self.copy()
        vcf_slice.samplenames = samples or ('',)
        return vcf_slice


class Info (object):
    def __init__(self, meta, header_line):
        self.meta = meta or {'fileformat': 'VCFv4.3'}
        self.samples = OrderedDict()

        sample_names = parse_header_line(header_line)
        for s in sample_names:
            self.samples[s] = {}
        # contigs, samples and comment lines have direct counterparts
        # in the SAM/BAM header format and are parsed specially for
        # easier access
        # TO DO: add comments parsing
        self.co = []
        # turn contig length information into ints
        for contig_id in self.meta.get('contig', []):
            try:
                self.meta['contig'][contig_id]['length'] = int(
                    self.meta['contig'][contig_id]['length']
                    )
            except KeyError:
                # ignore malformatted contig lines without 'length' element
                pass
        # parse mimodd-specific header lines (these get written by varcall)
        # parse rg information back into self.samples 
        # this synchronizes meta['rginfo'] and self.samples, but
        # TO DO: should be kept synchronous throughout the lifetime of an
        # Info instance
        if any(self.samples):
            for rginfo_id, values in self.meta.get('rginfo', {}).items():
                if values.get('Name'):
                    # in a genuine MiModD file every rginfo element
                    # should contain a Name element,
                    # so the above is really just protecting against
                    # other software using rginfo with a different tag structure
                    if values['Name'] in self.samples:
                        # only use rginfo if a corresponding sample name exists
                        # other rginfo is silently ignored
                        # TO DO: maybe a warning should be generated instead ?
                        self.samples[values['Name']] = {k:v for k,v in values.items()}
                        # add back the ID of the rginfo for synchronization
                        self.samples[values['Name']]['ID'] = rginfo_id
        elif len(self.meta.get('rginfo', {})) == 1:
            # if there are no sample names defined in the vcf,
            # but there is exactly one rginfo element, then
            # parse this element
            rginfo_id, values = next(iter(self.meta['rginfo'].items()))
            if values.get('Name'):
                self.samples[''] = {k:v for k,v in values.items()}
                # add back the ID of the rginfo for synchronization
                self.samples[values['']]['ID'] = rginfo_id

    @property
    def contigs (self):
        return [
            bioobj_base.Chromosome(
                contig_id, self.meta['contig'][contig_id].get('length', 0)
                )
            for contig_id in self.meta.get('contig', [])
            ]
    
    def getlines (self):
        # TO DO:
        # replace special characters in all items except
        # EscapedMetaString instances with their percent encodings
        lines = []
        for key, values in self.meta.items():
            if isinstance(values, list):
                for value in values:
                    lines.append('##' + '='.join((key, value)))
            elif isinstance(values, OrderedDict):
                for ID, fields in values.items():
                    new_line = '##' + key + '=' + '<ID=' + ID
                    for field_name, field_value in fields.items():
                        new_line += ',' + field_name + '=' + str(field_value)
                    new_line += '>'
                    lines.append(new_line)
            else:
                raise AssertionError('Oh oh, this looks like a bug')
        lastline = '#'+'\t'.join(VCFcols.names)
        if any(self.samples):
            lastline += '\t{0}\t{1}'.format(VCFcols.format_name,
                                            '\t'.join(self.samples))
        lines.append(lastline)
        return lines
            
    def __str__(self): 
        return '\n'.join(self.getlines())

    def sample_slice(self, samples = ('',)):
        for sample in samples:
            if sample not in self.samples:
                raise KeyError('"{0}" is not a valid sample in the input'.format(sample))
        info_slice = copy.copy(self)
        info_slice.samples = OrderedDict([(name, info)
                                          for name, info in self.samples.items()
                                          if name in samples]) \
                                  or OrderedDict([('', {})])
        return info_slice


class VCFLikeFileReader (RecordBasedFormatReader):
    """Abstract base class of Readers for VCF-like files and streams.

    VCF-like files/streams consist of a (optional) VCF-style metadata section,
    a mandatory single header line and an arbitrary number of body lines
    with TAB-separated columns.

    Subclasses need to overwrite the metaparser class attribute with a
    suitable metadata parser.
    """

    def __init__ (self, ifo):
        super().__init__(
            ifo, encoding=defaultencoding, errors=handle_decoding_errors
            )
        meta, header_line = self.parse_info()
        if self.ifo_isseekable:
            self.body_start = ifo.tell()
        # the call of metaparser is what makes this class abstract
        self.info = self.metaparser(meta, header_line)

    def metaparser (self, meta, header_line):
        raise NotImplementedError
    
    def seek (self, offset):
        if not self.ifo_isseekable:
            raise NotImplementedError(
                'seek is implemented only for real files.'
                )
        return self.ifo.seek(self.body_start + offset)

    def parse_info (self):
        """Parse the info section (meta data and header) of a vcf input stream."""
        
        # read the Meta section into a list of lines
        meta_lines = []
        while True:
            line = self.ifo.readline()
            if line[0:2] != '##':
                break
            meta_lines.append(line)
        # parse the Meta list
        meta = self.parse_meta_lines(meta_lines)
        # parse the header line
        if not line:
            if not meta:
                raise FormatParseError(
                    'Could not obtain vcf header information. Empty file.'
                    )
            else:
                raise FormatParseError(
                    'Could not obtain vcf header information.',
                    help='The input contains valid metadata, but seems to be truncated before the header line.'
                    )
        return meta, line

    def parse_meta_lines(self, meta_lines):
        """Parse a list of vcf Meta section lines into an OrderedDict."""
        
        meta = OrderedDict()
        for line_no, line in enumerate(meta_lines, 1):
            line = line.strip()[2:]
            try:
                key, valuestring = [s.strip() for s in line.split("=",1)]
            except ValueError:
                raise FormatParseError(
                    'Malformed meta-information at line {line_no}: "{token}".',
                    token=line,
                    line_no=line_no,
                    help='Expected key=value structure.')
            if valuestring[0] == '<' and valuestring[-1] == '>':
                # a structured Meta value
                try:
                    ID, content = self.parse_structured_meta_value(valuestring)
                except FormatParseError as e:
                    e.token = line,
                    e.line_no = line_no
                    raise e
                if key not in meta:
                    meta[key] = OrderedDict()
                elif not isinstance(meta[key], OrderedDict):
                    raise FormatParseError(
                        'Offending meta-information at line {line_no}: "{token}".',
                        token=line,
                        line_no=line_no,
                        help='Mixed use of simple and structured meta information for same type. Meta information type {0} has been used as a simple type with {0}=value assignment on a previous line, but the current line tries to assign a structured value enclosed in "<>".'
                             .format(key)
                        )                
                if ID not in meta[key]:
                    meta[key][ID] = content
                else:
                    raise FormatParseError(
                        'Malformed meta-information at line {line_no}: "{token}".',
                        token=line,
                        line_no=line_no,
                        help='The ID specified for structured meta data must be unique within the meta type, but ID {0} has been used for type {1} on a previous line.'
                             .format(ID, key)
                        )
            else:
                # a simple Meta value
                if key in meta and not isinstance(meta[key], list):
                    raise FormatParseError(
                        'Offending meta-information at line {line_no}: "{token}".',
                        token=line,
                        line_no=line_no,
                        help='Mixed use of simple and structured meta information for same type. Meta information type {0} has been used as a structured type with values enclosed in "<>" on a previous line, but the current line specifies a simple {0}=value assignment.'
                             .format(key)
                        )                    
                meta.setdefault(key, []).append(valuestring)

        # TO DO: decode percent encodings in all items except
        # EscapedMetaString instances
        return meta


    def parse_structured_meta_value(self, valuestring):
        """Parse structured meta data values enclosed in angle brackets.

        Returns a tuple of the data's ID value and an OrderedDict of all other
        key=value pairs found in the feature."""
        
        structure = OrderedDict()
        valuestring = valuestring[1:-1]
        while valuestring:
            # extract all key=value pairs from the string
            try:
                key, remainder = [s.strip(' ') for s in valuestring.split('=', 1)]
            except ValueError:
                raise FormatParseError(
                    'Malformed meta-information at line {line_no}: "{token}".',
                    help='Expected comma-separated key=value pairs inside "<>".')
            if key in structure:
                raise FormatParseError(
                    'Malformed meta-information at line {line_no}: "{token}".',
                    help='Duplicate key "{0}" found inside structured value.'
                         .format(key)
                    )
            if remainder[0] == '[':
                # the value is a list of options, which
                # we represent as a MetaList
                up_to = remainder.find(']')
                if find == -1:
                    raise FormatParseError(
                        'Malformed meta-information at line {line_no}: "{token}".',
                        help='Unquoted values starting with "[" must be terminated with "]" to form a valid list of items.'
                        )
                value = MetaList(remainder[1:up_to])
                next_split_at = up_to+1
            elif remainder[0] == '"':
                # the value is a string, possibly with escape characters
                # this is a job for the shlex module and our
                # EscapedMetaString class
                lexer = shlex.shlex(remainder, posix=True)
                lexer.quotes = '"'
                value = EscapedMetaString(lexer.get_token())
                next_split_at = len(str(value))
            else:
                # the value is a standard value, which we only
                # need to strip off of the rest of the string
                up_to = remainder.find(',')
                if up_to == -1:
                    value = remainder
                    next_split_at = len(remainder)
                else:
                    value = remainder[:up_to].rstrip(' ')
                    next_split_at = up_to
            structure[key] = value
            valuestring = remainder[next_split_at:].lstrip(' ')
            if valuestring:
                if valuestring[0] != ',':
                    raise FormatParseError(
                        'Malformed meta-information at line {line_no}: "{token}".',
                        help='Expected comma-separated key=value pairs inside "<>".')
                valuestring = valuestring[1:]
        # finished string parsing
        # lets see if there is an ID to return
        try:
            ID = structure.pop('ID')
        except KeyError:
            raise FormatParseError(
                'Malformed meta-information at line {line_no}: "{token}".',
                help='Structured meta data enclosed in "<>" must specify an ID of the form "ID=id_value".'
                )

        return ID, structure


class VCFReader (VCFLikeFileReader):
    metaparser = Info

    def __next__ (self):
        try:
            return VCFEntry(next(self.ifo), self.info.samples)
        except StopIteration:
            # regular end of input
            raise
        except RuntimeError:
            # VCFEntry uses RuntimeError to signal a blank line in the input, 
            # but we consider this only an error if the line is followed
            # by additonal non-blank lines, so let's check this
            for line in self.ifo:
                if line.strip():
                    raise
            raise StopIteration
        except:
            # all other errors indicate a parsing problem 
            raise RuntimeError ('Malformed VCF file body.')
    
    def field_iter (self, field, skip_indels = True):
        """A specialized iterator providing fast access to per-sample field contents.

        Returns a tuple of (chrom, pos, [value_sample1, value_sample2, ...])
        with all elements of type str.
        Skips INDELs by default."""

        if not any(self.info.samples):
            raise RuntimeError('Iteration over sample-specific fields impossible: sample-specific information missing from the vcf input.')
        field_values = [None for sample in self.info.samples]
        for line in self.ifo:
            cols = line.rstrip('\t\r\n').split('\t')
            if not skip_indels or 'INDEL' not in cols[7].split(';'):
                chrom = cols[0]
                pos = cols[1]
                field_index = cols[8].split(':').index(field)
                for i, column in enumerate(cols[9:]):
                    try:
                        field_values[i] = column.split(':')[field_index]
                    except IndexError:
                        field_values[i] = ''
                yield chrom, pos, field_values
    
    def expand_samples (self):
        excluded_gt_set = set('0/|.')
        if any(self.info.samples):
            for e in self:
                for sample in e.samplenames:
                    if any(c not in excluded_gt_set for c in e.sampleinfo['GT'][sample]):
                        yield sample, e
        else:
            # this is not a multi-sample vcf, just yield everything
            for e in self:
                yield '', e
                    
    def by_sample (self):
        excluded_gt_set = set('0/|.')
        if not self.ifo_isseekable:
            raise NotImplementedError(
                'by_sample method is currently implemented only for '
                'seekable files and file-like objects'
                )
        if any(self.info.samples):
            for sample in self.info.samples:
                self.seek(0)
                for e in self:
                    if any(
                      c not in excluded_gt_set
                      for c in e.sampleinfo['GT'][sample]
                      ):
                        yield sample, e
        else:
            # this is not a multi-sample vcf, just yield everything
            for e in self:
                yield '', e

    def sample_slice (self, samples):
        # WARNING: this method is not doing what it is supposed to do
        # and will be removed or rewritten soon
        # -> do NOT use it !!
        reader_slice = copy.copy(self)
        reader_slice.info = reader_slice.info.sample_slice(samples)
        return reader_slice
    
    def filter (self, h_filters, v_filters = None):
        """An iterator over the lines of a vcf file that pass a user-defined genotype filter.

        The filters argument must be a dictionary of sample names:filters, 
        where the keys must be strings matching sample names declared in the 
        vcf header line, and the values must be filter dictionaries of the form:
        
        {
        'GT': valid vcf genotype strings (e.g., '1/1', '0/1') or tuples thereof,
        'DP': depth of coverage,
        'GQ': genotype quality,
        'DPR': (allele number, minimal fraction, maximal fraction)
        }
        
        that specify eligible values for the samples genotype.

        Example filters:
        {'Sample1':{
                    'GT':'1/1'
                   }}
        => yields all entries where Sample1's genotype is 1/1
        {'Sample1':{
                    'GT':'1/1'
                   },
         'Sample2':{
                    'GT':('0/1','0/0')
                   }}
        => yields entries where Sample1's genotype is 1/1 and Sample2's 
        genotype is either 0/1 or 0/0."""

        if not any(self.info.samples):
            raise RuntimeError('filter: sample-specific information missing from the vcf input.')
        # extract all fieldkeys occurring in any filter dictionary as a flat set
        fieldkeys = {key for filterdict in h_filters.values()
                         for key in filterdict}
        fieldkeys_not_found = set()
        any_applicable = False
        for v in self:
            undefined_keys = fieldkeys - set(v.sampleinfo) 
            if undefined_keys:
                # this record does not have one of the fieldkeys
                # we want to filter for
                fieldkeys_not_found.update(undefined_keys)
                break
            # we got here so at least one record had all fieldkeys and could
            # be filtered
            any_applicable = True
            try:
                for samplekey in h_filters:
                    if 'GT' in h_filters[samplekey]:
                        if v.sampleinfo['GT'][samplekey] not in h_filters[samplekey]['GT']:
                            break
                    if 'DP' in h_filters[samplekey]:
                        try:
                            coverage_for_sample = int(v.sampleinfo['DP'][samplekey])
                        except ValueError:
                            break
                        if coverage_for_sample < h_filters[samplekey]['DP']:
                            break
                    if 'GQ' in h_filters[samplekey]:
                        try:
                            quality_for_sample = int(v.sampleinfo['GQ'][samplekey])
                        except ValueError:
                            break
                        if quality_for_sample < h_filters[samplekey]['GQ']:
                            break
                    if 'DPR' in h_filters[samplekey]:
                        allele_no, fmin, fmax = h_filters[samplekey]['DPR']
                        # keep record if the fraction of reads supporting
                        # the indicated allele is between fmin and fmax
                        try:
                            dpr_of_sample_list = [int(c) for c in v.sampleinfo['DPR'][samplekey].split(",")]
                        except ValueError:
                            break
                        dp_of_sample = sum(dpr_of_sample_list)                        
                        if dp_of_sample == 0:
                            # avoid division by zero
                            break
                        if allele_no < 0:
                            # with a negative allele_no the filter works on
                            # the predominant non-reference allele
                            ratio = max(dpr_of_sample_list[1:])/dp_of_sample                            
                        else:
                            ratio = dpr_of_sample_list[allele_no]/dp_of_sample                            
                        if ratio < fmin or ratio > fmax:
                            break
                else:
                    if v_filters:
                        yield v.sample_slice(v_filters)
                    else:
                        yield v
            except KeyError:
                raise RuntimeError('VCF file has no sample named "{0}".'.format(samplekey))
        if not any_applicable:
            msg = 'Could not apply filters to any record because no line in the vcf file specifies all of the following required FORMAT keys: '
            msg += ', '.join(fieldkeys_not_found)
            raise RuntimeError(msg)

    def split_affected (self):
        """Iterator for splitting a vcf file into separate files for each sample.

        Returns a tuple of the same length and in the same order as the samples in the vcf file.
        In it, each element is either a VCFEntry instance representing the current line or None.
        A VCFEntry instance signifies that the corresponding sample has a non-wt genotype at the site."""

        if not any(self.info.samples):
            raise RuntimeError('This is not a multi-sample vcf file. Nothing to split.')
        for v in self:
            yield tuple((v if v.sampleinfo['GT'][sample] not in ('0/0', '0|0') else None
                         for sample in self.info.samples))


def open (file, mode = 'r'):
    if mode == 'r':
        return VCFReader(io.open(file, mode, encoding=defaultencoding,
                                 errors=handle_decoding_errors))
    elif mode == 'rb':
        with pybcftools.open(file):
            # if we get here, we passed a simple format check and
            # are likey dealing with a bcf file
            pass
        return VCFReader(pybcftools.view(file, encoding=defaultencoding,
                                         errors=handle_decoding_errors))
    elif mode == 'w':
        return VCFWriter(io.open(file, mode, encoding=defaultencoding))
    else:
        raise ValueError('Unsupported value for mode: "{0}"'.format(mode))


class VCFWriter (RecordBasedFormatWriter):
    """Write VCFReader input as VCF.

    In order to write custom formats, subclasses may wish to overwrite
    record_to_str to specify how a VCFEntry should be transformed to a string
    before writing (see the cloudmap module for an example).
    """
    
    def __init__ (self, ofile_obj, header=None, samples=None, converter=None):
        if converter is None:
            converter = VCFRecord_VCF_Converter(header, samples)
        super().__init__(
            ofile_obj, encoding=defaultencoding, converter=converter
            )
        self.samples = samples


class VCFRecord_VCF_Converter (converters.Record_Converter):
    """Convert a VCFEntry object to a string in VCF format using the
    Record_Converter interface.
    """

    def __init__ (self, header=None, samples=None):
        if samples is None:
            self.header = header
        else:
            self.header = header.sample_slice(samples)
        self.samples = samples
        super().__init__(header)

    def convert (self, record):
        if self.samples is not None:
            record = record.sample_slice(self.samples)
        return str(record)
