#! /usr/bin/env python
# This script will import a training database and stream the entire sample through, classifying k-mers as it goes
# inspired by: https://genomeinformatics.github.io/mash-screen/
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
#from multiprocessing import Queue
from Queue import Queue
from sklearn.cluster import dbscan

#training_data = "/home/dkoslicki/Dropbox/Repositories/CMash/CMash/data/test2.h5"
#training_data = "/home/dkoslicki/Dropbox/Repositories/CMash/CMash/data/AllVirusSketches.h5"
training_data = "/home/dkoslicki/Dropbox/Repositories/CMash/CMash/data/AllRepoPhlAnFileNames.h5"  # The big one
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


# Reduce the number of sketches for RAM testing
sketches = sketches[0:10000]

# Put all the k-mers in a tree
tree = MH.Kmer_Tree()
tree.make_tree(sketches, range(len(sketches)))


class Counters(object):
	# This class is basically an array of counters (on the same basis as the sketches)
	# it's used to keep track (in a parallel friendly way) of which streamed k-mers went into the training file sketches
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
			indicies = tree.query(kmer)
			if len(indicies) > 0:
				for index in indicies:
					self.increment(index)

	def process_record(self, record):
		seq = record.sequence
		self.process_seq(seq)

	def process_chunk(self, chunk):
		for record in chunk:
			self.process_record(record)


def q_func(queue, counter):
	# Worker function to process the reads in the queue
	while True:
		record = queue.get()
		if record is False:  # In case I need to pass a poison pill
			return
		else:
			counter.process_seq(record)
		#queue.task_done()

if __name__ == '__main__':
	counter = Counters(0)
	# Start the q
	queue = multiprocessing.Queue()
	ps = list()
	for i in range(num_threads):
		p = multiprocessing.Process(target=q_func, args=(queue, counter))
		p.daemon = True
		p.start()
		ps.append(p)

	# populate the queue
	fid = khmer.ReadParser(query_file)  # This is faster than screed
	i = 0
	for record in fid:  # I need to somehow get screed to properly put stuff in the queue
		seq = record.sequence
		queue.put(seq)
		i += 1
		if i % 10000 == 0:
			print("Read in %d sequences" % i)

	# Wait for everything to finish
	while True:
		if queue.empty():
			break
		else:
			print("Sequences left: %d" % queue.qsize())
			time.sleep(5)
	queue.close()
	queue.join_thread()

	# check the results
	print("counter: %d" % counter.value(9))

