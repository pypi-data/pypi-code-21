import os
import sys
import io
import shlex
import subprocess
import shutil

from collections import namedtuple, OrderedDict
from contextlib import ExitStack
from threading import Thread

from . import config, encoding_base, templates, tmpfiles
from . import pyvcf, anno_weblinks, bioobj_base
from . import (
    DependencyError, ArgumentParseError, ArgumentValidationError,
    FormatParseError
    )

from .encoding_base import RecordBasedFormatWriter
from .encoding_base import DEFAULTENCODING, ExternalApplicationCall
from .converters import Record_Converter


class VCFRecord_Report_Converter (Record_Converter):
    """Base class of converters that generate multiline output per VCF record.
    """
    
    def __init__ (self, vcf_info, link_formatter=None, samples=None):
        self.link_formatter = link_formatter
        if samples is not None:
            self.samples = samples
            self.slice_samples = True
        else:
            self.samples = vcf_info.samples if any(vcf_info.samples) else []
            self.slice_samples = False
        self.contig_info = {
            contig.name: contig for contig in vcf_info.contigs
            }

    def convert (self, record):
        if self.slice_samples:
            record = record.sample_slice(self.samples)
        effects = EffectsCatalogue.from_VCFRecord(record)
        return '\n'.join(self.build_report_rows(record, effects))
        
    def build_report_rows (self, record, effects):
        rows = []
        location_elem = self.format_location(
            record, effects
            )
        sample_specs_elem = self.format_sample_specs(
            record, effects
            )
        preformatted_effects = []
        for gene_name in effects.effects:
            preformatted_effects.append(
                (
                    self.format_gene(gene_name, record, effects),
                    [
                        t_e for t_e in self.format_transcripts_effects(
                            gene_name, record, effects
                            )
                        ]
                    )
                )
        return self.format_rows(
            location_elem,
            sample_specs_elem,
            preformatted_effects
            )

    def format_rows (self, location, sample_specs, pre_eff):
        rows = []
        for gene, t_e in pre_eff:
            for transcript, eff in t_e:
                rows.append(
                    self.format_row(
                        location, sample_specs, gene, transcript, eff
                        )
                    )
        return rows

    def format_row (self, location, sample_specs, gene, transcript, eff):
        return self.templates['row_template'].format(
            location=location,
            sample_specs=sample_specs,
            gene=gene,
            transcript=transcript,
            effects=eff
            )

    def format_location (self, record, effects=None, **kwargs):
        # Subclasses may wish to override this method to control how locations
        # are formatted.
        if self.link_formatter:
            chr_obj = self.contig_info.get(
                record.chrom,
                # If no information about the contig can be found,
                # use a fallback object and assume the contig extends at least
                # 500 nt beyond the current variant.
                bioobj_base.Chromosome(record.chrom, record.pos + 501)
                )
            location_elem = self.templates['hyperlinked_location_template'].format(
                location_url=self.link_formatter['pos'].format(
                    chromosome=chr_obj,
                    start=max(record.pos-500, 1),
                    stop=min(record.pos+500, chr_obj.length)
                    ),
                chromosome=chr_obj.name,
                position=record.pos,
                **kwargs
                )
        else:
            location_elem = self.templates['location_template'].format(
                chromosome=record.chrom,
                position=record.pos,
                **kwargs
                )
        return location_elem

    def format_sample_specs (self, record, effects=None, **kwargs):
        return self.templates['sample_specs_template'].format(
            gt_items=self.format_gt_items(record),
            **kwargs
            )

    def format_gt_items (self, record):
        # simple default implementation that can be used to report
        # GT, DPR and GQ fields per sample
        gt_data = record.sampleinfo.get('GT')
        dpr_data = record.sampleinfo.get('DPR')
        gq_data = record.sampleinfo.get('GQ')
        nas = ['n/a'] * len(self.samples)
        if gt_data is None:
            gts = nas
        else:
            gts = [gt_data[sample] for sample in record.samplenames]
        if dpr_data is None:
            dprs = nas
        else:
            dprs = [dpr_data[sample] for sample in record.samplenames]
        if gq_data is None:
            gqs = nas
        else:
            gqs = [gq_data[sample] for sample in record.samplenames]

        return '\t'.join(
            self.templates['gt_items_template'].format(
                gt=gt,
                dpr=dpr,
                gq=gq
                )
            for gt, dpr, gq in zip(gts, dprs, gqs)
            )
        
    def format_gene (self, gene_name, record=None, effects=None, **kwargs):
        # Subclasses may wish to override this method to control how genes
        # are formatted.
        return self.templates['gene_template'].format(
            gene=gene_name,
            **kwargs
            )

    def format_transcripts_effects (self, gene_name, record, effects=None):
        # Subclasses may wish to override this method to control how
        # per-transcript effects are reported.
        effects = effects.effects[gene_name]
        for transcript_id in effects:
            effect_spans = [
                self.format_effect(
                    eff_type='ref allele',
                    allele=record.ref
                    )
                ]
            for allele, efftype, impact in effects[transcript_id]:
                effect_spans.append(
                    self.format_effect(
                        eff_type=efftype or '?',
                        allele=allele or record.alt
                        )
                    )

            effects_elem = self.format_effects(effect_spans)
            transcript_elem = self.format_transcript(
                gene_name, transcript_id
                )
            yield transcript_elem, effects_elem

    def format_effects (self, effects, **kwargs):
        return self.templates['effects_template'].format(
            effect_items=''.join(effects)
            )
    
    def format_effect (self, eff_type, allele, **kwargs):
        return self.templates['effect_items_template'].format(
            effect=eff_type,
            allele=allele,
            **kwargs
            )

    def format_transcript (self, gene_name, transcript_id, **kwargs):
        if self.link_formatter and transcript_id:
            transcript_elem = self.templates[
                'hyperlinked_transcript_template'
                ].format(
                    transcript_url=self.link_formatter['gene'].format(
                        gene=gene_name,
                        transcript=bioobj_base.Transcript(transcript_id)
                        ),
                    transcript=transcript_id,
                    **kwargs
                    )
        else:
            transcript_elem = self.templates['transcript_template'].format(
                transcript=transcript_id,
                **kwargs
                )
        return transcript_elem

    
