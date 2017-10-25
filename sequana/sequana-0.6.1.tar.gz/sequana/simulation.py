from tempfile import TemporaryDirectory
from easydev import execute, shellcmd
import os


class Simulator(object):
    """A simple wrapper of art_illumina to generate simulated reads


    Here, we hard*coded the HiSeq2500 but one can chnage the length, coverage,
    standard deviation, paired or not. One can also generate the reads based
    on the coverage or the number of reads.

    Finally, one can also generate a mix of species using
    :meth:`generate_mixture`.


    https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5224698/
    """
    def __init__(self, verbose=True):
        self.verbose = verbose

    def generate(self, fasta_file, outfile, length=150, coverage=10, stdev=10,
            paired=True, nreads=100000, method="coverage",
            illumina_sequence="HiSeq2500"):
        """

        :param fasta_file: input reference

        -m 200 the mean size of DNA/RNA fragments for paired-end simulations
        :param stdev: the standard deviation of DNA/RNA fragment size for paired-end simulations
        :param illumina_sequence: HiSeq2500 or MiSeq

        """
        if illumina_sequence == "HiSeq2500":
            cmd = "art_illumina -ss HS25 "
        elif illumina_sequence == "MiSeq":
            cmd = "art_illumina -ss MS "

        cmd += " -i %s " % fasta_file
        cmd += "  -l %s " % length
        if method == "coverage":
            cmd += " -f %s " % coverage
        elif method == "nreads":
            cmd += " -c %s " % nreads

        cmd += " -m 200"
        cmd += " -s %s " % stdev
        cmd += " -o %s" % outfile
        if paired:
            cmd += " -p"
        #execute(cmd, verbose=self.verbose, show=self.verbose)
        _ = shellcmd(cmd, show=self.verbose)

    def generate_mixture(self, fasta_files, outfile="mixture", length=150, 
            coverage=10, stdev=10, paired=True, method="nreads", nreads=100000):
        """

        :param nreads: integer or list of integer for each fasta
        :param coverage: integer or list of integer for each fasta


        """
        if isinstance(nreads, (int, float)):
            nreads = [nreads] * len(fasta_files)
        if isinstance(coverage, (int, float)):
            coverage = [coverage] * len(fasta_files)

        for i, fasta in enumerate(fasta_files):
            assert os.path.exists(fasta)

        tempdir = TemporaryDirectory()

        for i, fasta in enumerate(fasta_files):
            self.generate(fasta, "%s/test_%s_" % (tempdir.name, i), length=length,
                coverage=coverage[i], stdev=stdev, paired=paired, method=method,
                nreads=nreads[i])

        # Finally concat all the files into the outfile
        # The execute command fails because it uses the stdout and somehow
        # interfers with the cat command ?
        _ = shellcmd("cat {}/test_*_1.fq > {}_1.fq".format(tempdir.name, outfile),
                     show=self.verbose)

        if paired is True:
            _ = shellcmd("cat {}/test_*_2.fq > {}_2.fq".format(tempdir.name, outfile),
                         show=self.verbose)

        tempdir.cleanup()




