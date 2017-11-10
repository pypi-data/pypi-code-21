"""Convert :term:`VCF` file to :term:`BCF` file"""
from bioconvert import ConvBase


class VCF2BCF(ConvBase):
    """

    """
    input_ext = [".vcf"]
    output_ext = [".bcf"]

    def __init__(self, infile, outfile, *args, **kargs):
        """.. rubric:: constructor

        :param str infile:
        :param str outfile:

        command used::

            bcftools view -Sb
        """
        super(VCF2BCF, self).__init__(infile, outfile, *args, **kargs)

    def _method_bcftools(self, *args, **kwargs):
        # -S means ignored (input format is VCF)
        # -b output BCF instead of VCF
        #cmd = "bcftools view -Sb {} >  {}".format(self.infile, self.outfile)

        # -O, --output-type b|u|z|v Output compressed BCF (b), uncompressed BCF
        # (u), compressed VCF (z), uncompressed VCF (v). Use the -Ou option when
        # piping between bcftools subcommands to speed up performance
        cmd = "bcftools view {} -O b -o {}".format(self.infile, self.outfile)
        self.execute(cmd)