class VCFRecord_HTMLReport_Converter (VCFRecord_Report_Converter):
    """Convert a VCF record to richly formatted HTML."""

    def __init__ (self, vcf_info, link_formatter=None, samples=None):
        super().__init__(vcf_info, link_formatter, samples)
        self.header, self.record_start_template, \
        record_row_template, self.record_details_template, \
        self.record_end, self.footer \
            = templates.parse_html_template('variant_report.html')
        self.templates = {
            'row_template': record_row_template,
            'location_template':
                '<td rowspan="{n_total_transcripts}">'
                '{chromosome}: {position}</td>',
            'hyperlinked_location_template':
                '<td rowspan="{n_total_transcripts}">'
                '<a href={location_url}>{chromosome}: {position}</a></td>',
            'sample_specs_template':
                '<td rowspan="{n_total_transcripts}">'
                '<ul>{gt_items}</ul></td>',
            'gene_template':
                '<td rowspan="{n_assoc_transcripts}">{gene}</td>',
            'transcript_template':
                '<td class="eff" level="{max_effect_level}">{transcript}</td>',
            'hyperlinked_transcript_template':
                '<td class="eff" level="{max_effect_level}">'
                '<a href={transcript_url}>{transcript}</a></td>',
            'effects_template':
                '<td><ul>{effect_items}</ul></td>',
            'effect_items_template':
                '<li class="eff" level="{effect_level}">'
                '<b>{allele}: </b>{effect}</li>',
            'gt_items_template':
                '<li class="gt" gt="{gt_type}" level="{quality_level}">'
                '{genotype}</li>',
            'per_sample_details_template':
                '<tr>'
                '<td>{sample}</td><td>{gt}</td><td>{dpr}</td><td>{gq}</td>'
                '</tr>',
            'allele_legend_template':
                '<li>{allele_no}={allele}</li>',
            }
        self.next_record_uid = 1

    def convert (self, record):
        record_report_parts = [
            super().convert(record), self.format_details_row(record)
            ]
        return self.format_record_report(record_report_parts)

    def format_record_report (self, rows):
        ret = (
            self.record_start_template.format(uid=self.next_record_uid)
            + '\n'.join(rows)
            + self.record_end
            )
        self.next_record_uid += 1
        return ret

    def format_rows (self, location, sample_specs, pre_eff):
        rows = []
        for gene, t_e in pre_eff:
            for transcript, eff in t_e:
                rows.append(
                    self.format_row(
                        location, sample_specs, gene, transcript, eff
                        )
                    )
                # don't report redundant parts repeatedly
                gene = ''
                sample_specs = ''
                location = ''
        return rows

    def format_transcripts_effects (self, gene_name, record, effects):
        effects = effects.effects[gene_name]
        for transcript_id in effects:
            effect_spans = [
                self.format_effect(
                    effect_level='',
                    eff_type='ref allele',
                    allele=record.ref
                    )
                ]
            impacts_seen = set()
            for allele, efftype, impact in effects[transcript_id]:
                impacts_seen.add(impact)
                effect_spans.append(
                    self.format_effect(
                        effect_level=impact,
                        eff_type=efftype or '?',
                        allele=allele or record.alt
                        )
                    )
            effects_elem = self.format_effects(effect_spans)

            for impact in ['HIGH', 'MODERATE', 'MODIFIER', 'LOW']:
                if impact in impacts_seen:
                    break
            else:
                impact = ''

            transcript_elem = self.format_transcript(
                gene_name, transcript_id, max_effect_level=impact
                )
            yield transcript_elem, effects_elem

    def format_location (self, record, effects):
        return super().format_location(
            record,
            n_total_transcripts=effects.n_transcripts_affected()
            )

    def format_sample_specs (self, record, effects):
        return super().format_sample_specs(
            record,
            n_total_transcripts=effects.n_transcripts_affected()
            )

    def format_gene (self, gene_name, record, effects):
        return super().format_gene(
            gene_name,
            n_assoc_transcripts=effects.n_transcripts_affected(gene_name)
            )

    def format_gt_items (self, record):
        if not self.samples:
            return 'n/a'
        gq_level = []
        genotype_data = record.sampleinfo.get('GT')
        if genotype_data is not None:
            gt = []
            gt_types = []
            for sample in record.samplenames:
                genotype = genotype_data[sample]
                if genotype[0] == genotype[2] == '0':
                    gt_type = 'ref'
                elif '.' in genotype:
                    gt_type = 'uncertain'
                elif genotype[0] == genotype[2]:
                    gt_type = 'mut'
                else:
                    gt_type = 'het'
                gt.append(genotype)
                gt_types.append(gt_type)
        else:
            gt = ['?/?'] * len(self.samples)
            gt_types = ['unknown'] * len(self.samples)

        quality_data = record.sampleinfo.get('GQ')
        if quality_data is not None:
            gq_levels = []
            for sample in record.samplenames:
                gq_level = 0
                quality = quality_data[sample]
                if quality.isdecimal():
                    gq_val = int(quality)
                    thresholds = [1, 6, 46, 69, 92]
                    for threshold in thresholds:
                        if gq_val < threshold:
                            break
                        gq_level += 1        
                gq_levels.append(gq_level)
        else:
            gq_levels = [0] * len(self.samples)

        gt_items = [
            self.templates['gt_items_template'].format(
                gt_type=gt_type,
                quality_level=gq_level,
                genotype=genotype
                )
            for gt_type, gq_level, genotype in zip(gt_types, gq_levels, gt)
            ]
        return ''.join(gt_items)

    def format_details_row (self, record):
        if not self.samples:
            return ''
        per_sample_details = self.format_per_sample_details(record)
        allele_legend_elem = self.format_allele_legend(record)
        return self.record_details_template.format(
            allele_legend = allele_legend_elem,
            per_sample_details = per_sample_details
            )

    def format_per_sample_details (self, record):
        gt_data = record.sampleinfo.get('GT')
        dpr_data = record.sampleinfo.get('DPR')
        gq_data = record.sampleinfo.get('GQ')
        nas = ['n/a'] * len(self.samples)
        if gt_data is None:
            gts = nas
        else:
            gts = [gt_data[sample] for sample in record.samplenames]
        if dpr_data is None:
            dprs = nas
        else:
            dprs = [dpr_data[sample] for sample in record.samplenames]
        if gq_data is None:
            gqs = nas
        else:
            gqs = [gq_data[sample] for sample in record.samplenames]

        return '\n'.join(
            self.templates['per_sample_details_template'].format(
                sample=sample,
                gt=gt,
                dpr=dpr,
                gq=gq
                )
            for sample, gt, dpr, gq in zip(record.samplenames, gts, dprs, gqs)
            )
    
    def format_allele_legend (self, record):
        allele_elem_list = [
            self.templates['allele_legend_template'].format(
                allele_no=0, allele='ref'
                )
            ]
        for no, al in enumerate(record.alt_list, 1):
            allele_elem_list.append(
            self.templates['allele_legend_template'].format(
                allele_no=no, allele=al
                )
            )
        return ''.join(allele_elem_list)


