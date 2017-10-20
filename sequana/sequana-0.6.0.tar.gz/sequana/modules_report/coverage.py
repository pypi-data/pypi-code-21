# coding: utf-8
#
#  This file is part of Sequana software
#
#  Copyright (c) 2016 - Sequana Development Team
#
#  File author(s):
#      Dimitri Desvillechabrol <dimitri.desvillechabrol@pasteur.fr>,
#          <d.desvillechabrol@gmail.com>
#
#  Distributed under the terms of the 3-clause BSD license.
#  The full license is in the LICENSE file, distributed with this software.
#
#  website: https://github.com/sequana/sequana
#  documentation: http://sequana.readthedocs.io
#
##############################################################################
"""Module to write coverage report"""
import os

import pandas as pd

from sequana import bedtools
from sequana.modules_report.base_module import SequanaBaseModule
from sequana.utils import config
from sequana.utils.datatables_js import DataTable, DataTableFunction
from sequana.plots.canvasjs_linegraph import CanvasJSLineGraph
from sequana import logger


__all__ = ["CoverageModule", "ChromosomeCoverageModule"]


class CoverageModule(SequanaBaseModule):
    """ Write HTML report of coverage analysis. This class takes either a
    :class:`GenomeCov` instances or a csv file where analysis are stored.
    """
    def __init__(self, data):
        """.. rubric:: constructor

        :param data: it can be a csv filename created by sequana_coverage or a
        :class:`bedtools.GenomeCov` object.
        """
        super().__init__()
        try:
            self.bed = bedtools.GenomeCov(data)
        except FileNotFoundError:
            msg = ("The csv file is not present. Please, check if your"
                   " file is present.")
            raise FileNotFoundError(msg)
        except TypeError:
            self.bed = data
        try:
            html_list = self.create_reports()
        except TypeError:
            msg = ("Data must be either a csv file or a :class:`GenomeCov` "
                   "instance where zscore is computed.")
            raise TypeError(msg)
        self.title = "Coverage Report of {0}".format(config.sample_name)
        self.intro = ("<p>Report the coverage of your sample {0} to check the "
                      "quality of your mapping and to highlight regions of "
                      "interest (under and over covered).</p>".format(
                      config.sample_name))
        self.create_report_content(html_list)
        self.create_html("sequana_coverage.html")

    def create_report_content(self, html_list):
        self.sections = list()
        self.chromosome_table(html_list)

    def chromosome_table(self, html_list):
        """ Create table with links to chromosome reports
        """
        df = pd.DataFrame([[chrom.chrom_name, chrom.get_size(),
                          chrom.get_mean_cov(), chrom.get_var_coef(), page] for
                          chrom, page in zip(self.bed.chr_list, html_list)],
                          columns=["chromosome", "size", "mean_coverage",
                          "coef_variation", "link"])
        datatable = DataTable(df, 'chrom')
        datatable.datatable.datatable_options = {'pageLength': 15,
                                                 'dom': 'Bfrtip',
                                                 'buttons': ['copy', 'csv']}
        datatable.datatable.set_links_to_column('link', 'chromosome')
        js = datatable.create_javascript_function()
        html_table = datatable.create_datatable(float_format='%.3g')
        self.sections.append({
            "name": "Chromosomes",
            "anchor": "chromosomes",
            "content":
                "<p>Link to coverage analysis report for each chromosome. "
                "Size, mean coverage and coefficient of variation are reported"
                " in the table below.</p>\n{0}\n{1}".format(js, html_table)
            })

    def create_reports(self):
        """ Create HTML report for each chromosome present in data.
        """
        # FIXME: why bed[0] (i.e. first chromosome)
        datatable_js = CoverageModule.init_roi_datatable(self.bed[0])
        chrom_output_dir = config.output_dir + os.sep + "coverage_reports"
        if not os.path.exists(chrom_output_dir):
            os.makedirs(chrom_output_dir)
        page_list = []
        for chrom in self.bed:
            logger.info("Creating coverage report {}".format(chrom.chrom_name))
            chrom_report = ChromosomeCoverageModule(chrom, datatable_js)
            page_list.append(chrom_report.html_page)
        return page_list

    # I made it as static method because I need it in the coverage standalone
    # to initiate my datatables
    def init_roi_datatable(chrom):
        """ Initiate :class:`DataTableFunction` to create table to link each
        row with sub HTML report. All table will have the same appearance. So,
        let's initiate its only once.
        """
        # get an roi df
        df = chrom.get_roi().df.copy()
        df['link'] = ''
        # set datatable options
        datatable_js = DataTableFunction(df, 'roi')
        datatable_js.set_links_to_column('link', 'start')
        datatable_js.set_links_to_column('link', 'end')
        datatable_js.datatable_options = {'scrollX': 'true',
                                          'pageLength': 15,
                                          'scrollCollapse' : 'true',
                                          'dom': 'Bfrtip',
                                          'buttons': ['copy', 'csv']}
        return datatable_js


