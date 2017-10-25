#!/usr/bin/env python
""" MultiQC module to parse output from sequana"""
from __future__ import print_function
from collections import OrderedDict
import logging
import os
import re
from collections import defaultdict
import yaml

from multiqc import config
from multiqc.modules.base_module import BaseMultiqcModule
from multiqc.plots import linegraph, table, heatmap, bargraph

log = logging.getLogger('multiqc.sequana/quality_control')


class MultiqcModule(BaseMultiqcModule):

    def __init__(self):

        # Initialise the parent object
        super(MultiqcModule, self).__init__(
            name='Sequana/quality_control',
            anchor='sequana_quality_control',
            target='sequana_quality_control',
            href='http://github.com/sequana/sequana/',
            info="(sequana pipelines)")

        self.data = {}
        for myfile in self.find_log_files("sequana/quality_control"):
            thisdata =  self.parse_logs(myfile["f"])
            name = thisdata["project"]
            self.data[name] = self.parse_logs(myfile["f"])

        if len(self.data) == 0:
            log.debug("Could not find any data in {}".format(config.analysis_dir))
            raise UserWarning

        log.info("Found {} reports".format(len(self.data)))

        self.populate_columns()
        self.add_phix_section()
        self.add_adapter_section()

    def populate_columns(self):

        # cutadapt_json
        #  Number of reads
        #      Total paired reads: 864,879

        headers = {}
        if any(['multiqc_total_reads' in self.data[s] for s in self.data]):
            headers['multiqc_total_reads'] = {
                'title': 'TODO',
                'description': 'TODO',
                #'max': 100,
                'min': 0,
                #'modify': lambda x: x * 100,
                'scale': 'RdYlGn',
                #'format': '{:,.1f}'
                'shared_key': 'multiqc_total_reads',
                #'format': read_format,
                'hidden': True,
            }
        if len(headers.keys()):
            self.general_stats_addcols(self.data, headers)

    def parse_logs(self, log_dict):
        import json
        data = json.loads(log_dict)
        this =  data["cutadapt_json"]["Number of reads"]["Total paired reads"]
        data["multiqc_total_reads"] = this
        return data

    def add_phix_section(self):
        data = {}
        for name in self.data.keys():
            data[name] = {'phix_qc': self.data[name]["phix_section"]["contamination"]}

        pconfig = {
            "title": "Percentage of phix in the raw data",
            "percentages": True,
            "min": 100,
        }

        self.add_section(
            name = 'Phix presence',
            anchor = 'mean_read_length',
            description = 'TODO',
            helptext = "",
            plot = bargraph.plot(data, None, pconfig))

    def add_adapter_section(self):
        data = {}
        for name in self.data.keys():
            thisdata = self.data[name]["cutadapt_json"]["percent"]["Pairs kept"]
            data[name] = {'pairs_kept': thisdata.replace("(","").replace(")","").replace("%","")}

        pconfig = {
            "title": "Percentage of pairs kept",
            "percentages": True,
            "min": 0,
            "max": 100,
        }

        self.add_section(
            name = 'Pairs kept',
            anchor = 'Pairs kept',
            description = 'Pairs kept',
            helptext = "",
            plot = bargraph.plot(data, None, pconfig))