class VCFRecord_TabularReport_Converter (VCFRecord_Report_Converter):
    """Convert VCF records to custom tabular format."""
        
    def __init__ (self, vcf_info, link_formatter=None, samples=None):
        super().__init__(vcf_info, link_formatter, samples)
        self.header = (
            'Chromosome\t'
            'Position\t'
            'Affected Gene\t'
            'Transcript\t'
            'Effects'
            )
        if self.samples:
            sample_specs = '\t'.join(
                'genotype {0}\t'
                'observed allele counts {0}\t'
                'genotype quality {0}'
                .format(sn)
                for sn in self.samples
                )
            self.header += '\t' + sample_specs
        self.footer = None
        self.templates = {
            'row_template':
                '{location}\t'
                '{gene}\t'
                '{transcript}\t'
                '{effects}\t'
                '{sample_specs}',
            'location_template':
                '{chromosome}\t{position}',
            'hyperlinked_location_template':
                '<a href={location_url}>{chromosome}: {position}</a>',
            'sample_specs_template':
                '{gt_items}',
            'gene_template':
                '{gene}',
            'transcript_template':
                '{transcript}',
            'hyperlinked_transcript_template':
                '<a href={transcript_url}>{transcript}</a>',
            'effects_template':
                '{effect_items}',
            'effect_items_template':
                '{allele}: {effect}',
            'gt_items_template':
                '{gt}\t{dpr}\t{gq}'
            }

    def format_effects (self, effects, **kwargs):
        return self.templates['effects_template'].format(
            effect_items='; '.join(effects)
            )


