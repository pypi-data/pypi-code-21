#!/usr/bin/python2

import time
import os
import traceback

from os.path import join


from process.sequence import AlignmentList
import process.data as data


data_dir = "/home/diogo/Diogo/Science/Scripts/packages/TriFusion_benchmarks/data/"
db_path = "/home/diogo/Diogo/TriFusion_testdata/benchmark.db"
res_path = "/home/diogo/Diogo/TriFusion_testdata/results.csv"
bench_dir = "/home/diogo/Diogo/TriFusion_testdata/benchmarks_out"
res = []

ds1 = join(data_dir, "614_protein")
ds2 = join(data_dir, "3093_protein")
ds3 = join(data_dir, "3093_141_protein")
ds4 = join(data_dir, "3093_376_protein")
ds5 = join(data_dir, "7378_dna")
ds6 = join(data_dir, "1_40_large")
ds7 = join(data_dir, "1_40_large_interleave")
ds8 = join(data_dir, "1_40_large_interleave_nex")
ds9 = join(data_dir, "1_376_large")
ds10 = join(data_dir, "1_376_1G")
ds11 = join(data_dir, "2_big_data")
ds12 = join(data_dir, "52285_loci")

ds_list = [[join(x, j) for j in os.listdir(x)] for x in [ds1, ds2, ds3, ds4,
                                                         ds5, ds6, ds7, ds8,
                                                         ds9, ds10, ds11, ds12]]

# ds_list = [[join(x, j) for j in os.listdir(x)] for x in [ds4main ]]

# rev_ds1 = join(data_dir, "614_protein_rev")
# rev_ds2 = join(data_dir, "3093_protein_rev")
# rev_ds3 = join(data_dir, "3093_141_protein_rev")
# rev_ds4 = join(data_dir, "3093_376_protein_rev")
# rev_ds5 = join(data_dir, "7378_dna_rev")
# rev_ds8 = join(data_dir, "2_big_data_rev")
# rev_ds11 = join(data_dir, "52285_loci_rev")


# rev_ds_list = [[join(x, j) for j in os.listdir(x) if j.endswith(".phy")] for
#                x in [rev_ds1, rev_ds2, rev_ds3, rev_ds4, rev_ds5, rev_ds8,
#                      rev_ds11]]
# part_files = [[join(x, j) for j in os.listdir(x) if not j.endswith(".phy")] for
#                x in [rev_ds1, rev_ds2, rev_ds3, rev_ds4, rev_ds5, rev_ds8,
#                      rev_ds11]]

# Filter data
flist = [["Postia_placenta"],
         ["Postia_placenta"],
         ["Postia_placenta"],
         ["Postia_placenta"],
         ["535_12"],
         ["Ang_30"],
         ["Ang_30"],
         ["Ang_30"],
         ["Postia_placenta"],
         ["Ang_30"],
         ["Ang_30"]]

class CleanUp(object):

    def __init__(self, func):

        self.func = func

    def __call__(self, *args, **kwargs):

        global res

        print("Clocking function {}".format(self.func.__name__))
        start_time = time.time()
        try:
            self.func(*args, **kwargs)
        except Exception as e:
            print(e)
            traceback.print_exc()
            #os.remove(db_path)
        finish = round(time.time() - start_time, 1)
        res.append(finish)
        print(finish)

        try:
            args[0].con.close()
        except AttributeError:
            print("aln not found")
            pass

        os.remove(db_path)


class GetResults(object):

    def __init__(self, func):
        self.func = func

    def __call__(self, *args, **kwargs):

        global res
        res = []

        self.func(*args, **kwargs)

        with open(res_path, "w") as fh:
            fh.write(",".join(map(str, res)))


@CleanUp
def read_alns(infiles):
    AlignmentList(infiles, sql_db=db_path)


@GetResults
def read_benchmark():

    for ds in ds_list:
        read_alns(ds)


@CleanUp
def convert_alns(aln_obj):
    aln_obj.write_to_file(["stockholm"], output_dir=bench_dir)


@CleanUp
def convert_alns_int(aln_obj):
    aln_obj.write_to_file(["nexus"], output_dir=bench_dir, interleave=True)

@CleanUp
def concatenate_alns(aln):
    aln.concatenate()
    #aln.write_to_file(["nexus"], output_dir=bench_dir)

@CleanUp
def collapse(aln):
    aln.collapse(dest=bench_dir, use_main_table=True)

@CleanUp
def consensus(aln):
    aln.consensus("Soft mask", single_file=True, use_main_table=True)

@CleanUp
def filter_contain_taxa(aln, tx_lsit):
    aln.filter_by_taxa(tx_lsit, "Contain")

@CleanUp
def filter_min_taxa(aln):
    aln.filter_min_taxa(80)

@CleanUp
def filter_missing_data(aln):
    aln.filter_missing_data(50, 75)

@CleanUp
def filter_codon(aln):
    aln.filter_codon_positions([True, True, False])

@CleanUp
def filter_variable(aln):
    aln.filter_segregating_sites(0, 200)

@CleanUp
def filter_informative(aln):
    aln.filter_informative_sites(0, 200)

@CleanUp
def code_gaps(aln):
    aln.code_gaps()

@CleanUp
def rev_concatenation(aln, part_file):
    partition = data.Partitions()
    partition.read_from_file(part_file)
    aln.alignments.values()[0].set_partitions(partition)
    aln.set_partition_from_alignment(aln.alignments.values()[0])
    aln.reverse_concatenate()

    # Post reverse ops
    print("Writing files")
    aln.write_to_file(["nexus"], output_dir=bench_dir)

@GetResults
def convert_benchmark():
    for p, ds in enumerate(ds_list):
        print("Profiling data set {}".format(p + 1))
        aln_obj = AlignmentList(ds, sql_db=db_path)
        # convert_alns(aln_obj)
        # convert_alns_int(aln_obj)
        # concatenate_alns(aln_obj)
        # collapse(aln_obj)
        # consensus(aln_obj)
        # filter_contain_taxa(aln_obj, flist[p])
        # filter_min_taxa(aln_obj)
        # filter_missing_data(aln_obj)
        # filter_codon(aln_obj)
        # filter_variable(aln_obj)
        # filter_informative(aln_obj)
        code_gaps(aln_obj)

@GetResults
def reverse_conc():
    for p, (ds, part_file) in enumerate(zip(rev_ds_list, part_files)):
        print("Profiling data set {}".format(p + 1))
        aln_obj = AlignmentList(ds, sql_db=db_path)
        rev_concatenation(aln_obj, part_file[0])

read_benchmark()
# convert_benchmark()
# reverse_conc()

# @profile
# def read_a():
#     AlignmentList(ds_list[0], sql_db=db_path)
#
# read_a()
