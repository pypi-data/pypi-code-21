from subprocess import check_output
from io import StringIO

import pandas as pd

def vcf_to_dosage(vcf):
    "Convert vcf to dosage using bcftools"

    fixed_fields = "#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO	FORMAT"

    header = check_output("bcftools view -h {vcf} | tail -1".format(vcf=vcf), shell=True).decode()
    header_id_only = header.replace(fixed_fields, "ID")

    cmd = r'bcftools query -f "%ID[\t%DS]\n" {vcf}'.format(vcf=vcf)
    dosage_only = check_output(cmd, shell=True).decode()

    dosage = pd.read_table(StringIO(dosage_only), names=header_id_only.split(), sep="\t", index_col=0).T
    dosage.columns = [d + "_dose" for d in dosage.columns]
    dosage.index.name = "ID"

    return dosage