def open_report (oformat, ofile, *args, **kwargs):
    if oformat == 'html':
        return RecordBasedFormatWriter(
            sys.stdout if ofile is None else open(
                ofile, 'w', encoding='utf-8'
                ),
            converter = VCFRecord_HTMLReport_Converter(
                *args, **kwargs
                )
            )
    elif oformat == 'text':
        return RecordBasedFormatWriter(
            sys.stdout if ofile is None else open(
                ofile, 'w', encoding=DEFAULTENCODING
                ),
            converter = VCFRecord_TabularReport_Converter(
                *args, **kwargs
                )
            )
    else:
        raise ArgumentParseError(
            'Invalid output format "{0}". Expected "html" or "text".',
            oformat
            )


def report (
    inputfile,
    species = None, ofile = None, oformat = 'html', link_formatter = None
    ):
    """Pretty-print the variants in the VCF input.

    The report can be enriched with hyperlinks to genome browser and
    organism-specific database views if oformat is set to html and a
    species is declared or can be detected from the VCF header.
    """

    with pyvcf.open(inputfile) as vcf_to_report:
        if oformat == 'html':
            if species:
                user_defined_species = True
            else:
                user_defined_species = False            

                # If no organism species is specified, try to parse it
                # from the VCF header (assuming the VCF file was generated by
                # the annotate function, this will succeed)
                # SnpEff's config file (replacing underscore in the SnpEff
                # species name with spaces).
                try:
                    species = vcf_to_report.info.meta['annotation_info']['EFF']['species']
                except KeyError:
                    pass
                
            if link_formatter:
                if not species:
                    raise ArgumentParseError(
                        'Need a species name to use with the link formatter file.'
                        )
                try:
                    link_formatter = link_formatter[species]
                except KeyError:
                    raise ArgumentValidationError(
                        'Species "{0}" not found in formatter file.', species
                        )
            elif species:
                # See if the species (user-provided or figured out from the VCF
                # header) is in the default dictionary, in which case we can
                # get built-in link formatting instructions.
                # If the default lookup fails and the user provided the species
                # explicitly, we want to raise an error reporting that fact.
                # If the species was obtained from the VCF header, we ignore the
                # failure silently because most likely the user is aware of the
                # missing formatting instructions, but wants SnpEff-annotated
                # html output still.
                species_id = anno_weblinks.species_synonyms.get(species)
                if species_id:
                    link_formatter = anno_weblinks.links[species_id]
                elif user_defined_species:
                    raise ArgumentValidationError(
                        'Unknown species "{0}". '
                        'Not found in default lookup table.',
                        species
                        )
        elif oformat == 'text':
            # we don't want to write hyperlinks in text format
            link_formatter = None

        with open_report(
            oformat, ofile, vcf_to_report.info, link_formatter
            ) as report_writer:
            for variant in vcf_to_report:
                report_writer.write(variant)


SnpEff_Effect = namedtuple('SnpEff_Effect',
                           ['verbatim',
                            'efftype', 'impact', 'func_class',
                            'codon_change', 'aa_change',
                            'aa_len', 'gene_name',
                            'transcript_biotype',
                            'gene_coding', 'transcript_id',
                            'exon', 'allele',
                            'errors', 'warnings'])


def snpeff_effects (vcf_entry):
    """Read out the Eff tag added to the INFO field by SnpEff as a namedtuple."""
    
    if 'EFF' in vcf_entry.info:
        effects = [eff.strip() for eff in vcf_entry.info['EFF'].split(',')]
        for effect in effects:
            try:
                eff_type, details = effect.rstrip(')').split('(')
            except:
                raise
            eff_details = [d.split(':')[-1] for d in details.split('|')]
            l = len(eff_details)
            if not 11 <= l <= 13:
                raise RuntimeError(
                    'Mal-formatted EFF entry in vcf INFO field: {0}'
                    .format(effect)
                    )
            if l < 13: #no errors, no warnings
                for i in range(13-l):
                    eff_details.append(None)
            if eff_details[10].isdigit():
                # SnpEff v3 reports variant alleles by number,
                # instead of as actual bases.
                # Since the old behaviour is the documented one,
                # it is uncertain what future versions will do.
                # Here, when we find a number instead of a base, we simply
                # convert it to the correspnding alt allele.
                eff_details[10] = vcf_entry.alt_from_num(int(eff_details[10]))
            yield SnpEff_Effect(effect, eff_type, *eff_details)
    else:
        yield SnpEff_Effect(*['']*13, errors=None, warnings=None)


class EffectsCatalogue (object):
    """Catalogue of effects of a single variant"""
    
    def __init__ (self):
        self.effects = OrderedDict()
        self._total_transcripts_affected = 0

    @classmethod
    def from_VCFRecord (cls, record):
        effects = cls()
        for eff in snpeff_effects(record):
            effects.add_effect(eff)
        return effects

    def n_genes_affected (self):
        return len(self.effects)

    def n_transcripts_affected (self, gene=None):
        if gene is None:
            return self._total_transcripts_affected
        else:
            return len(self.effects[gene])        
        
    def add_effect (self, eff):
        if eff.gene_name not in self.effects:
            self.effects[eff.gene_name] = OrderedDict()
        if eff.transcript_id not in self.effects[eff.gene_name]:
            self.effects[eff.gene_name][eff.transcript_id] = []
            self._total_transcripts_affected += 1
        self.effects[eff.gene_name][eff.transcript_id].append(
            (eff.allele, eff.efftype, eff.impact)
            )


