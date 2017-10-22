# With bloom filters as nodes instead of dictionaries, problem here is it takes way too long to make all the
# bloom filters, would probably be better to do it off line, then write to file
# could also look at unioning bloom filters using f1.union(f2). NOPE! Uses way too much ram...
import pybloom_live  # takes too long to make them all
import fastbloom  # faster to make, but won't clear memory for some reason, also, weird bug with kmer = kmer+'' required
import peloton_bloomfilters  # works, and sharedmem is nice since it automatically saves the bloom filter, but has non-deterministic behavior
# peloton non-shared may be a winner! Under 42% mem for the big one, 136user 1:29elapsed
# Using khmer has the advantage of: no extra packages, fast, low mem, BUT I can only use a single fixed k-mer size
# khmer on the big one: 166user, 2:11elapsed, 39.8% mem
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
import itertools
import tempfile


class Kmer_Bloom_Tree(object):
	def __init__(self):
		self.left = None
		self.right = None
		self.data = None  # this should be a dictionary of the k-mer counts at this node
		self.id = None  # this is None, except for the leaf nodes, in which case it's supposed to be the index
		#  in the global sketches

	def query(self, kmer):  # Breadth first search for the k-mer
		#if self.data:
		#	test_kmer = self.data.iterkeys().next()
		#	if len(test_kmer) != len(kmer):
		#		raise Exception("Query k-mer length %d different than tree k-mer length %d" % (len(kmer), len(test_kmer)))
		#else:
		#	raise Exception("Tree has no data in it, cannot be queried")
		#kmer = kmer + ''  # ONLY FOR FASTBLOOM
		this_level = [self]  # start at the root
		locations = list()  # locations of the tips containing the k-mer
		while this_level:
			next_level = list()  # next level down the tree
			for n in this_level:
				#if kmer in n.data:
				if n.data.get(kmer)>0:  # khmer bloom filter
					if n.id is not None:  # if the node is labeled, add it
						locations.append(n.id)
					else:
						if n.left:  # if there is a left child node, add it to the next level to search
							next_level.append(n.left)
						if n.right:
							next_level.append(n.right)
			this_level = next_level
		return locations

	def insert(self, sketches, left_list, right_list):
		# This function will insert the sketches into the tree, left child node corresponding to the indicies
		# in the left_list (and same with the right)
		# As I have currently designed it, the left_list and right_list will be progressively bisected
		# (see 0:len(left_list)/2 part), so it assumes that the given left_list and right_list give the ordering
		# of the nodes
		i = 0
		for update_list in left_list, right_list:
			# create a dictionary of all the k-mers supposed to go in the left/right node
			#update_dict = pybloom_live.BloomFilter(capacity=2*len(left_list)*len(sketches[0]._kmers), error_rate=0.001)  # pybloom_live
			#update_dict = fastbloom.BloomFilter(2 * len(left_list) * len(sketches[0]._kmers), 0.001)  # fastbloom
			# shared memory bloom filter is nice since it automatically saves it, but it appears to have some weird non-deterministic behavior
			#update_dict = peloton_bloomfilters.SharedMemoryBloomFilter('/tmp/bloom/leaf'+str(update_list[0])+'_'+str(len(update_list)), 2 * len(left_list) * len(sketches[0]._kmers), 0.001)  # peloton
			#update_dict = peloton_bloomfilters.BloomFilter(2 * len(left_list) * len(sketches[0]._kmers), 0.001)  # peloton
			res = optimal_size(len(left_list) * len(sketches[0]._kmers), fp_rate=0.001)
			update_dict = khmer.Nodegraph(ksize, res.htable_size, res.num_htables)
			#############################################
			for index in update_list:
				for kmer in sketches[index]._kmers:
					if len(kmer) > 0:  # ignore '' k-mers (from really short database genomes)
						#update_dict[kmer] = True
						#kmer = kmer + ''  # ONLY FOR FASTBLOOM
						update_dict.add(kmer)
			##############################################
			update_tree = Kmer_Bloom_Tree()  # initialize the left tree
			if update_dict:  # if the insert_dict is not empty
				update_tree.data = update_dict
				if len(update_list) == 1:  # if the left list is terminal
					update_tree.id = update_list[0]  # assign it the correct index
			if i == 0:  # if it's the left guy
				if len(left_list) > 1:
					update_tree.insert(sketches, left_list[0:(len(left_list)/2)], left_list[(len(left_list)/2):])
					self.left = update_tree
				else:
					self.left = update_tree
			else:  # if it's the right guy
				if len(right_list) > 1:
					update_tree.insert(sketches, right_list[0:(len(right_list) / 2)], right_list[(len(right_list) / 2):])
					self.right = update_tree
				else:
					self.right = update_tree
			i += 1  # iterate i

	def make_tree(self, sketches, index_list):
		# This function will initialize the tree
		# putting all the index_list kmers in the root dictionary, and then progressively bisecting the index_list
		# First, make the root node (all k-mers in sketches at the indices given in index_list)
		#update_dict = pybloom_live.BloomFilter(capacity=2*len(index_list)*len(sketches[0]._kmers), error_rate=0.001)  # pybloom_live
		#update_dict = fastbloom.BloomFilter(2 * len(index_list) * len(sketches[0]._kmers), 0.001)  # fastbloom
		#update_dict = peloton_bloomfilters.SharedMemoryBloomFilter('/tmp/bloom/root', 2 * len(index_list) * len(sketches[0]._kmers), 0.001)  # peloton
		#update_dict = peloton_bloomfilters.BloomFilter(2 * len(index_list) * len(sketches[0]._kmers), 0.001)  # peloton
		res = optimal_size(len(index_list) * len(sketches[0]._kmers), fp_rate=0.001)
		update_dict = khmer.Nodegraph(ksize, res.htable_size, res.num_htables)
		#################################################
		for index in index_list:
			sketch = sketches[index]
			for kmer in sketch._kmers:
				if len(kmer) > 0:  # ignore '' k-mers
					#update_dict[kmer] = True
					#kmer = kmer+''  # ONLY FOR FASTBLOOM
					update_dict.add(kmer)
		##################################################
		self.data = update_dict
		# Then bisect the index_list and create the child nodes
		self.insert(sketches, index_list[0:len(index_list)/2], index_list[len(index_list)/2:])

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
tree = Kmer_Bloom_Tree()
tree.make_tree(sketches, range(len(sketches)))

# For initial testing, put all the k-mers in a dictionary too
all_kmers_dict = dict()
for sketch in sketches:
	for kmer in sketch._kmers:
		all_kmers_dict[kmer] = True


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
			if kmer in all_kmers_dict:  # super fast initial testing to see if the k-mer is in the tree
				indicies = tree.query(kmer)
				if len(indicies) > 0:
					for index in indicies:
						self.increment(index)


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