class ChromosomeCoverageModule(SequanaBaseModule):
    """ Write HTML report of coverage analysis for each chromosome. It is
    created by CoverageModule.
    """
    def __init__(self, chromosome, datatable, directory="coverage_reports"):
        """
        """
        super().__init__()
        # to define where are css and js
        if directory in {None, '.'}:
            self.path = ''
            directory = '.'
        else:
            self.path = '../'
        self.chromosome = chromosome
        self.datatable = datatable
        self.title = "Coverage analysis of chromosome {0}".format(
            self.chromosome.chrom_name)
        self.intro = ("<p>The genome coverage analysis of the chromosome "
                      "<b>{0}</b>.</p>".format(self.chromosome.chrom_name))
        self.create_report_content(directory)
        self.html_page = "{0}{1}{2}.cov.html".format(
            directory, os.sep, self.chromosome.chrom_name)
        self.create_html(self.html_page)

    def create_report_content(self, directory):
        """ Generate the sections list to fill the HTML report.
        """
        self.sections = list()

        rois = self.chromosome.get_roi()

        self.coverage_plot()
        links = self.subcoverage(rois, directory)
        self.coverage_barplot()
        self.basic_stats()
        self.regions_of_interest(rois, links)
        if "gc" in self.chromosome.columns():
            self.gc_vs_coverage()
        self.normalized_coverage()
        self.zscore_distribution()

    def coverage_plot(self):
        """ Coverage section.
        """
        image = self.create_embedded_png(self.chromosome.plot_coverage,
                                         input_arg="filename")
        self.sections.append({
            "name": "Coverage",
            "anchor": "coverage",
            "content":
                "<p>The following figure shows the per-base coverage along the"
                " reference genome (black line). The blue line indicates the "
                "running median. From the normalised coverage, we estimate "
                "z-scores on a per-base level. The red lines indicates the "
                "z-scores at plus or minus N standard deviations, where N is "
                "chosen by the user. (default:4)</p>\n{0}".format(image)
        })

    def coverage_barplot(self):
        """ Coverage barplots section.
        """
        image1 = self.create_embedded_png(self.chromosome.plot_hist_coverage,
                                          input_arg="filename",
                                          style="width:45%")
        image2 = self.create_embedded_png(self.chromosome.plot_hist_coverage,
                                          input_arg="filename",
                                          style="width:45%",
                                          logx=False)
        self.sections.append({
            'name': "Coverage histogram",
            'anchor': "cov_barplot",
            'content':
                "<p>The following figure contains the histogram of the genome "
                "coverage. The X and Y axis being in log scale.</p>\n"
                "{0}\n{1}".format(image1, image2)
        })

    def subcoverage(self, rois, directory):
        """ Create subcoverage report to have acces of a zoomable line plot.
        """
        # create directory
        chrom_output_dir = os.sep.join([config.output_dir, directory,
                                       str(self.chromosome.chrom_name)])
        if not os.path.exists(chrom_output_dir):
            os.makedirs(chrom_output_dir)
        # create the combobox to link toward different sub coverage
        links = ["{0}/{0}_{1}_{2}.html".format(self.chromosome.chrom_name,
                 i, min(i + 200000, len(self.chromosome))) for i in
                 range(0, len(self.chromosome), 200000)]
        intra_links = ("{0}_{1}_{2}.html".format(self.chromosome.chrom_name,
                       i, min(i + 200000, len(self.chromosome))) for i in
                       range(0, len(self.chromosome), 200000))
        combobox = self.create_combobox(links, 'sub', True)
        combobox_intra = self.create_combobox(intra_links, 'sub', False)
        datatable = self._init_datatable_function(rois)
        # break the chromosome as piece of 200 Mbp
        for i in range(0, len(self.chromosome), 200000):
            SubCoverageModule(self.chromosome, rois, combobox_intra, datatable,
                              i, min(i + 200000, len(self.chromosome)),
                              directory)
        self.sections.append({'name': 'Subcoverage',
                              'anchor': 'subcoverage',
                              'content': combobox})
        return links

    def _init_datatable_function(self, rois):
        """ Initiate :class:`DataTableFunction` to create table to link each
        row with sub HTML report. All table will have the same appearance. So,
        let's initiate its only once.
        """
        datatable_js = DataTableFunction(rois.df, 'roi')
        datatable_js.datatable_options = {'scrollX': 'true',
                                          'pageLength': 15,
                                          'scrollCollapse' : 'true',
                                          'dom': 'Bfrtip',
                                          'buttons': ['copy', 'csv']}
        return datatable_js

    def basic_stats(self):
        """ Basics statistics section.
        """
        li = '<li><b>{0}</b> ({1}): {2:.2f}</li>'
        df = self.chromosome.get_stats(output="dataframe")
        stats = [li.format(tag, desc, value) for desc, value, tag in
                 zip(df['Description'], df['Value'], df['name'])]
        stats = '<ul>{0}</ul>'.format('\n'.join(stats))
        self.sections.append({
            'name': "Basic stats",
            'anchor': 'basic_stats',
            'content':
                "<p>Here are some basic statistics about the "
                "genome coverage.</p>\n{0}".format(stats)
        })

    def regions_of_interest(self, rois, links):
        """ Region of interest section.
        """ 
        # add links to the roi
        x = 200000
        i = 0
        def connect_link(n, x, i):
            condition = True
            while condition:
                if n > x:
                    x += 200000
                    i += 1
                else:
                    condition = False
            return i
        links_list = [links[connect_link(n[0],x,i)] for n in
                     zip(rois.df['start'])]
        rois.df['link'] = links_list
        # create datatable
        low_roi = rois.get_low_roi()
        high_roi = rois.get_high_roi()
        js = self.datatable.create_javascript_function()
        lroi = DataTable(low_roi, "lroi", self.datatable)
        hroi = DataTable(high_roi, "hroi", self.datatable)
        html_low_roi = lroi.create_datatable(float_format='%.3g')
        html_high_roi = hroi.create_datatable(float_format='%.3g')
        rois.df.drop('link', 1, inplace=True)
        roi_paragraph = (
            "<p>Regions with a z-score {0}er than {1:.2f} and at "
            "least one base with a z-score {0}er than {2:.2f} are detected as "
            "{0} coverage region. Thus, there are {3} {0} coverage regions."
            "</p>"
        )
        low_paragraph = roi_paragraph.format("low",
                                             self.chromosome.thresholds.low2,
                                             self.chromosome.thresholds.low,
                                             len(low_roi))
        high_paragraph = roi_paragraph.format("high",
                                              self.chromosome.thresholds.high2,
                                              self.chromosome.thresholds.high,
                                              len(high_roi))
        self.sections.append({
            'name': "Regions Of Interest (ROI)",
            'anchor': 'roi',
            'content':
                "{4}\n"
                "<p>Running median is the median computed along the genome "
                "using a sliding window. The following tables give regions of "
                "interest detected by sequana. Here are the definitions of the "
                "columns:</p>\n"
                "<ul><li>mean_cov: the average of coverage</li>\n"
                "<li>mean_rm: the average of running median</li>\n"
                "<li>mean_zscore: the average of zscore</li>\n"
                "<li>max_zscore: the higher zscore contains in the region</li>"
                "</ul>\n"
                "<h3>Low coverage region</h3>\n{0}\n{1}\n"
                "<h3>High coverage region</h3>\n{2}\n{3}\n".format(
                low_paragraph, html_low_roi, high_paragraph, html_high_roi, js)
        })

    def gc_vs_coverage(self):
        """ 3 dimensional plot of GC content versus coverage.
        """
        image = self.create_embedded_png(self.chromosome.plot_gc_vs_coverage,
                                         input_arg='filename')
        corr = self.chromosome.get_gc_correlation()
        self.sections.append({
            'name': 'Coverage vs GC content',
            'anchor': 'cov_vs_gc',
            'content': 
                "<p>The correlation coefficient between the coverage and GC "
                "content is <b>{0:.3g}</b> with a window size of {1}bp.</p>\n"
                "{2}\n"
                "<p>Note: the correlation coefficient has to be between -1.0 "
                "and 1.0. A coefficient of 0 means no correlation, while a "
                "coefficient of -1 or 1 means an existing "
                "correlation between GC and Coverage</p>".format(
                    corr, self.chromosome.bed.gc_window_size, image
                )
        })

    def normalized_coverage(self):
        """ Barplot of normalized coverage section.
        """
        image = self.create_embedded_png(
            self.chromosome.plot_hist_normalized_coverage,
            input_arg="filename")
        self.sections.append({
            'name': "Normalised coverage",
            'anchor': 'normalised_coverage',
            'content':
                "<p>Distribution of the normalised coverage with predicted "
                "Gaussian. The red line should be followed the trend of the "
                "barplot.</p>\n{0}".format(image)
        })

    def zscore_distribution(self):
        """ Barplot of zscore distribution section.
        """
        image = self.create_embedded_png(self.chromosome.plot_hist_zscore,
                                      input_arg="filename")
        self.sections.append({
            'name': "Z-Score distribution",
            'anchor': 'zscore_distribution',
            'content':
                "<p>Distribution of the z-score (normalised coverage); You "
                "should see a Gaussian distribution centered around 0. The "
                "estimated parameters are mu={0:.2f} and sigma={1:.2f}.</p>\n"
                "{2}".format(self.chromosome.best_gaussian["mu"],
                             self.chromosome.best_gaussian["sigma"],
                             image)
        })