def snpeff (genome, inputfile = '-', ofile = None,
            codon_tables = None, snpeff_path = None,
            memory = None, verbose = False, quiet = True, **optionals):
    """Wrapper around SnpEff.

    Provides a functional interface for subprocess calls of the form:
    java -Xmx<i>g -jar snpEff.jar [options] genome-version variants-file.

    Arguments:
    genome (required): the reference genome version;

    inputfile: path to the input VCF file; '-' (the default) means stdin
    outputfile: path to outputfile; default: stdout
    snpeff_path: path of the SnpEff installation directory;
                 default: config.snpeff_dir
    memory: max GB of memory to be used; default: config.max_memory

    Additional optional arguments that, if provided, will be passed through to
    SnpEff (see the option_table and bool_table dictionaries):
    no_downstream: if True, do not show downstream changes
    no_upstream: if True, do not show upstream changes
    no_intron: if True, do not show intron changes
    ud: set upstream downstream interval length
    stats: write a summary of results to the indicated file;
           if not provided, -noStats gets passed to SnpEff instead
    v: if True, show messages and errors if True

    Some SnpEff settings currently not modifiable through the interface:
      -o vcf: output format is always vcf
      -t (multithreading) is always switched off
    """
    
    # SnpEff installation queries:
    # set snpEff config file, check genome file and extract organism name
    if snpeff_path is None:
        snpeff_path = config.snpeff_dir
    snpeff_jar = os.path.join(snpeff_path, 'snpEff.jar')
    if not is_installed_snpeff_genome(genome, snpeff_path):
        raise ArgumentValidationError(
            '{0} is not the name of an installed SnpEff genome.'.format(genome)
            )
    config_file = get_snpeff_config_file(snpeff_path)
    species = get_organism_from_snpeff_genome(genome, snpeff_path)
    taxon_id = anno_weblinks.species_synonyms.get(species)
    
    # adjust the memory parameter
    memory = '-Xmx{0}g'.format(memory or config.max_memory)
    
    # sanitize and process optional parameters
    option_table = {
        'stats': '-stats',
        'ud': '-ud'
        }

    bool_table = {
        'no_downstream': '-no-downstream',
        'no_upstream': '-no-upstream',
        'no_intron': '-no-intron',
        'no_intergenic': '-no-intergenic',
        'no_utr': '-no-utr',
        }
    for opt in optionals:
        if opt not in option_table and opt not in bool_table:
            raise ArgumentParseError(
                'Unknown option {0}', opt
                )

    # turn optional non-boolean parameters into SnpEff command line arguments
    options = []
    for option, option_trans in option_table.items():
        if option in optionals:
            options += [option_trans, str(optionals[option])]
    # always ask for VCF output
    options += ['-o', 'vcf']

    # turn boolean options into SnpEff command line switches
    switches = [
        switch_trans for switch, switch_trans in bool_table.items()
        if optionals.get(switch)
        ]
    if 'stats' not in optionals:
        switches.append('-noStats')
    # always disable SnpEff call home behavior
    switches.append('-noLog')

    snpeff_installation_details = get_snpeff_installation_details(snpeff_jar)
    if snpeff_installation_details.formateff_support:
        # -formatEff seems to be available
        # add it to switches
        switches.append('-formatEff')

    if not quiet:
        # Unless the user asks to ignore wrapped application output explicitly
        # we run SnpEff in verbose mode.
        # This is necessary because SnpEff v4 does not report annotation
        # errors and warnings otherwise.
        switches.append('-v')
    
    # from here onwards the rather complex IO handling
    # uses an ExitStack to clean up behind itself
    with ExitStack() as cleanup_stack:
        with ExitStack() as ifile_stack:
            if inputfile == '-':
                # We are going to read from stdin, but since we are expecting
                # VCF format, we enforce the pyvcf default encoding 
                instream = encoding_base.get_custom_std(
                    sys.stdin,
                    encoding=pyvcf.defaultencoding,
                    errors=pyvcf.handle_decoding_errors
                    )
            else:
                instream = ifile_stack.enter_context(
                    open(inputfile, encoding=pyvcf.defaultencoding)
                    )
            instream_header = pyvcf.VCFReader(instream).info

            if codon_tables:
                # Support for on-the-fly codon table handling:
                # if the function got called with a codon table,
                # we create a temporary copy of the SnpEff config file,
                # in which we declare the user-specified table usage.
                default_codontable = None
                default_codontable_contigs = []
                if '' in codon_tables:
                    default_codontable = codon_tables.pop('')
                    if not snpeff_installation_details.genome_codonTable_support:
                        # The installed version of SnpEff does not understand
                        # genome-wide codon table declarations.
                        # We need to extract the contig names from the VCF to
                        # declare their codon table usage explicitly.
                        # If the information cannot be found in the VCF header,
                        # then there is no solution, but to abort with an
                        # informative error message.
                        if instream_header.contigs:
                            # The VCF header declares contig names.
                            # We record those for which no contig-specific
                            # codon table usage got specified.
                            default_codontable_contigs = [
                                c.name for c in instream_header.contigs
                                if c.name not in codon_tables
                                ]
                        else:
                            raise ArgumentValidationError(
                                'Cannot apply genome-wide codon table "{0}".\n'
                                'The VCF input does not declare '
                                'chromosome/contig names in its header. '
                                'Such input can be combined with a '
                                'genome-wide codon table only when using '
                                'SnpEff version 4.2 or higher (detected '
                                'version: {1}).'
                                .format(
                                    default_codontable,
                                    '.'.join(
                                        str(part) for part in
                                        snpeff_installation_details.version
                                        )
                                    )
                                )
                with open(config_file) as cfg_original:
                    with tmpfiles.NamedTemporaryMiModDFile(
                        mode= 'w',
                        prefix='snpeff',
                        suffix='.config',
                        delete=False
                    ) as cfg_tmp:
                        cleanup_stack.callback(
                            tmpfiles.remove_temporary_file, cfg_tmp.name
                            )
                        for line in cfg_original:
                            # rewrite the data_dir config setting as an
                            # absolute path so that it will work from the
                            # temporary file location
                            if line.startswith('data_dir') or line.startswith(
                                'data.dir'
                                ):
                                cfg_tmp.write(
                                    '{0} = {1}\n'.format(
                                        line.split('=')[0].strip(),
                                        get_snpeff_data_dir()
                                        )
                                    )
                                break
                            else:
                                cfg_tmp.write(line)
                        for line in cfg_original:
                            cfg_tmp.write(line)
                        # write the codon table declarations
                        if default_codontable:
                            if default_codontable_contigs:
                                for chrom in default_codontable_contigs:
                                    cfg_tmp.write(
                                        '{0}.{1}.codonTable: {2}\n'
                                        .format(
                                            genome,
                                            chrom,
                                            default_codontable
                                            )
                                        )
                            else:
                                cfg_tmp.write(
                                    '{0}.codonTable: {1}\n'
                                    .format(genome, default_codontable)
                                    )
                        for chrom, table in sorted(codon_tables.items()):
                            cfg_tmp.write(
                                '{0}.{1}.codonTable: {2}\n'
                                .format(genome, chrom, table)
                            )
                # use our temporary copy of the config file in the subsequent
                # SnpEff call
                options += ['-c', cfg_tmp.name]
            else:
                # just use the original config file when calling SnpEff
                options += ['-c', config_file]
                
            # Now build a SnpEff call of the form:
            # java -Xmx<i>g -jar snpEff.jar [switches] [options] genome file
            snpeff_call = [
                'java', memory, '-jar', snpeff_jar
                ] + switches + options + [genome, inputfile]

            if verbose:
                print ('Calling SnpEff with')
                print (' '.join(snpeff_call))

            if ofile:
                stdout_pipe = cleanup_stack.enter_context(
                    open(ofile, 'w', encoding=pyvcf.defaultencoding)
                    )
            else:
                stdout_pipe = sys.stdout
            if inputfile == '-':
                # If we are getting our input from stdin, then we have consumed
                # the header part of it by wrapping it in a pyvcf.VCFReader
                # above. Hence, we need to pipe the complete data to the
                # SnpEff subprocess.
                # Since we also need to read stdout of the subprocess while
                # it's getting generated, we need to fill the input pipe from
                # a separate thread.
                
                def enqueue_vcf (vcf_stream, obuffer, header):
                    # stdin of the subprocess will be binary, but we are
                    # receiving strings. The simplest solution is to wrap the
                    # binary buffer into a TextIOWrapper that handles the
                    # encoding to bytes for us.
                    outstream = io.TextIOWrapper(
                        obuffer,
                        encoding=pyvcf.defaultencoding,
                        line_buffering=True
                        )
                    outstream.write(str(header) + '\n')
                    shutil.copyfileobj(vcf_stream, outstream)
                
                proc = ExternalApplicationCall(args=snpeff_call,
                                               stdin=subprocess.PIPE,
                                               stdout=subprocess.PIPE,
                                               stderr=subprocess.PIPE)
                proc.start()
                cleanup_stack.callback(
                    handle_snpeff_process_stderr, proc, verbose, quiet
                    )
                feeder = Thread(
                    target=enqueue_vcf,
                    args=(instream, proc.Popen.stdin, instream_header)
                    )
                feeder.daemon = True
                feeder.start()
                # We need to keep instream open until it's content has been
                # passed to snpEff
                cleanup_stack.push(instream)
                ifile_stack.pop_all()
            else:
                # With a regular file we can just close our current handle to
                # it and let the SnpEff subprocess open it again.
                instream.close()
                ifile_stack.pop_all()
                proc = ExternalApplicationCall(args=snpeff_call,
                                               stdin=subprocess.PIPE,
                                               stdout=subprocess.PIPE,
                                               stderr=subprocess.PIPE)
                proc.start()
                cleanup_stack.callback(
                    handle_snpeff_process_stderr, proc, verbose, quiet
                    )

        # access SnpEff's output as it gets generated
        # We can use UTF-8 to decode the binary output stream
        # since it should represent VCF format and that is UTF-8-encoded
        # by its specs.
        snpeff_stdout = io.TextIOWrapper(
            proc.Popen.stdout,
            encoding=pyvcf.defaultencoding,
            errors=pyvcf.handle_decoding_errors,
            line_buffering=True
            )
        # Wrapping the stream into a VCFReader gives us a straightforward way
        # to access the header lines in a preparsed format via the wrapper's
        # info.meta attribute, which is an OrderedDict of key: value pairs
        # defined in the header.
        # We manipulate this structure on the fly to insert our tool-specific
        # metadata instead of the one produced by SnpEff before writing
        # everything to the target file or to stdout.
        try:
            snpeff_header = pyvcf.VCFReader(snpeff_stdout).info
        except FormatParseError:
            raise FormatParseError(
                'Hmm, the output of SnpEff does not seem to be valid VCF.'
                )
        if 'SnpEffCmd' in snpeff_header.meta:
            del snpeff_header.meta['SnpEffCmd']
        if 'SnpEffVersion' in snpeff_header.meta:
            snpeff_version_string = snpeff_header.meta['SnpEffVersion'][0]
            del snpeff_header.meta['SnpEffVersion']
        snpeff_header.meta['annotation_info'] = OrderedDict()
        snpeff_header.meta['annotation_info']['EFF'] = OrderedDict([
            ('tool', pyvcf.EscapedMetaString('SnpEff')),
            ('tool_version', snpeff_version_string),
            ('source', pyvcf.EscapedMetaString(genome)),
            ('species', pyvcf.EscapedMetaString(species)),
            ])
        if taxon_id is not None:
            snpeff_header.meta['annotation_info']['EFF'][
                'taxon_id'] = pyvcf.EscapedMetaString(taxon_id)
        snpeff_header.meta['annotation_command']=[
            ' '.join(shlex.quote(arg) for arg in snpeff_call)
            ]
        # header manipulation complete, so lets write out everything
        stdout_pipe.write(str(snpeff_header) + '\n')
        for line in snpeff_stdout:
            stdout_pipe.write(line)


