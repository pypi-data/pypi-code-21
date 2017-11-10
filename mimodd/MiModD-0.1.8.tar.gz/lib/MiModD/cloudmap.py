import sys
import math

from decimal import Decimal
from collections import OrderedDict, Counter, namedtuple
from contextlib import ExitStack

from . import pyvcf, plotters, stats_base, converters, fasta
from . import (ArgumentParseError, ArgumentValidationError,
               FormatParseError, DependencyError)


SimpleInfo = namedtuple('SimpleInfo',
                        ['meta',
                         'header_fields'])

SimpleRecord = namedtuple('SimpleRecord',
                          ['chrom',
                           'pos',
                           'linkage_data']
                          )


class BinnedCounts (dict):
    def __init__ (self, bins, contigs):
        self.contigs = contigs
        for xbase in bins:
            # Initialize bin counters and
            # prepopulate each marker bin with one pseudocount
            # to avoid division-by-zero errors and
            # skipping of empty bins when calculating
            # histogram data.
            self[xbase] = {contig: {'markers': Counter(
                x for x in range(1, ctg_info['length']//xbase + 2)
                ),
                                    'non_segregating': Counter()
                                    }
                           for contig, ctg_info in contigs.items()
                           }
        
    def get_markers_per_contig (self, contig):
        this_base = next(iter(self))
        # do not forget to subtract one pseudocount per bin
        return (sum(self[this_base][contig]['markers'].values())
                - len(self[this_base][contig]['markers']))
    
    def get_histogram_bins (self, xbase):
        hdata = OrderedDict()
        for contig in self.contigs:
            raw_counts = self[xbase][contig]
            # Throughout the method, we iterate over the keys in 'markers'.
            # Some of these may be missing in 'non_segregating', but since
            # we are dealing with Counters, we can still access them directly.
            if len(raw_counts['non_segregating']) > 0:
                mean_non_seg_count_on_contig = Decimal(
                    sum(raw_counts['non_segregating'].values())
                    ) / len(raw_counts['markers'])
                # In the following calculation the one pseudocount in each
                # marker bin is intentionally not subtracted to avoid
                # division by zero errors. Effectively, this shifts linkage
                # scores towards zero, with a larger effect on bins with only
                # few or less convincingly linked variants.
                hdata[contig] = {
                    bin: (Decimal(raw_counts['non_segregating'][bin])
                          / Decimal(raw_counts['markers'][bin]
                                    - raw_counts['non_segregating'][bin])
                          ) * mean_non_seg_count_on_contig
                    for bin in raw_counts['markers']
                    }
            else:
                # shortcut that also avoids accidental division-by-zero
                # if no non-segregating variants exist
                hdata[contig] = {bin: 0 for bin in raw_counts['markers']}
        return hdata

    def get_histogram_series (self):
        hdata = OrderedDict((contig, {}) for contig in self.contigs)
        for contig in self.contigs:
            hdata[contig]['markers'] = self.get_markers_per_contig(contig)
            hdata[contig]['data'] = {}
        for xbase in self:
            data = self.get_histogram_bins(xbase)
            series_sum = 0
            for contig, data_series in data.items():
                series_sum += sum(data_series.values())
                hdata[contig]['data'][xbase] = data_series
            # normalize bins to add up to 1 across all contigs
            if series_sum > 0:
                for contig, data_series in data.items():
                    for bin in hdata[contig]['data'][xbase]:
                        hdata[contig]['data'][xbase][bin] /= series_sum
        return hdata

    def get_markers_per_bin (self, xbase):
        hdata = OrderedDict()
        for contig in self.contigs:
            # remember to subtract the one pseudocount from the markers
            scaling = Decimal(max(self)) / xbase
            hdata[contig] = {bin: (counts - 1) * scaling 
                             for bin, counts in
                             self[xbase][contig]['markers'].items()}
        return hdata
    
    def get_marker_series (self):
        hdata = OrderedDict((contig, {}) for contig in self.contigs)
        for contig in self.contigs:
            hdata[contig]['markers'] = self.get_markers_per_contig(contig)
            hdata[contig]['data'] = {}
        for xbase in self:
            data = self.get_markers_per_bin(xbase)
            series_sum = 0
            for contig, data_series in data.items():
                series_sum += sum(data_series.values())
                hdata[contig]['data'][xbase] = data_series
            # normalize bins to add up to 1 across all contigs
            if series_sum > 0:
                for contig, data_series in data.items():
                    for bin in hdata[contig]['data'][xbase]:
                        hdata[contig]['data'][xbase][bin] /= series_sum
        return hdata


class LinkageData (object):
    def __init__ (self, contig):
        self.contig = contig
        self.pos = []
        self.scores = []
        self.weights = []
        self.values = []

    def append (self, pos, score, weight = 1, values = []):
        self.pos.append(pos)
        self.scores.append(score)
        self.weights.append(weight)
        if self.values:
            if len(values) != len(self.values):
                raise ValueError(
                    'Need same number of values during consecutive appends'
                    )
            for i, v in enumerate(values):
                self.values[i].append(v)
        else:
            self.values = [[v] for v in values]

    def pos_scores (self):
        yield from zip(self.pos, self.scores, self.weights)

    def pos_values (self, index):
        yield from zip(self.pos, self.values[index])

    def iter_value_series (self):
        for i, _ in enumerate(self.values):
            yield self.pos_values(i)


# +++++++++++ A class hierarchy of Linkage Scorers ++++++++++++
#
# Linkage Scorers provide weighed linkage scores based on the allele
# composition at individual base positions.
# The base class, AlleleBasedLinkageScorer, is an abstract class.
# The concrete subclasses derived from it are used by the corresponding
# Linkage Analyzers to provide individual data points for linkage analyses.

class AlleleBasedLinkageScorer (object):
    def __init__ (self, vcfreader, samples = None):
        self.reader = vcfreader
        self.samples_to_report = samples
        
    def __iter__ (self):
        for record in self.reader:
            ld_info = self.calculate_ld_info(record)
            if ld_info:
                record.linkage_data = ld_info
                yield record.sample_slice(self.samples_to_report)

    def calculate_ld_info (self, record):
        raise NotImplementedError

    
class ContrastScorer (AlleleBasedLinkageScorer):
    def __init__ (self, vcfreader, sample_1, sample_2):
        super().__init__(vcfreader, [sample_1, sample_2])
        self.sample_1 = sample_1
        self.sample_2 = sample_2
        # precalculate constant part of the correction factor used
        # in the per-site information content calculation performed by
        # the calculate_ld_info method of this Scorer.
        self.cf = 3/(2*math.log(2))

    def calculate_ld_info (self, record):
        # parse the DPR field of the two samples
        dpr_counts_1 = [
            int(count) for count in
            record.sampleinfo['DPR'][self.sample_1]
              .split(',')
            ]
        total_counts_1 = sum(dpr_counts_1)
        dpr_counts_2 = [
            int(count) for count in
            record.sampleinfo['DPR'][self.sample_2]
              .split(',')
            ]
        total_counts_2 = sum(dpr_counts_2)
        if total_counts_1 > 0 and total_counts_2 > 0:
            # Calculate a) the sum of the frequency differences
            # between the two samples for every nucleotide
            # and b) an information score for each sample
            # at the site. For the information score we use the
            # information content formula from:
            # Schneider and Stormo (1986), J Mol Biol 188
            # doi:10.1016/0022-2836(86)90165-8.
            # The information score of the contrast sample is calculated as
            # 2 - bit score. The purpose of this is to keep data points of the
            # two samples separate when plotted together.
            linkage_score = 0
            info_score_1 = 2 - self.cf/total_counts_1
            info_score_2 = self.cf/total_counts_2
            for nuc_count_1, nuc_count_2 in zip(dpr_counts_1, dpr_counts_2):
                freq_1 = nuc_count_1 / total_counts_1
                freq_2 = nuc_count_2 / total_counts_2
                linkage_score += abs(freq_1 - freq_2)
                if freq_1 > 0:
                    info_score_1 += freq_1 * math.log(freq_1, 2)
                if freq_2 > 0:
                    info_score_2 -= freq_2 * math.log(freq_2, 2)
            # The above sum of absolute frequency differences, effectively
            # counts differences twice so, for the final linkage score, we
            # correct this.
            # We report cubic linkage scores in analogy to the Frequency Mapper
            # algorithm, but there is no solid justification for this other than
            # that it keeps peak sizes in different mapping modes comparable.
            linkage_score = (linkage_score/2)**3
            linkage_weight = (total_counts_1 + total_counts_2)**0.5
            return [
                linkage_score,
                linkage_weight,
                [info_score_1, info_score_2]
        ]


class FrequencyScorer (AlleleBasedLinkageScorer):
    def __init__ (self, vcfreader, mapping_sample,
                  related_parent = None, unrelated_parent = None,
                  infer_missing_parent = False,
                  stats_bins = []):
        super().__init__(vcfreader, [mapping_sample])
        self.mapping_sample = mapping_sample
        self.related_parent = related_parent
        self.unrelated_parent = unrelated_parent
        self.infer_missing_parent = infer_missing_parent
        self.undef = '.' # string that indicates an unavailable genotype

    def calculate_ld_info (self, record):
        # parse the related and unrelated parent samples' GT field
        # would currently fail for phased data, where separator is '|'
        if self.related_parent:
            related_parent_gt_allele_nos = set(
                record.sampleinfo['GT'][self.related_parent].split('/')
                )
        else:
            related_parent_gt_allele_nos = {self.undef}
        if self.unrelated_parent:
            unrelated_parent_gt_allele_nos = set(
              record.sampleinfo['GT'][self.unrelated_parent].split('/')
              )
        else:
            unrelated_parent_gt_allele_nos = {self.undef}
        # include only sites where all parents
        # have a homozygous genotype call and where that call
        # is different for the parents if two are provided
        if len(related_parent_gt_allele_nos) == 1 and \
         len(unrelated_parent_gt_allele_nos) == 1 and \
         related_parent_gt_allele_nos != unrelated_parent_gt_allele_nos:
            # Get each parent's homozygous allele no
            # and convert it to an int.
            # An unavailable genotype ('./.') is converted to None
            # which has the same effect as an unavailable sample
            # but for only this position.
            related_gt_allele_no = related_parent_gt_allele_nos.pop()
            if related_gt_allele_no == self.undef:
                related_gt_allele_no = None
            else:
                related_gt_allele_no = int(related_gt_allele_no)
            unrelated_gt_allele_no = unrelated_parent_gt_allele_nos.pop()
            if unrelated_gt_allele_no == self.undef:
                unrelated_gt_allele_no = None
            else:
                unrelated_gt_allele_no = int(unrelated_gt_allele_no)
            # include a site only if at least one parent has a
            # non-reference (>0) genotype or if, with one parent,
            # infer_missing_parent is True
            if related_gt_allele_no or \
              unrelated_gt_allele_no or self.infer_missing_parent:
                # parse the DPR field of the mapping_sample
                dpr_counts = [
                    int(count) for count in
                    record.sampleinfo['DPR'][self.mapping_sample]
                      .split(',')
                    ]
                total_counts = sum(dpr_counts)
                # Calculate the AD field with respect to recombination
                # frequency (dip towards zero indicates close linkage).
                # For a sample trio (mapping sample, related and
                # unrelated parent), AD is:
                # "related parent's allele count,
                # unrelated parent's allele count".
                # For a pair of samples (mapping sample and related or
                # unrelated parent), the default is to assume a
                # homozygous REF genotype for the missing sample.
                # If infer_missing_parent is True, the missing
                # parent's allele count is the sum of all counts
                # except those of the other parent's genotype.
                if related_gt_allele_no is None:
                    if self.infer_missing_parent:
                        related_like_counts = total_counts - dpr_counts[unrelated_gt_allele_no]
                    else:
                        related_like_counts = dpr_counts[0]
                else:
                    related_like_counts = dpr_counts[related_gt_allele_no]
                if unrelated_gt_allele_no is None:
                    if self.infer_missing_parent:
                        unrelated_like_counts = total_counts - dpr_counts[related_gt_allele_no]
                    else:
                        unrelated_like_counts = dpr_counts[0]
                else:
                    unrelated_like_counts = dpr_counts[unrelated_gt_allele_no]

                informative_dp = related_like_counts + unrelated_like_counts
                if informative_dp > 0:
                    if related_like_counts > unrelated_like_counts:
                        # Unlike in the original algorithm used by CloudMap,
                        # we are not just counting totally non-segregating
                        # variants, but calculate a score for any variant with
                        # overrepresentation of the related parent allele.
                        # This score is calculated below as the cubic relative
                        # overrepresentation of the related parent allele.
                        # This is a purely empirical formula, which, at some
                        # point, we may want to replace with a statistical
                        # measure of linkage.
                        linkage_score = (
                            (related_like_counts-unrelated_like_counts)**3 /
                            informative_dp**3
                            )
                    else:
                        # Sites with overrepresentation of the unrelated parent
                        # allele get a linkage_score of zero. This is better
                        # than using a negative score with no clear experimental
                        # correlate. In other words, we assume that this kind of
                        # overrepresentation is an artefact of the upstream
                        # analysis.
                        linkage_score = 0

                    return [
                        linkage_score,
                        informative_dp ** 0.5,
                        [related_like_counts,
                         unrelated_like_counts,
                         total_counts]
                    ]
        

# +++++++++++ A class hierarchy of LinkageAnalyzers ++++++++++++
#
# The base class, LinkageAnalyzer, and the CMCompatibleLinkageAnalyzer class
# are abstract classes.
# The concrete subclasses derived from them support the different
# mapping modes of the package.

class LinkageAnalyzer (object):
    def __init__ (self, ifo, bin_sizes,
                  text_out = None, plot_file = None, plot_options = {}):
        if plot_file:
            if plot_options.get('no_hist') and plot_options.get('no_scatter'):
                raise ArgumentParseError(
                    'Conflicting plot settings. '
                    'A plot output file is specified, but both histogram '
                    'and scatter plotting are turned off '
                    'so there is nothing to plot.'
                    )
        elif plot_options:
            raise ArgumentParseError(
                'Any plot options require a specified plot output file.'
                )
        
        if isinstance(ifo, pyvcf.VCFReader):
            self.mapper = None
            self.remap = False
        elif isinstance(ifo, PerVariantFileReader):
            if text_out:
                raise ArgumentParseError(
                    'Additional per-variant site output ("-t" option) is not '
                    'supported when remapping from a per-variant report file.'
                    )
            self.mapper = ifo
            self.remap = True
        else:
            raise ArgumentValidationError(
                'The input for linkage analysis has to be in VCF or in '
                'per-variant report format.'
                )
        self.ifo = ifo
        self.contigs = ifo.info.meta['contig']
        if not self.contigs or any(
            'length' not in info for info in self.contigs.values()
            ):
            raise ArgumentValidationError(
                'Could not obtain the required contig information (names '
                'and lengths) from the input file. '
                'You may have to provide an additional CloudMap-style '
                'seqdict file.'
                )
        self.bin_sizes = bin_sizes
        self.binned_counts = BinnedCounts(self.bin_sizes, self.contigs)
        self.kde_binned_counts = BinnedCounts([10000], self.contigs)
        self.text_out = text_out
        self.plot_out = plot_file
        self.plot_options = plot_options

    def analyze (self):
        report_writer = self.get_report_writer()
        plothandle = self.initialize_plotter()
        if plothandle:
            self.configure_plotting(plothandle)
        result = self.report(report_writer, plothandle)
        if plothandle:
            plothandle.plotter.close()
        return result
            
    def get_report_writer (self):
        raise NotImplementedError

    def configure_plotting (self, plothandle):
        raise NotImplementedError

    def populate_bins (self, contig_linkage_data):
        contig = contig_linkage_data.contig
        for pos, score, weight in contig_linkage_data.pos_scores():
            for binner in [self.binned_counts, self.kde_binned_counts]:
                for xbase in binner:
                    this_bin = pos//xbase + 1
                    binner[xbase][contig]['markers'][this_bin] += weight
                    binner[xbase][contig]['non_segregating'
                                          ][this_bin] += score * weight

    def report (self, report_writer, plothandle):
        raise NotImplementedError

    def initialize_plotter (self):
        if self.plot_out:
            # set up the plotting device
            plotter = plotters.contig_plotter(
                self.plot_out,
                xlab='Location (Mb)',
                major_tick_unit=self.bin_sizes[0],
                xlim=max(info['length'] for info in self.contigs.values())
                     if not self.plot_options.get('fit_width')
                     else None
                )
            next(plotter) # prime the coroutine, now waiting for data to plot
            return plotters.PlotHandle(plotter)
        else:
            # no plots to be generated
            return None
        
    def linkage_reader (self, report_writer):
        linkage_data = LinkageData(None)
        while True:
            for record in self.mapper:
                if report_writer:
                    report_writer.write(record)
                if record.chrom != linkage_data.contig:
                    if linkage_data.contig is not None:
                        yield linkage_data
                    break
                linkage_data.append(record.pos, *record.linkage_data)
            else:
                # the mapper is exhausted
                # yield data for last contig, then return
                if linkage_data.contig is not None:
                    yield linkage_data
                return
            linkage_data = LinkageData(record.chrom)
            linkage_data.append(record.pos, *record.linkage_data)

    def verify_samples_exist (self, samples):
        for sample in samples:
            if sample and sample not in self.ifo.info.samples:
                raise ArgumentValidationError(
                    'Sample "{0}": no such sample name in the VCF file.',
                    sample
                    )


class CMCompatibleLinkageAnalyzer (LinkageAnalyzer):
    def __init__ (self, cloudmap_mode = False, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if cloudmap_mode:
            if not self.text_out:
                raise ArgumentParseError(
                    'CloudMap compatibility mode requires an additional '
                    'text output file specified through the "-t" option.'
                    )
            if self.remap:
                raise ArgumentParseError(
                    'CloudMap compatibility mode is not available '
                    'when remapping from a per-variant report file.'
                    )
        self.cloudmap_mode = cloudmap_mode


class VAFAnalyzer (CMCompatibleLinkageAnalyzer):
    def __init__ (self, mapping_sample,
                  related_parent = None, unrelated_parent = None,
                  infer_missing_parent = None,
                  *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not self.mapper:
            if not (related_parent or unrelated_parent):
                raise ArgumentParseError(
                    'At least one parent sample must be specified for '
                    'Variant Allele Frequency Mapping.'
                    )
            if related_parent and unrelated_parent and infer_missing_parent:
                raise ArgumentParseError(
                    '"infer_missing_parent" cannot be used with both parent '
                    'samples specified.'
                    )
            self.verify_samples_exist(
                [mapping_sample, related_parent, unrelated_parent]
                )

            self.mapper = FrequencyScorer(self.ifo, mapping_sample,
                                          related_parent, unrelated_parent,
                                          infer_missing_parent)
        else:
            if mapping_sample or related_parent or unrelated_parent:
                raise ArgumentParseError(
                    'Sample information cannot be used when replotting from '
                    'a per-variant report file.'
                    )

    def get_report_writer (self):
        if self.text_out:
            if self.cloudmap_mode:
                # In cloudmap_mode we want to write a CloudMap compatibility
                # file, which is, essentially, vcf.
                return pyvcf.VCFWriter(
                    self.text_out,
                    converter = VCFRecord_CloudMap_Converter(
                        self.ifo.info, self.mapper.mapping_sample
                        )
                    )
            # In standard mode, we write a simple TAB-separated format
            # with read counts and ratios.
            colnames = ['#Chr',
                        'Pos',
                        'LinkageScore',
                        'Weight',
                        'RelCounts',
                        'UnrelCounts',
                        'TotalCounts']
            return pyvcf.VCFWriter(
                self.text_out,
                converter=VCFRecord_VAFReport_Converter(self.contigs, colnames)
                )

    def configure_plotting (self, plothandle):
        if not self.plot_options.get('no_scatter'):
            plothandle.with_scatter = True
            plothandle.scatter_params = {
                'ylab': 'apparent rate of marker segregation',
                'loess_span': self.plot_options.get('loess_span', 0.1),
                'ylim': self.plot_options.get('ylim_scatter') or 1,
                'points_colors':
                    self.plot_options.get('points_colors') or ['black'],
                'loess_colors':
                    self.plot_options.get('loess_colors') or ['red'],
                'no_warnings': self.plot_options.get('no_warnings')
                }
        if self.plot_options.get('no_hist'):
            plothandle.with_hist = False

    def report (self, report_writer, plotter):
        for contig_linkage_data in self.linkage_reader(report_writer):
            self.populate_bins(contig_linkage_data)

            if plotter and plotter.with_scatter and contig_linkage_data:
                # Get a list of position/segregation rate pairs that
                # will be used as x,y coordinates in the scatterplot of the
                # data. Segregation rate is calculated as unrelated allele
                # count / total nucleotide count at each position. The raw
                # data necessary for this calculation is stored in the values
                # list of lists of the contig_linkage_data, at index positions
                # 1 and 2.
                ratios = [
                    (ld[0], ld[1]/ld[2])
                    for ld in
                    zip(contig_linkage_data.pos,
                        contig_linkage_data.values[1],
                        contig_linkage_data.values[2])
                    ]
                plot_data = stats_base.hexbin(ratios, 100000, 0.002).values()
                # These plots need both the hexbinned and the raw data
                # (the latter to calculate the Loess regression).
                # We pass in the second dataset through an additional plotting
                # parameter.
                plotter.scatter_params.update(title=contig_linkage_data.contig)
                plotter.scatter_params['raw_data'] = [ratios]
                plotter.plot_scatter([plot_data])
                
        # Now use the binned stats per contig obtained during the iteration
        # above to plot histograms.
        hdata = self.binned_counts.get_histogram_series()
        kde_data = self.kde_binned_counts.get_histogram_series()
        if plotter and plotter.with_hist:
            if not self.plot_options.get('ylim_hist'):
                # scale all histogram y-axes to the largest value overall
                max_observed_y = max(value
                                     for data in hdata.values()
                                     for series in data['data'].values()
                                     for value in series.values())
                self.plot_options['ylim_hist'] = plotters.pretty_round(
                    max_observed_y
                    )
            # plot histograms one per contig
            for contig, data in hdata.items():
                if hdata[contig]['markers'] > 0:
                    hist_params = {
                        'title': contig,
                        'ylim': self.plot_options['ylim_hist'],
                        'ylab': 'normalized linkage scores',
                        'hist_colors': self.plot_options.get('hist_colors'),
                        'lines_plot':
                            None
                            if self.plot_options.get('no_kde') else
                            kde_data[contig]['data']
                        }
                    plotter.plot_histogram(data['data'], hist_params)
        return hdata


class VACAnalyzer (LinkageAnalyzer):
    def __init__ (self, mapping_sample, contrast_sample, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if not self.mapper:
            if not mapping_sample:
                raise ArgumentParseError(
                    'The mapping sample must be specified in '
                    'Variant Allele Contrast Mapping.'
                    )
            if not contrast_sample:
                raise ArgumentParseError(
                    'A contrast sample must be provided for '
                    'Variant Allele Contrast Mapping.'
                    )
            self.verify_samples_exist([mapping_sample, contrast_sample])

            self.mapper = ContrastScorer(
                self.ifo, mapping_sample, contrast_sample
                )
        else:
            if mapping_sample or contrast_sample:
                raise ArgumentParseError(
                    'Sample information cannot be used when replotting from '
                    'a per-variant report file.'
                    )

    def get_report_writer (self):
        if self.text_out:
            # In standard mode, we write a simple TAB-separated format
            # with read counts and ratios.
            colnames = ['#Chr',
                        'Pos',
                        'LinkageScore',
                        'Weight',
                        'bits1',
                        '2-bits2']
            return pyvcf.VCFWriter(
                self.text_out,
                converter=VCFRecord_VAFReport_Converter(self.contigs, colnames)
                )

    def configure_plotting (self, plothandle):
        if not self.plot_options.get('no_scatter'):
            plothandle.with_scatter = True
            plothandle.scatter_params = {
                'ylab': 'information content / bits',
                'loess_span': self.plot_options.get('loess_span', 0.1),
                'ylim': self.plot_options.get('ylim_scatter') or 2,
                'points_colors':
                    self.plot_options.get('points_colors') or ['orange',
                                                               'dodgerblue3'],
                'loess_colors':
                    self.plot_options.get('loess_colors') or ['red', 'black'],
                'no_warnings': self.plot_options.get('no_warnings')
                }
        if self.plot_options.get('no_hist'):
            plothandle.with_hist = False

    def report (self, report_writer, plotter):
        for contig_linkage_data in self.linkage_reader(report_writer):
            self.populate_bins(contig_linkage_data)
            
            if plotter and plotter.with_scatter:
                raw_ratio_data = [
                    list(ratios)
                    for ratios in contig_linkage_data.iter_value_series()
                    ]
                plot_data = [
                    stats_base.hexbin(ratios, 100000, 0.002).values()
                    for ratios in raw_ratio_data
                    ]
                # These plots need both the hexbinned and the raw data
                # (the latter to calculate the Loess regression).
                # We pass in the second dataset through an additional plotting
                # parameter.
                plotter.scatter_params.update(title=contig_linkage_data.contig)
                plotter.scatter_params['raw_data'] = raw_ratio_data
                plotter.plot_scatter(plot_data)
                
        # Now use the binned stats per contig obtained during the iteration
        # above to plot histograms.
        hdata = self.binned_counts.get_histogram_series()
        kde_data = self.kde_binned_counts.get_histogram_series()
        if plotter and plotter.with_hist:
            if not self.plot_options.get('ylim_hist'):
                # scale all histogram y-axes to the largest value overall
                max_observed_y = max(value
                                     for data in hdata.values()
                                     for series in data['data'].values()
                                     for value in series.values())
                self.plot_options['ylim_hist'] = plotters.pretty_round(
                    max_observed_y
                    )
            # plot histograms one per contig
            for contig, data in hdata.items():
                if hdata[contig]['markers'] > 0:
                    hist_params = {
                        'title': contig,
                        'ylim': self.plot_options['ylim_hist'],
                        'ylab': 'normalized linkage scores',
                        'hist_colors': self.plot_options.get('hist_colors'),
                        'lines_plot':
                            None
                            if self.plot_options.get('no_kde') else
                            kde_data[contig]['data']
                        }
                    plotter.plot_histogram(data['data'], hist_params)
        return hdata


class SVDAnalyzer (CMCompatibleLinkageAnalyzer):
    def __init__ (self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.plot_out and self.plot_options.get('no_hist'):
            raise ArgumentParseError(
                'Conflicting plot settings. A plot output file is specified, '
                'but histogram plotting is turned off and there is nothing '
                'else to plot in SVD mode.'
                )

        # in current 'SVD' mode, we simply strip collect every variant
        # found in the input file
        def svd_parser (ifo):
            # mock something to fit in our framework!
            # ugly, but works
            for record in ifo:
                record.linkage_data = [1, 1, []]
                yield record
                
        if not self.mapper:
            self.mapper = svd_parser(self.ifo)


    def get_report_writer (self):
        if self.text_out:
            if self.cloudmap_mode:
                # In cloudmap_mode we want to write a CloudMap compatibility
                # file, which is, essentially, vcf.
                # Note: When no sample name is given, the RecordWriter
                # automatically discards all sample-specific information.
                return pyvcf.VCFWriter(
                    self.text_out,
                    converter=VCFRecord_CloudMap_Converter(self.ifo.info)
                    )
            # In standard mode, we write a simple TAB-separated
            # 2-column format.
            colnames = ['#Chr',
                        'Pos']

            return pyvcf.VCFWriter(
                self.text_out,
                converter=VCFRecord_SVDReport_Converter(self.contigs, colnames)
                )
        
    def configure_plotting (self, plothandle):
        if self.plot_options.get('no_hist'):
            plothandle.with_hist = False

    def report (self, report_writer, plotter):
        for contig_linkage_data in self.linkage_reader(report_writer):
            self.populate_bins(contig_linkage_data)

        for contig_linkage_data in self.linkage_reader(report_writer):
            contig = contig_linkage_data.contig
            for pos, score, weight in contig_linkage_data.pos_scores():
                for binner in [self.binned_counts, self.kde_binned_counts]:
                    for xbase in binner:
                        this_bin = pos//xbase + 1
                        binner[xbase][contig]['markers'][this_bin] += weight
                        binner[xbase][contig]['non_segregating'
                                              ][this_bin] += score * weight


        # treat binned counts
        hdata = self.binned_counts.get_marker_series()
        kde_data = self.kde_binned_counts.get_marker_series()
        if plotter and plotter.with_hist:
            if not self.plot_options.get('ylim_hist'):
                # scale all histogram y-axes to the largest value overall
                max_observed_y = max(value
                                     for data in hdata.values()
                                     for series in data['data'].values()
                                     for value in series.values())
                self.plot_options['ylim_hist'] = plotters.pretty_round(
                    max_observed_y
                    )
            # plot histograms one per contig
            for contig, data in hdata.items():
                plotter.plot_histogram(
                    data['data'],
                    {'title': contig,
                     'ylim': self.plot_options['ylim_hist'],
                     'ylab': 'normalized variant density',
                     'hist_colors': self.plot_options.get('hist_colors'),
                     'lines_plot':
                         None
                         if self.plot_options.get('no_kde') else
                         kde_data[contig]['data']}
                    )
        return hdata            


# +++++++++++++++++++++ Readers / Writers ++++++++++++++++++
#
# The following classes support reading and writing of the per-variant remap
# files and CloudMap-compatibility files that can be generated through the
# -t/--text-file option of the mimodd map command or that were produced by
# CloudMap.

class PerVariantFileReader (pyvcf.VCFLikeFileReader):
    legacy_header_fields = ['Chr', 'Pos',
                            'Alt Count', 'Ref Count',
                            'Read Depth', 'Ratio'
                            ]
    
    def metaparser (self, meta, header_line):
        """Parse the info section (meta data and header)
        of a per-variant report input stream."""

        # special-case contig lengths by treating them as integers
        # copying pyvcf.Info behavior
        for contig_id in meta.setdefault('contig', OrderedDict()):
            try:
                meta['contig'][contig_id]['length'] = int(
                    meta['contig'][contig_id]['length']
                    )
            except KeyError:
                # ignore malformatted contig lines without 'length' element
                pass
        
        # parse the header line
        if header_line[0] == '#':
            header_fields = header_line[1:].rstrip('\t\r\n').split('\t')
        elif header_line.startswith('"#Chr'):
            # probably a CloudMap-corrupted header line
            # don't bother reading it
            header_fields = type(self).legacy_header_fields
        else:
            raise FormatParseError(
                'Could not parse header line.',
                help='A header line starting with a single "#" must precede '
                     'the body of a per-variant report file.'
                )
        return SimpleInfo(meta, header_fields)


class PerVariantSvdFileReader (PerVariantFileReader):
    colnames = ['Chr', 'Pos']

    def __init__ (self, ifo):
        super().__init__(ifo)
        if self.info.header_fields[:2] != self.colnames:
            raise FormatParseError(
                'Invalid per-variant file'
                )
        
    def __next__ (self):
        fields = next(self.ifo).rstrip('\t\r\n').split('\t')
        if len(fields) >= 2:
            return SimpleRecord(chrom=fields[0],
                                pos=int(fields[1]),
                                linkage_data=[1, 1, []]
                                )
        else:
            raise FormatParseError(
                'Invalid per-variant report file. Expected 2 columns per line.'
                )

    
class PerVariantScoreFileReader (PerVariantFileReader):
    colnames = [
        'Chr', 'Pos',
        'LinkageScore', 'Weight'
        ]

    def __init__ (self, ifo):
        super().__init__(ifo)
        
        self.legacy_mode = False
        if self.info.header_fields[:4] != self.colnames[:4]:
            if self.info.header_fields == type(self).legacy_header_fields:
                # This is a legacy CloudMap-style remap file, in which
                # CloudMap or an older version of MiModD did not store
                # the final linkage data for the position, but only the
                # allele count information necessary to recalculate them.
                self.legacy_mode = True
            else:
                raise FormatParseError(
                    'Invalid per-variant file.'
                    )

    def __next__(self):
        fields = next(self.ifo).rstrip('\t\r\n').split('\t')
        if len(fields) != len(self.info.header_fields):
            raise FormatParseError(
                'Invalid per-variant report file. '
                'Expected a constant number of TAB-separated fields per line.'
                )
        try:
            return self.parse_into_record(fields)
        except ValueError:
            pass
        raise FormatParseError(
            'Invalid per-variant report file. '
            'Make sure the file was generated in the same analysis mode as '
            'the current one or with a compatible CloudMap tool.'
            )

    def parse_into_record (self, fields):
        raise NotImplementedError

    
class PerVariantVacFileReader (PerVariantScoreFileReader):
    def __init__ (self, ifo):
        super().__init__(ifo)
        
        if self.legacy_mode:
            raise FormatParseError(
                'Invalid per-variant file. "VAC" analysis is not compatible '
                'with legacy remap files as produced by CloudMap or older '
                'versions of MiModD.'
                )

    def parse_into_record (self, fields):
        ld = [float(n) for n in fields[4:6]]
        if ld[0] >= 3:
            # VAC-style info scores cannot be larger than 2.0.
            # Larger values indicate file format incompatibility
            # (e.g., this could be a VAF-style file, where the corresponding
            # field stores an integer allele count) and we signal this to the
            # caller by raising a ValueError.
            raise ValueError
        return SimpleRecord(
            chrom=fields[0],
            pos=int(fields[1]),
            linkage_data=[float(fields[2]),
                          float(fields[3]),
                          ld]
            )

    
class PerVariantVafFileReader (PerVariantScoreFileReader):
    def __init__ (self, ifo):
        super().__init__(ifo)

    def parse_into_record (self, fields):
        if self.legacy_mode:
            return self._legacy_linkage_calc(*fields[:5])

        return SimpleRecord(
            chrom=fields[0],
            pos=int(fields[1]),
            linkage_data=[float(fields[2]),
                          float(fields[3]),
                          [int(n) for n in fields[4:]]]
            )

    def _legacy_linkage_calc (self, chrom, *count_fields):
        pos, unrelated_like, related_like, total = [
            int(n) for n in count_fields
            ]
        informative_dp = unrelated_like + related_like
        if related_like > unrelated_like:
            linkage_score = (
                (related_like - unrelated_like)**3 / informative_dp**3
                )
        else:
            linkage_score = 0
        return SimpleRecord(
            chrom=chrom,
            pos=pos,
            linkage_data=[
                linkage_score, informative_dp ** 0.5,
                [related_like, unrelated_like, total]
                ]
            )


class VCFRecord_VAFReport_Converter (converters.Record_Converter):
    """Convert linkage data records into VAF report format."""
    
    def __init__ (self, contigs, colnames):
        self.colnames = colnames
        self.ColError = RuntimeError(
            'Number of columns to be written to TAB-separated file '
            'does not match the number of column names written earlier.'
            )
        header = ''
        for ID, info in contigs.items():
            header += '##contig=<ID={0},length={1}>\n'.format(ID,
                                                              info['length'])
        header += '\t'.join(colnames)
        super().__init__(header)

    def convert (self, record):
        data = [record.chrom, record.pos,
                record.linkage_data[0],
                record.linkage_data[1]] + record.linkage_data[2]
        if len(data) != len(self.colnames):
            raise self.ColError
        return '\t'.join(str(d) for d in data)


class VCFRecord_SVDReport_Converter (VCFRecord_VAFReport_Converter):
    """Convert VCFRecords into stripped down SVD Report format."""
    
    def convert (self, record):
        data = [record.chrom, record.pos]
        if len(data) != len(self.colnames):
            raise self.ColError
        # write records as they come in
        return '\t'.join(str(d) for d in data)


class VCFRecord_CloudMap_Converter (pyvcf.VCFRecord_VCF_Converter):
    """Convert VCF records into the limited VCF variant used by CloudMap."""
    
    def __init__ (self, header, sample=None):
        # CloudMap only deals with single-sample VCF files.
        # If sample is None, we want to write a VCF file without
        # any sample-specific columns, otherwise we keep only the column
        # of the single specified sample.

        # sanitize contig names so that CloudMap can cope with them
        self.compat_contig_names = sanitize_contig_names_for_cloudmap(
                                      header.meta['contig'])
        new_contigs = OrderedDict()
        for contig_ID, contig_data in header.meta['contig'].items():
            new_contigs[self.compat_contig_names[contig_ID]] = contig_data
        header.meta['contig'] = new_contigs

        # The superclass expects a list of samples, but here
        # we are interested in maximally one so we do the conversion from
        # a single item to a list here.
        if sample is None:
            samples = []
        else:
            samples = [sample]
        # fast access to parent class methods
        self.super = super()
        self.super.__init__(header, samples)

    def convert (self, record):
        if self.samples:
            sample = self.samples[0]
            # We are writing a sample-specific column, which we need to
            # adjust for CloudMap
            record.sampleinfo['AD'] = {}
            # Within the record.linkage_data list the first two elements
            # represent the linkage score and its weight. Neither of these
            # values is needed for CloudMap, but the third element is the
            # list of the raw allele counts that we are interested in here.
            record.sampleinfo['AD'][sample] = '{0},{1}'.format(
                record.linkage_data[2][0], record.linkage_data[2][1]
                )
            # cloudmap calculates linkage as:
            # second value of AD field / read depth from DP field
            # so we need to adjust DP to equal the sum of the two
            # AD field values
            record.sampleinfo['DP'][sample] = '{0}'.format(
                record.linkage_data[2][0] + record.linkage_data[2][1]
                )
            # CloudMap does not know about the DPR field so we do not have
            # to write it
            del record.sampleinfo['DPR']
        # CloudMap is not inspecting the INFO field
        record.info = OrderedDict()
        # to think about: do we want to adjust REF and ALT?
        # turn chromosome names into their CloudMap
        # compatible versions before writing
        record.chrom = self.compat_contig_names[record.chrom]
        return self.super.convert(record)


# ++++++++++++ helper functions ++++++++++++++

def cloudmap_seqdict_from_vcf (ifile, ofile = None):
    with ExitStack() as exit_stack:
        vcf = exit_stack.enter_context(pyvcf.open(ifile))
        if not ofile:
            out = sys.stdout
        else:
            out = open(ofile, 'w')
            exit_stack.enter_context(out)
        compat_contig_names = sanitize_contig_names_for_cloudmap(
                              vcf.info.meta['contig'])
        for ident, info in vcf.info.meta['contig']:
            out.write('{0}\t{1}\n'.format(compat_contig_names[ident],
                                          int(info['length'])//10**6+1))
    

def parse_seqdict_source (dict_file):
    try:
        # see if the source file is in fasta format
        seqinfo = fasta.get_fasta_info(dict_file)
    except FormatParseError:
        try:
            # maybe we can parse this as a cloudmap sequence dictionary?
            seqinfo = read_cloudmap_seqdict(dict_file)
        except FormatParseError:
            # give up
            raise FormatParseError(
                'Failed to parse the sequence information source file.\n'
                'The source must be a fasta reference genome or a '
                'CloudMap-style sequence dictionary file specifying '
                'chromosome lengths.'
                )

    contig_dict = OrderedDict()
    for record in seqinfo:
        contig_dict[record['SN']] = OrderedDict([('length', record['LN'])])
    return contig_dict


def read_cloudmap_seqdict (dict_file):
    seqinfo = []
    with open(dict_file) as i_file:
        for line in i_file:
            # allow empty lines
            line = line.strip('\t\r\n')
            if line:
                try:
                    chrom, length = line.split('\t')
                except ValueError:
                    raise FormatParseError(
                        'CloudMap Sequence Dictionary files must be '
                        'TAB-separated with two columns.'
                        )
                try:
                    length = int(length) * 10**6
                except ValueError:
                    raise FormatParseError(
                        'The second column of a CloudMap Sequence Dictionary '
                        'file must consist of numeric values specifying '
                        'chromosome lengths in Megabases.'
                        )
                seqinfo.append({'SN': chrom, 'LN': length})
    return seqinfo


def sanitize_contig_names_for_cloudmap (ori_names):
    """Map contig names to CloudMap-compatible versions."""

    # CloudMap does not work correctly with contig names containing colons
    # so we replace ":" with "_".

    compat_map = {contig_name: contig_name.replace(':', '_')
                  for contig_name in ori_names}
    return compat_map


def parse_bin_sizes (bin_sizes):
    factors = {'K': 10**3,
               'M': 10**6
               }
    sizes = []
    for size_str in bin_sizes:
        # ensure size_str has a minimal length of two
        size_str = '00' + size_str.strip()
        if size_str[-1] == 'b':
            try:
                factor = factors[size_str[-2]]
                size_int = int(size_str[:-2]) * factor
            except (KeyError, ValueError):
                raise ArgumentParseError(
                    'Could not parse bin-size value "{0}". '
                    'Expected format INT[Kb|Mb].',
                    size_str
                    )
        else:
            try:
                size_int = int(size_str)
            except ValueError:
                raise ArgumentParseError(
                    'Could not parse bin-size value "{0}". '
                    'Expected format INT[Kb|Mb].',
                    size_str
                    )
        sizes.append(size_int)
    return sizes


def delegate (mode, ifile, mapping_sample = None,
              related_parent = None, unrelated_parent = None,
              contrast_sample = None,
              infer_missing_parent = None,
              ofile = None,
              bin_sizes = None,
              text_file = None,
              seqinfo_external = None,
              cloudmap_mode = False,
              plot_file = None,
              quiet = False,
              **plot_options):
    """Module entry function called from the package CLI.

    Delegates the real analysis work to dedicated linkage analyzers
    after general argument validation and preprocessing.
    """

    # general argument validation
    mode = mode.upper()
    if mode == 'VAF':
        if contrast_sample:
            raise ArgumentParseError(
                'Cannot use a contrast sample in "{0}" mode.',
                mode
                )
        call_args = {
            'mapping_sample': mapping_sample,
            'related_parent': related_parent,
            'unrelated_parent': unrelated_parent,
            'infer_missing_parent': infer_missing_parent,
            'cloudmap_mode': cloudmap_mode
            }
        analyzer = VAFAnalyzer
    elif mode == 'VAC':
        if related_parent or unrelated_parent:
            raise ArgumentParseError(
                'Cannot use related/unrelated parent samples in "{0}" mode.',
                mode
                )
        if infer_missing_parent:
            raise ArgumentParseError(
                'Parental allele inference is not supported in "{0}" mode.',
                mode
                )
        if cloudmap_mode:
            raise ArgumentParseError(
                '"{0}" mode cannot produce Cloudmap-compatible output.',
                mode
                )
        call_args = {
            'mapping_sample': mapping_sample,
            'contrast_sample': contrast_sample,
            }
        analyzer = VACAnalyzer
    elif mode == 'SVD':
        if any([
            mapping_sample, related_parent, unrelated_parent, contrast_sample
            ]):
            raise ArgumentParseError(
                'Assigning roles to samples is not supported in "{0}" mode.',
                mode
                )
        if infer_missing_parent:
            raise ArgumentParseError(
                'Parental allele inference is not supported in "{0}" mode.',
                mode
                )
        call_args = {'cloudmap_mode': cloudmap_mode}
        analyzer = SVDAnalyzer
    else:
        raise ArgumentParseError(
            'Unknown mode "{0}". Expected "SVD", "VAF" or "VAC".',
            mode
            )

    if plot_file:
        if plotters.RPY_EXCEPTION:
            # upon import plotters sets this to False
            # if rpy2 is not installed
            raise DependencyError(
                'Graphical output requires the third-party module rpy.',
                plotters.RPY_EXCEPTION
                )
        if quiet:
            plot_options['no_warnings'] = True
        call_args['plot_file'] = plot_file
        call_args['plot_options'] = plot_options

    if not bin_sizes:
        bin_sizes = [10**6, 5*10**5]
    else:
        bin_sizes = parse_bin_sizes(bin_sizes)
    call_args['bin_sizes'] = bin_sizes

    # With IO starting here all opened files are pushed onto
    # an ExitStack to ensure they are closed at the end of the function.
    with ExitStack() as exit_stack:
        # input file format dependent argument validation
        # open input file and detect its format
        try:
            ifo = pyvcf.open(ifile)
        except FormatParseError:
            try:
                if mode == 'SVD':
                    ifo = PerVariantSvdFileReader(open(ifile))
                elif mode == 'VAF':
                    ifo = PerVariantVafFileReader(open(ifile))
                else:
                    ifo = PerVariantVacFileReader(open(ifile))
            except FormatParseError:
                raise ArgumentValidationError(
                    'Expected a VCF or a per-variant report file as input. '
                    'When using a per-variant report file, make sure the file '
                    'was generated in "{0}" mode or with a compatible CloudMap '
                    'tool.', mode
                    )
        exit_stack.enter_context(ifo)
        call_args['ifo'] = ifo

        if seqinfo_external:
            if ifo.info.meta.get('contig'):
                # If an input file provides contig information in its header
                # we prefer this over user-specified info.
                # TO DO: Extend the sanitize tool to allow overwriting
                # the contig information found in a VCF-like file with that
                # calculated from a fasta file.
                raise ArgumentValidationError(
                    'Contig size information is already present in the input. '
                    'Since this info is probably more reliable, than '
                    'user-provided values, this tool does not allow you to '
                    'overwrite it.\n'
                    'Please rerun the tool without providing a sequence '
                    'dictionary source file.'
                    )
            ifo.info.meta['contig'] = parse_seqdict_source(seqinfo_external)
        elif not ifo.info.meta.get('contig'):
            raise ArgumentValidationError(
                'Your input file does not encode the required information '
                'about contig sizes.\n'
                'Please specify the reference genome fasta file or a '
                'CloudMap-style sequence dictionary that provides this info.'
                )

        # acquire output streams
        if not ofile:
            out = sys.stdout
        else:
            out = open(ofile, 'w')
            exit_stack.enter_context(out)
            
        if not text_file:
            text_out = None
        else:
            text_out = open(text_file, 'w')
            exit_stack.enter_context(text_out)
        call_args['text_out'] = text_out

        result = analyzer(**call_args).analyze()

        # print the binned linkage data returned by the delegates
        header_template = 'Histogram data for LG: {0} '
        if mode == 'SVD':
            header_template += '(total markers: {1})'
        else:
            header_template += '(aggregated marker weights: {1})'
        for contig, data_series in result.items():
            if mode == 'SVD' or result[contig]['markers'] > 0:
                print(
                    header_template
                    .format(contig, int(result[contig]['markers'])),
                    file=out
                    )
                for xbase, series_data in data_series['data'].items():
                    print('Data based on bin-width ' + str(xbase), file=out)
                    for column, counts in series_data.items():
                        print('{0}\t{1:.2f}'.format(column, counts), file=out)
                    print(file=out)
                print(file=out)
            else:
                print(
                    'Skipping LG: {0} - no markers found.'.format(contig),
                    file=out
                    )
                if not quiet:
                    print('LG {0}: No markers found!'.format(contig))
