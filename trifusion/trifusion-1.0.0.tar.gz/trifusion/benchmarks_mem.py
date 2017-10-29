import os
from os.path import join

from memory_profiler import memory_usage
import traceback

from process.sequence import AlignmentList
import process.data as data

data_dir = "/home/diogo/Diogo/Science/Scripts/packages/TriFusion_benchmarks/data/"
db_path = "/home/diogo/Diogo/TriFusion_testdata/benchmark.db"
bench_dir = "/home/diogo/Diogo/TriFusion_testdata/benchmarks_out"

res = []

# Uncomment active data set
# ds_path = join(data_dir, "614_protein")
# ds_path = join(data_dir, "3093_protein")
# ds_path = join(data_dir, "3093_141_protein")
# ds_path = join(data_dir, "3093_376_protein")
# ds_path = join(data_dir, "7378_dna")
# ds_path = join(data_dir, "1_40_large")
# ds_path = join(data_dir, "1_40_large_interleave")
# ds_path = join(data_dir, "1_40_large_interleave_nex")
# ds_path = join(data_dir, "1_376_large")
# ds_path = join(data_dir, "2_big_data")
ds_path = join(data_dir, "52285_loci")

#mfilter = ["Postia_placenta"]
#mfilter = ["535_12"]
mfilter = ["Ang_30"]

ds = [join(ds_path, x) for x in os.listdir(ds_path)]

# rev_ds = join(data_dir, "614_protein_rev")
# rev_ds = join(data_dir, "3093_protein_rev")
# rev_ds = join(data_dir, "3093_141_protein_rev")
# rev_ds = join(data_dir, "3093_376_protein_rev")
# rev_ds = join(data_dir, "7378_dna_rev")
# rev_ds = join(data_dir, "2_big_data_rev")
# rev_ds = join(data_dir, "52285_loci_rev")

# ds = [join(rev_ds, x) for x in os.listdir(rev_ds) if x.endswith(".phy")]
# part_file = [join(rev_ds, x) for x in os.listdir(rev_ds) if not x.endswith(".phy")][0]

# @profile
def read_ds(ds):
    print("Profiling 'read_ds' with a data set of {} files".format(len(ds)))
    x = AlignmentList(ds, sql_db=db_path)

# @profile
def convert_ds(aln_obj):

    aln_obj.write_to_file(["fasta"], output_dir=bench_dir)

# @profile
def convert_ds_int(aln_obj):
    print("Profiling 'convert_ds_int' with a data set of {} files and "
          "{} taxa".format(
        len(aln_obj.alignments), len(aln_obj.taxa_names)))
    aln_obj.write_to_file(["nexus"], output_dir=bench_dir, interleave=True)

# @profile
def concatenate_ds(aln_obj):
    print("Profiling 'concatenate_ds' with a data set of {} files and "
          "{} taxa".format(
        len(aln_obj.alignments), len(aln_obj.taxa_names)))
    aln_obj.concatenate()

def collapse_ds(aln_obj):
    print("Profiling 'collapse_ds' with a data set of {} files and "
          "{} taxa".format(
        len(aln_obj.alignments), len(aln_obj.taxa_names)))
    aln_obj.collapse(use_main_table=True, dest=bench_dir)

def consensus_ds(aln_obj):
    print("Profiling 'consensus_ds' with a data set of {} files and "
          "{} taxa".format(
        len(aln_obj.alignments), len(aln_obj.taxa_names)))
    aln_obj.consensus("Soft mask", single_file=True, use_main_table=True)

def taxa_contain_filter(aln_obj):
    print("Profiling 'taxa_contain_filter' with a data set of {} files and "
          "{} taxa".format(
        len(aln_obj.alignments), len(aln_obj.taxa_names)))
    aln_obj.filter_by_taxa(mfilter, "contain")

def min_taxa_filter(aln_obj):
    print("Profiling 'min_taxa_filter' with a data set of {} files and "
          "{} taxa".format(
        len(aln_obj.alignments), len(aln_obj.taxa_names)))
    aln_obj.filter_min_taxa(80)

def missing_data_filter(aln_obj):
    print("Profiling 'missing_data_filter' with a data set of {} files and "
          "{} taxa".format(
        len(aln_obj.alignments), len(aln_obj.taxa_names)))
    aln_obj.filter_missing_data(50, 75)

def codon_filter(aln_obj):
    print("Profiling 'codon_filter' with a data set of {} files and "
          "{} taxa".format(
        len(aln_obj.alignments), len(aln_obj.taxa_names)))
    aln_obj.filter_codon_positions([True, True, False])

def variable_filter(aln_obj):
    print("Profiling 'variable_filter' with a data set of {} files and "
          "{} taxa".format(
        len(aln_obj.alignments), len(aln_obj.taxa_names)))
    aln_obj.filter_segregating_sites(0, 200)

def informative_filter(aln_obj):
    print("Profiling 'informative_filter' with a data set of {} files and "
          "{} taxa".format(
        len(aln_obj.alignments), len(aln_obj.taxa_names)))
    aln_obj.filter_informative_sites(0, 200)

def code_gaps(aln_obj):
    print("Profiling 'code_gaps' with a data set of {} files and "
          "{} taxa".format(
        len(aln_obj.alignments), len(aln_obj.taxa_names)))
    aln_obj.code_gaps()

def reverse_concat(aln_obj, part_file):
    print("Profiling 'reverse_concat' with a data set of {} files and "
          "{} taxa".format(
        len(aln_obj.alignments), len(aln_obj.taxa_names)))
    partition = data.Partitions()
    partition.read_from_file(part_file)
    saln = aln_obj.alignments.values()[0]
    saln.set_partitions(partition)
    aln_obj.set_partition_from_alignment(saln)
    aln_obj.reverse_concatenate()

    # Post reverse ops
    print("Writing files")
    aln_obj.write_to_file(["nexus"], output_dir=bench_dir)

# Always start by reseting database
if os.path.exists(db_path):
    os.remove(db_path)

aln_obj = AlignmentList(ds, sql_db=db_path)

try:
    control_mem = memory_usage()
    # print("Control memory usage at: %s" % round(max(control_mem), 1))
    # mem_usage = memory_usage((read_ds, (ds, )))
    # mem_usage = memory_usage((convert_ds, (aln_obj,)))
    # mem_usage = memory_usage((convert_ds_int, (aln_obj, )))
    # mem_usage = memory_usage((concatenate_ds, (aln_obj,)))
    # mem_usage = memory_usage((collapse_ds, (aln_obj, )))
    # mem_usage = memory_usage((consensus_ds, (aln_obj, )))
    #mem_usage = memory_usage((taxa_contain_filter, (aln_obj, )))
    # mem_usage = memory_usage((min_taxa_filter, (aln_obj, )))
    # mem_usage = memory_usage((missing_data_filter, (aln_obj, )))
    # mem_usage = memory_usage((codon_filter, (aln_obj, )))
    # mem_usage = memory_usage((variable_filter, (aln_obj, )))
    # mem_usage = memory_usage((informative_filter, (aln_obj, )))
    # mem_usage = memory_usage((reverse_concat, (aln_obj, part_file, )))
    mem_usage = memory_usage((code_gaps, (aln_obj, )))
    print("Maximum memory usage: %s" % round(max(mem_usage) - max(control_mem), 1))
except Exception as e:
    print(e)
    traceback.print_exc()

# os.remove(db_path)