def handle_snpeff_process_stderr (snpeff_proc, verbose, quiet):
    if snpeff_proc.wait():
        err = []
        for line in snpeff_proc.run_info.errors.split('\n'):
            if line.startswith('snpEff version'):
                break
            err.append(line)
        raise RuntimeError(
            'snpEff failed with the following error:\n{0}'
            .format('\n'.join(err))
            )
    if snpeff_proc.run_info.errors and not quiet:
        # redirect warnings to stdout
        if verbose:
            print ('Stderr output from snpEff:')
        print (snpeff_proc.run_info.errors)


def get_snpeff_config_file (snpeff_path = None):
    if snpeff_path is None:
        snpeff_path = config.snpeff_dir
    config_file = os.path.join(
        os.path.expanduser(snpeff_path), 'snpEff.config'
        )
    if not os.path.isfile(config_file):
        raise DependencyError(
            'Could not get snpEff config file. '
            'Check the SNPEFF_PATH variable in the MiModD '
            'configuration settings.'
            )
    return config_file


def get_snpeff_data_dir (snpeff_path = None):
    if snpeff_path is None:
        snpeff_path = config.snpeff_dir    
    config_file = get_snpeff_config_file(snpeff_path)
    with open(config_file, encoding=DEFAULTENCODING) as ifo:
        for line in ifo:
            if line.startswith('data_dir') or line.startswith('data.dir'):
                data_dir = line.split('=')[-1].strip()
                data_dir = os.path.normpath(os.path.join(os.path.expanduser(snpeff_path), os.path.expanduser(data_dir)))
                if not os.path.isdir(data_dir):
                    raise DependencyError(
                        'Could not find snpEff data directory at location {0} '
                        'specified in snpEff config file.'
                        .format(data_dir)
                        )
                return data_dir
        raise DependencyError(
            'snpEff config file at {0} does not specify a data directory.'
            .format(config_file)
            )


