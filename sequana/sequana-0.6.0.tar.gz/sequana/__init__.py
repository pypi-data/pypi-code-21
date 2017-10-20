
import pkg_resources
try:
    version = pkg_resources.require("sequana")[0].version
except:
    version = ">=0.20.0"

import colorlog as logger
def sequana_debug_level(level="WARNING"):
    """A deubg level setter at top level of the library"""
    assert level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    logging_level = getattr(logger.logging.logging, level)
    logger.getLogger().setLevel(logging_level)


from easydev import CustomConfig
configuration = CustomConfig("sequana", verbose=False)
sequana_config_path = configuration.user_config_dir

# This must be import before all other modules (sequana_data function)
from .datatools import sequana_data

from .assembly import *
from .adapters import AdapterReader, FindAdaptersFromDesign, Adapter
from .bamtools import BAM, SAMFlags
from .bedtools import GenomeCov
from .cigar import Cigar
from .coverage import Coverage
from .expdesign import ExpDesignAdapter
from .fastq import FastQ, FastQC, Identifier
from .fasta import FastA
from .freebayes_vcf_filter import VCF_freebayes
from .freebayes_bcf_filter import BCF_freebayes
from .kraken_builder import KrakenBuilder
from .krona import KronaMerger
from .kraken import KrakenResults, KrakenPipeline, KrakenAnalysis, KrakenDownload
from .pacbio import BAMPacbio
from .phred import Quality
from .running_median import RunningMedian
from .snaketools import *
from .snpeff import SnpEff
from .sequence import DNA, RNA, Sequence, Repeats


# The standalone app
from . import scripts


def _download_biokit_taxon():
    # This is done only once
    from .lazy import biokit
    tt = biokit.Taxonomy()
    tt._load_flat_file()
try: _download_biokit_taxon()
except: pass



