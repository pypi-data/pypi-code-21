import os

from sequana.misc import wget
from sequana import sequana_config_path
from easydev import DevTools, execute


class BuscoConfig(object):

    def __init__(self, species, outpath=None, sample_name=None, conda_bin_path=None,
            tmp_path=None, Rscript_bin_path=None):

        self.params = {}
        self.params['conda_bin_path'] = conda_bin_path # "/home/cokelaer/miniconda3/env/py3/bin"
        self.params['Rscript'] = Rscript_bin_path # "/home/cokelaer/miniconda3/bin"
        self.params['sample'] = sample_name  # prefix used in output files
        self.params['outpath'] = outpath  # where to store the output directory
        self.params['lineage_path'] = sequana_config_path + "/busco/{}".format(species) 
        self.params['tmp_path'] = tmp_path

    def save_config_file(self, filename):
        from sequana import sequana_data
        config_generic = sequana_data("config.ini", "busco")
        data = open(config_generic, "r").read()
        data = data.format(**self.params)
        with open(filename, "w") as fh:
            fh.write(data)

class BuscoDownload(object):
    """

    This code downloads the BUSCO datasets (about G uncompressed). The data
    is stored in your config path (e.g. ~/.config/sequana/busco under Linux)

        from sequana import busco
        bd = busco.BuscoDownload()
        bd.download()

    Those datasets will then be found automatically by the BUSCO rule provided
    as a snakemake rule in Sequana. 

    """

    def __init__(self):

        dv = DevTools()
        self.base = sequana_config_path + os.sep + "busco"
        dv.mkdir(self.base)
        self.filenames = sorted([
            "bacteria_odb9",
            "proteobacteria_odb9",
            "rhizobiales_odb9",
            "betaproteobacteria_odb9",
            "gammaproteobacteria_odb9",
            "enterobacteriales_odb9",
            "deltaepsilonsub_odb9",
            "actinobacteria_odb9",
            "cyanobacteria_odb9",
            "firmicutes_odb9",
            "clostridia_odb9",
            "lactobacillales_odb9",
            "bacillales_odb9",
            "bacteroidetes_odb9",
            "spirochaetes_odb9",
            "tenericutes_odb9",
            "eukaryota_odb9",
            "fungi_odb9",
            "microsporidia_odb9",
            "dikarya_odb9",
            "ascomycota_odb9",
            "pezizomycotina_odb9",
            "eurotiomycetes_odb9",
            "sordariomyceta_odb9",
            "saccharomyceta_odb9",
            "saccharomycetales_odb9",
            "basidiomycota_odb9",
            "metazoa_odb9",
            "nematoda_odb9",
            "arthropoda_odb9",
            "insecta_odb9",
            "endopterygota_odb9",
            "hymenoptera_odb9",
            "diptera_odb9",
            "vertebrata_odb9",
            "actinopterygii_odb9",
            "tetrapoda_odb9",
            "aves_odb9",
            "mammalia_odb9",
            "euarchontoglires_odb9",
            "laurasiatheria_odb9",
            "embryophyta_odb9",
            "protists_ensembl",
            "alveolata_stramenophiles_ensembl"])

    def download(self, uncompress=True):
        """Download the datasets (tar.gz) and uncompress them

        :param bool uncompress: if True, uncompress the tar.gz and delete it
        """
        url = "http://busco.ezlab.org/v2/datasets"
        for filename in self.filenames:
            basename = filename + ".tar.gz"
            target = self.base + "/" + basename
            print(url + "/" + basename)
            wget(url + "/" + basename, target)
            # TODO untar datasets and cleanup the tar.gz 
            if uncompress:
                execute("tar xvfz %s -C %s" % (target, self.base))
                execute("rm -f %s" % ( target))