def get_snpeff_config_genomes (snpeff_path = None):
    config_file = get_snpeff_config_file(snpeff_path)
    with open(config_file, encoding=DEFAULTENCODING) as ifo:
        for line in ifo:
            if not line.startswith('#'):
                fields = [e.strip() for e in line.split(':')]
                if len(fields) == 2 and fields[0].endswith('.genome'):
                    yield fields[0][:-len('.genome')], fields[1]


def is_installed_snpeff_genome (query_genome, snpeff_path = None):
    if query_genome in (genome
                        for genome, organism in
                        get_snpeff_config_genomes(snpeff_path)
                        ) and os.path.isfile(
                            os.path.join(get_snpeff_data_dir(snpeff_path),
                                         query_genome,
                                         'snpEffectPredictor.bin')):
        return True
    return False


def get_organism_from_snpeff_genome (query_genome, snpeff_path = None):
    for genome, organism in get_snpeff_config_genomes(snpeff_path):
        if genome == query_genome:
            return organism.replace('_', ' ')
    raise KeyError(
        'Genome file {0} not found among the registered SnpEff genomes'
        .format(query_genome)
        )

        
def get_installed_snpeff_genomes (output = None, snpeff_path = None):
    if output:
        file = open(output, 'w', encoding=DEFAULTENCODING)
    else:
        file = encoding_base.get_custom_std(sys.stdout)
        
    snpeff_data_dir = get_snpeff_data_dir (snpeff_path)
    for genome, organism in get_snpeff_config_genomes(snpeff_path):
        if os.path.isfile(os.path.join(snpeff_data_dir, genome, 'snpEffectPredictor.bin')):
            print ('{0}: {1}\t{1}'.format(organism, genome), file = file)
    if file is not sys.stdout:
        file.close()


