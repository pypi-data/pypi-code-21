import khmer
import numpy as np
from khmer.khmer_args import optimal_size
import os
import sys
# The following is for ease of development (so I don't need to keep re-installing the tool)
try:
	from CMash import MinHash as MH
except ImportError:
	try:
		import MinHash as MH
	except ImportError:
		sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
		from CMash import MinHash as MH
import time
from multiprocessing import Process, Value, Lock
import pandas as pd
from multiprocessing import Pool  # Much faster without dummy (threading)
import multiprocessing
import threading
from itertools import *
import argparse
import screed
import itertools

training_data = "/home/dkoslicki/Dropbox/Repositories/CMash/CMash/data/test.h5"
num_threads = 8
query_file = "/home/dkoslicki/Dropbox/Repositories/CMash/CMash/data/1Mil.fastq"
results_file = "/home/dkoslicki/Dropbox/Repositories/CMash/CMash/data/test_stream.csv"
force = True
coverage_threshold = 0.01

# Import data and error checking
# Query file
if not os.path.exists(query_file):
	raise Exception("Query file %s does not exist." % query_file)
if not os.path.exists(training_data):
	raise Exception("Training/reference file %s does not exist." % training_data)
# Training data
#global sketches
sketches = MH.import_multiple_from_single_hdf5(training_data)
ksizes = set()
if sketches[0]._kmers is None:
	raise Exception(
		"For some reason, the k-mers were not saved when the database was created. Try running MakeDNADatabase.py again.")
num_hashes = len(sketches[0]._kmers)
for i in range(len(sketches)):
	sketch = sketches[i]
	if sketch._kmers is None:
		raise Exception(
			"For some reason, the k-mers were not saved when the database was created. Try running MakeDNADatabase.py again.")
	if len(sketch._kmers) != num_hashes:
		raise Exception("Unequal number of hashes for sketch of %s" % sketch.input_file_name)
	ksizes.add(sketch.ksize)
	if len(ksizes) > 1:
		raise Exception(
			"Training/reference data uses different k-mer sizes. Culprit was %s." % (sketch.input_file_name))

ksize = ksizes.pop()


# Get names of training files for use as rows in returned tabular data
training_file_names = []
for i in range(len(sketches)):
	training_file_names.append(sketches[i].input_file_name)

# Put all the k-mers in dictionaries
sketches_dicts = list()
for sketch_i in range(len(sketches)):
	kmer_dict = dict()
	for kmer in sketches[sketch_i]._kmers:
		kmer_dict[kmer] = True
	sketches_dicts.append(kmer_dict)


class Counters(object):
	def __init__(self, initval=0):
		self.ksize = ksize
		N = len(sketches)
		self.vals = [0] * N  # initialize counters
		for i in range(N):
			self.vals[i] = Value('i', initval)  # all set to 0
			self.lock = Lock()

	def increment(self, i):
		with self.lock:
			self.vals[i].value += 1

	def value(self, i):
		with self.lock:
			return self.vals[i].value

	def process_seq(self, seq):
		for i in range(len(seq) - self.ksize + 1):  # this line and the next are what causes it to slow down
			kmer = seq[i:i + ksize]
			for sketch_i in range(len(sketches_dicts)):
				if kmer in sketches_dicts[sketch_i]:
					self.increment(sketch_i)

	def process_record(self, record):
		seq = record.sequence
		self.process_seq(seq)

	def process_chunk(self, chunk):
		for record in chunk:
			self.process_record(record)

def func(read):
	counter.process_record(read)

if __name__ == '__main__':
	counter = Counters(0)
	#procs = [Process(target=func, args=(counter,)) for i in range(10)]
	#for p in procs: p.start()
	#for p in procs: p.join()
	#pool = Pool()
	#num_chunks = 10
	#rparser = khmer.ReadParser(query_file)
	#chunks = itertools.groupby(rparser)
	#while True:
	#	groups = [list(chunk) for key, chunk in itertools.islice(chunks, num_chunks)]
	#	if groups:
	#		result = pool.map(func, groups)
	#	else:
	#		break

	#pool.close()
	#pool.join()

	chunksize = 10000
	num_threads = 8
	pool = Pool(num_threads)
	#rparser = khmer.ReadParser(query_file)
	#for chunk in iter(lambda: list(itertools.islice(rparser, chunksize * num_threads)), []):
	#	chunk = iter(chunk)
	#	pieces = list(iter(lambda: list(itertools.islice(chunk, chunksize)), []))
	#	result = pool.map(func, pieces)
	fid = screed.open(query_file)
	records = list()
	i = 0
	for record in fid:
		records.append(record)
		i += 1
		if i>10000:
			break
	pool.map(func, records)
	print counter.value(9)
	#pool.map(func, records)
	#pool.close()
	#pool.join()
	#print counter.value(9)

#group = list()
#i = 0
#for record in rparser:
#	group.append(record)
#	i += 1
#	if i > 10000:
#		break
#func(group)

# Clustering and tree stuff
A = MH.form_jaccard_matrix(sketches)
AD = 1-A
from scipy.cluster.hierarchy import dendrogram, linkage, to_tree
Z = linkage(A, 'ward')
dendrogram(Z)
tree = to_tree(Z)
tree.get_count()
tree.get_left()
tree.is_leaf()
tree.pre_order(lambda x: x.id)

# Debug Nathan's example
# python ~/Dropbox/Repositories/CMash/scripts/MakeDNADatabase.py viruses-filenames.txt test.h5
test = MH.import_multiple_from_single_hdf5('/home/dkoslicki/Dropbox/Repositories/CMash/CMash/data/Nathan/test/test.h5')

CE1 = MH.CountEstimator(n=5, max_prime=1e10, ksize=3, save_kmers='y')
CE2 = MH.CountEstimator(n=5, max_prime=1e10, ksize=3, save_kmers='y')
CE3 = MH.CountEstimator(n=5, max_prime=1e10, ksize=3, save_kmers='y')
seq1 = 'tacgactgatgcatgatcgaactgatgcactcgtgatgc'
seq2 = 'tacgactgatgcatgatcgaactgatgcactcgtgatgc'
seq3 = 'ttgatactcaatccgcatgcatgcatgacgatgcatgatgtacgactgatgcatgatcgaactgatgcactcgtgatgczxerqwewdfhg'
CE1.add_sequence(seq1)
CE2.add_sequence(seq2)
CE3.add_sequence(seq3)
A = MH.form_jaccard_count_matrix([CE1, CE2, CE3])