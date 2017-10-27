"""Patch ReSDK resources with analysis methods."""
from __future__ import absolute_import, division, print_function, unicode_literals

from resdk.analysis.alignment import bowtie2, hisat2
from resdk.analysis.chip_seq import macs, rose2
from resdk.analysis.differential_expressions import cuffdiff
from resdk.analysis.expressions import cuffnorm, cuffquant
from resdk.analysis.plots import bamliquidator, bamplot
from resdk.resources import Collection, Data, Relation, Sample
from resdk.utils.decorators import return_first_element

Collection.run_bamliquidator = bamliquidator
Collection.run_bamplot = bamplot
Collection.run_bowtie2 = bowtie2
Collection.run_cuffdiff = cuffdiff
Collection.run_cuffnorm = cuffnorm
Collection.run_cuffquant = cuffquant
Collection.run_hisat2 = hisat2
Collection.run_macs = macs
Collection.run_rose2 = rose2

# pylint: disable=no-value-for-parameter
Data.run_bowtie2 = return_first_element(bowtie2)
Data.run_hisat2 = return_first_element(hisat2)
# pylint: enable=no-value-for-parameter

Relation.run_bamliquidator = bamliquidator
Relation.run_bamplot = bamplot
Relation.run_bowtie2 = bowtie2
Relation.run_cuffdiff = cuffdiff
Relation.run_cuffnorm = cuffnorm
Relation.run_cuffquant = cuffquant
Relation.run_hisat2 = hisat2
Relation.run_macs = macs
Relation.run_rose2 = rose2

Sample.run_bowtie2 = bowtie2
Sample.run_cuffquant = cuffquant
Sample.run_hisat2 = hisat2
Sample.run_macs = macs
Sample.run_rose2 = rose2