def get_snpeff_installation_details (snpeff_jar):
    # should return a NamedTuple of:
    # version number,
    # supports_formatEff,
    # supports_genome_codonTable

    version = get_snpeff_version(snpeff_jar)
    return namedtuple(
        'SnpEffInstallationDetails',
        ['version', 'formateff_support', 'genome_codonTable_support']
        )(
            version,
            snpeff_supports_formateff(snpeff_jar),
            True if version >= (4, 2) else False
            )


def get_snpeff_version (snpeff_jar):
    version_call = ['java', '-jar', snpeff_jar, '-version', 'noLog']
    proc = ExternalApplicationCall(
        args=version_call, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
    returncode = proc.run()
    if not returncode:
        # This version of SnpEff has a version command.
        # We can parse its output directly.
        return parse_snpeff_version(proc.run_info.results.split())
    else:
        # The SnpEff version call failed, but it may be possible to
        # scrape the version from the stderr output.
        data = proc.run_info.errors.split('\n')
        line_token = 'snpEff version'
        for line in data:
            if line.startswith(line_token):
                return parse_snpeff_version(
                    line[len(line_token):].split()
                    )
    return None


def parse_snpeff_version (version_data):
    if version_data[0] == 'SnpEff' and len(version_data) > 1:
        version_string_components = version_data[1].split('.')
        if version_string_components[-1][-1].isalpha():
            version_string_components = version_string_components[:-1] + [
                version_string_components[-1][:-1],
                version_string_components[-1][-1]
                ]
        version = []
        for comp in version_string_components:
            try:
                version.append(int(comp))
            except ValueError:
                version.append(comp)
        return tuple(version)
    return None


def snpeff_supports_formateff (snpeff_jar):
    # see if we are running a new version of SnpEff (v4.1+)
    # that understands the '-formatEff' switch
    test_call = [
        'java', '-jar', snpeff_jar, '-formatEff',
        '-noLog',
        ]
    proc = ExternalApplicationCall(args=test_call,
                                   stderr=subprocess.PIPE)
    returncode = proc.run()
    # We always expect an error here, but
    # the question is: is it about the '-formateff' switch?
    # We have to look at the first line of the error message to find out.
    # in SnpEff 3.6 - 4.0 the first line should read:
    # Error        :    Unknow option '-formatEff'
    if not returncode:
        raise AssertionError(
            'This version of SnpEff seems to accept rudimentary test options.'
            )
    if "option '-formatEff'" in proc.run_info.errors.split('\n')[0]:
        return False
    else:
        return True

    
def parse_annotate_cl_args (**args):
    if 'codon_tables' in args:
        # Parse --codon-table argument list. Allowed formats for individual
        # items are:
        # TABLE, :TABLE, which both mean assign codon table TABLE to any
        # contig in the genome, for which no specific other table is given,
        # CHROM:TABLE, which assigns codon table TABLE to a specific contig.
        codon_tables = {}
        for table_spec in args['codon_tables']:
            chrom, sep, table = table_spec.rpartition(':')
            if not table:
                # The argument ends in, or is, a colon. Assuming that no SnpEff
                # codon table name ever matches this pattern this indicates an
                # error.
                raise ArgumentParseError(
                    'Failed to parse codon table specification: "{0}".\n'
                    'Allowed formats are CHROM:TABLE to use a codon table for '
                    'a specific chromosome, or TABLE to use a codon table for '
                    'all chromosomes that have no specific codon table '
                    'assigned to them.'
                    .format(table_spec)
                    )
            if chrom in codon_tables:
                # Naming the same contig or assigning a default codon table
                # twice is disallowed -> provide an appropriate error message.
                if chrom == '':
                    raise ArgumentParseError(
                        'You can only specify a single custom default codon '
                        'table through the codon-tables option. To specify '
                        'codon tables for individual chromosomes use the '
                        'format CHROM:TABLE.'
                        )
                else:
                    raise ArgumentParseError(
                        'Multiple codon tables specified for contig {0}.'
                        .format(chrom)
                        )
            # store the new contig -> codon table assignment
            codon_tables[chrom] = table
        args['codon_tables'] = codon_tables
    return args


def cl_annotate (**args):
    snpeff(**parse_annotate_cl_args(**args))
