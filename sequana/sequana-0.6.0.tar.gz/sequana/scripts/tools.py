


class SequanaOptions(object):
    # assuming an ArgumentParser structure
    def add_version(self, this):
        this.add_argument("--version", dest='version',
            action="store_true", help="print version")
    def add_verbose(self, this):
        this.add_argument("--verbose", dest='verbose',
            action="store_true", help="set verbosity on")
    def add_quiet(self, this):
        this.add_argument("--quiet", dest='verbose',
            action="store_false", help="set verbosity off")
    def add_cluster(self, this):
        this.add_argument("--snakemake-cluster", dest="cluster", 
            type=str,
            help="""FORMAT|a valid snakemake option dedicated to a cluster.  
e.g on LSF cluster use:
    --cluster 'qsub -cwd -q<QUEUE> '

On a SLURM system use for example:

    --cluster 'sbatch --qos normal'

""")