class SubCoverageModule(SequanaBaseModule):
    """ Write HTML report of subsection of chromosome with a javascript
    coverage plot.
    """
    def __init__(self, chromosome, rois, combobox, datatable, start, stop,
                 directory):
        super().__init__()
        if directory == ".":
            self.path = "../"
        else:
            self.path = "../../"
        self.chromosome = chromosome
        self.rois = rois
        self.combobox = combobox
        self.datatable = datatable
        self.start = start
        self.stop = stop
        self.title = ("Coverage analysis of chromosome {0}<br>"
                      "positions {1} and {2}".format(
                      self.chromosome.chrom_name, start, stop))
        self.create_report_content()
        self.create_html("{0}{4}{1}{4}{1}_{2}_{3}.html".format(
            directory, self.chromosome.chrom_name, start, stop, os.sep))

    def create_report_content(self):
        """ Generate the sections list to fill the HTML report.
        """
        self.sections = list()

        self.canvasjs_line_plot()
        self.regions_of_interest()

    def canvasjs_line_plot(self):
        """ Create the CanvasJS line plot section.
        """
        # set column of interest and create the csv
        x_col = 'pos'
        y_col = ('cov', 'mapq0', 'gc')
        columns = self.chromosome.columns()
        y_col = [n for n in y_col if n in columns]
        csv = self.chromosome.to_csv(start=self.start, stop=self.stop,
                                     columns=[x_col] + y_col, index=False,
                                     float_format="%.3g")

        # create CanvasJS stuff
        cjs = CanvasJSLineGraph(csv, 'cov', x_col, y_col)
        # set options
        cjs.set_options({'zoomEnabled': 'true',
                         'zoomType': 'x',
                         'exportEnabled': 'true'})
        # set title
        cjs.set_title("Genome Coverage")
        # set legend
        cjs.set_legend({'verticalAlign': 'bottom',
                        'horizontalAlign': 'center',
                        'cursor':'pointer'},
                        hide_on_click=True)
        # set axis
        cjs.set_axis_x({'title': "Position (bp)",
                        'labelAngle': 30,
                        'minimum': self.start,
                        'maximum': self.stop})
        cjs.set_axis_y({'title': "Coverage (Count)"})
        cjs.set_axis_y2({'title': "GC content (ratio)",
                         'minimum':0,
                         'maximum': 1,
                         'lineColor': '#FFC425',
                         'titleFontColor': '#FFC425',
                         'labelFontColor': '#FFC425'})
        # set datas
        cjs.set_data(index=0, data_dict={'type': 'line',
                                         'name': "Coverage",
                                         'showInLegend': 'true',
                                         'color': '#5BC0DE',
                                         'lineColor': '#5BC0DE'})
        try:
            i = y_col.index('mapq0')
            cjs.set_data(index=i, data_dict={'type': 'line',
                                             'name': "Filtered coverage",
                                             'showInLegend': 'true',
                                             'color': '#D9534F',
                                             'lineColor': '#D9534F'})
        except ValueError:
            pass
        try:
            i = y_col.index('gc')
            cjs.set_data(index=i, data_dict={'type': 'line',
                                             'axisYType': 'secondary',
                                             'name': "GC content",
                                             'showInLegend': 'true',
                                             'color': '#FFC425',
                                             'lineColor': '#FFC425'})
        except ValueError:
            pass
        # create canvasJS
        html_cjs = cjs.create_canvasjs()
        self.sections.append({
            'name': 'Interactive coverage plot',
            'anchor': 'iplot',
            'content': ("{0}{1}\n".format(self.combobox, html_cjs))})

    def regions_of_interest(self):
        """ Region of interest section.
        """
        subseq = [self.start, self.stop]
        low_roi = self.rois.get_low_roi(subseq)
        high_roi = self.rois.get_high_roi(subseq)
        js = self.datatable.create_javascript_function()
        lroi = DataTable(low_roi, "lroi", self.datatable)
        hroi = DataTable(high_roi, "hroi", self.datatable)
        html_low_roi = lroi.create_datatable(float_format='%.3g')
        html_high_roi = hroi.create_datatable(float_format='%.3g')
        roi_paragraph = (
            "<p>Regions with a z-score {0}er than {1:.2f} and at "
            "least one base with a z-score {0}er than {2:.2f} are detected as "
            "{0} coverage region. Thus, there are {3} {0} coverage regions "
            "between the position {4} and the position {5}</p>")
        low_paragraph = roi_paragraph.format("low",
                                             self.chromosome.thresholds.low2,
                                             self.chromosome.thresholds.low,
                                             len(low_roi), self.start,
                                             self.stop)
        high_paragraph = roi_paragraph.format("high",
                                              self.chromosome.thresholds.high2,
                                              self.chromosome.thresholds.high,
                                              len(high_roi), self.start,
                                              self.stop)
        self.sections.append({
            "name": "Regions Of Interest (ROI)",
            "anchor": "roi",
            "content":
                "{4}\n"
                "<p>Running median is the median computed along the genome "
                "using a sliding window. The following tables give regions of "
                "interest detected by sequana. Here are some definition of the "
                "table's columns:</p>\n"
                "<ul><li><b>mean_cov</b>: the average of coverage</li>\n"
                "<li><b>mean_rm</b>: the average of running median</li>\n"
                "<li><b>mean_zscore</b>: the average of zscore</li>\n"
                "<li><b>max_zscore</b>: the higher zscore contains in the "
                "region</li></ul>\n"
                "<h3>Low coverage region</h3>\n{0}\n{1}\n"
                "<h3>High coverage region</h3>\n{2}\n{3}\n".format(
                low_paragraph, html_low_roi, high_paragraph, html_high_roi, js)
        })
