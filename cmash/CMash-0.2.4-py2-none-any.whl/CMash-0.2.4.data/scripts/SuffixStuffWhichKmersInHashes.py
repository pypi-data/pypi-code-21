# I have checked these results against the following, and they agree!
# LC_ALL=C cat kmers.txt | xargs -I{} grep -c -m1 -F {} 1Mil.fastq | awk '{sum+=$1}END{print sum}'
# They should match the results given in the csv file

# IDEA: do one pass with the largest k-mer size, use that to set the threshold, then do the full thing
# to get all the k-mer sizes
import khmer
import tst  # t=tst.TST(); t['a']=1; t['aaa']=2; t['acc']=3; t.prefix_match('aa',None,tst.ListAction()); # returns [1,2]
import numpy as np
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
import multiprocessing
import ctypes
import pandas as pd

#training_data = "/home/dkoslicki/Dropbox/Repositories/CMash/CMash/data/test2.h5"
training_data = "/home/dkoslicki/Dropbox/Repositories/CMash/CMash/data/AllVirusSketches.h5"
#training_data = "/home/dkoslicki/Dropbox/Repositories/CMash/CMash/data/AllRepoPhlAnFileNames.h5"  # The big one
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

max_ksize = ksizes.pop()
#k_range = range(10, max_ksize + 1)
k_range = [10,15]

# For memory issues
sketches = sketches[0:10000]


# Get names of training files for use as rows in returned tabular data
training_file_names = []
for i in range(len(sketches)):
	training_file_names.append(sketches[i].input_file_name)


# Make the tst tree
write_to = '/tmp/tst_tree'
if os.path.exists(write_to):
	tree = tst.TST()
	tree.read_from_file(write_to)
else:
	tree = tst.TST()  # tst array
	for i in range(len(sketches)):
		for kmer_index in range(len(sketches[i]._kmers)):
			kmer = sketches[i]._kmers[kmer_index]
			tree[kmer + 'x' + str(i) + 'x' + str(kmer_index)] = True  # format here is kmer+x+hash_index+kmer_index
	#tree.write_to_file(write_to)

# For initial testing, put all the k-mers in a dictionary too
#all_kmers_dict = dict()
#for sketch in sketches:
#	for kmer in sketch._kmers:
#		for ksize in k_range:
#			all_kmers_dict[kmer[0:ksize]] = True  # put all the k-mers and the appropriate suffixes in

# Test set instead
all_kmers_dict_set = set()
for sketch in sketches:
	for kmer in sketch._kmers:
		for ksize in k_range:
			all_kmers_dict_set.add(kmer[0:ksize])  # put all the k-mers and the appropriate suffixes in


class Counters(object):
	# This class is basically an array of counters (on the same basis as the sketches)
	# it's used to keep track (in a parallel friendly way) of which streamed k-mers went into the training file sketches
	def __init__(self):
		self.ksize = max_ksize
		N = len(sketches)
		to_share = multiprocessing.Array(ctypes.c_bool, N * num_hashes * len(k_range))  # vector
		to_share_np = np.frombuffer(to_share.get_obj(), dtype=ctypes.c_bool)   # get it
		self.vals = to_share_np.reshape(N, num_hashes, len(k_range))
		self.lock = Lock()  # don't need since I don't care about collisions (once matched, always matched)

	def increment(self, hash_index, kmer_index, k_size_loc):
		self.vals[hash_index, kmer_index, k_size_loc] = True  # array

	def value(self, hash_index, k_size_loc):
		return np.sum(self.vals[hash_index, :, k_size_loc])  # get the number of True's

	def process_seq(self, seq):
		# TO DO: the only thing this doesn't do so far is note that when you decrease the ksize, the sketch gets duplicate entries
		# I will need to see if I can post-process these, or somehow handle them before updating the counters...
		# perhaps take all the matches for a sketch and see if the prefixes of the keys match
		# do this before incrementing the counters
		for k_size_loc in range(len(k_range)):  # could do this more efficiently by putting this in the inner loop
			ksize = k_range[k_size_loc]
			for i in range(len(seq) - ksize + 1):
				kmer = seq[i:i + ksize]
				#if kmer in all_kmers_dict:
				if kmer in all_kmers_dict_set:
					tuples = tree.prefix_match(kmer, None, tst.TupleListAction())
					#del all_kmers_dict[kmer]  # Drop from the pre-filter list, since it will subsequently not be used
					all_kmers_dict_set.remove(kmer)
					hash_loc_kmer_loc = []
					for item in tuples:
						split_string = item[0].split('x')
						hash_loc_kmer_loc.append((int(split_string[1]), int(split_string[2])))  # first is the hash location, second is which k-mer
					if len(hash_loc_kmer_loc) > 0:
						for hash_index, kmer_index in hash_loc_kmer_loc:
							self.increment(hash_index, kmer_index, k_size_loc)


def q_func(queue, counter):
	# Worker function to process the reads in the queue
	while True:
		record = queue.get()
		if record is False:  # In case I need to pass a poison pill
			return
		else:
			counter.process_seq(record)

if __name__ == '__main__':
	counter = Counters()
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
	#print("counter: %d" % counter.value(9))

	# export the results
	intersection_counts = np.zeros((len(sketches), len(k_range)))
	for sketch_index in range(len(sketches)):
		for k_size_loc in range(len(k_range)):
			intersection_counts[sketch_index, k_size_loc] = counter.value(sketch_index, k_size_loc)

	results = dict()
	for k_size_loc in range(len(k_range)):
		ksize = k_range[k_size_loc]
		key = 'k=%d' % ksize
		results[key] = intersection_counts[:, k_size_loc]
	df = pd.DataFrame(results, map(os.path.basename, training_file_names))
	max_key = 'k=%d' % k_range[-1]
	intersection_threshold = 0  # needs to be bigger than this
	filtered_results = df[df[max_key] > intersection_threshold].sort_values(max_key, ascending=False)
	filtered_results.to_csv(results_file, index=True, encoding='utf-8')
	#df.to_csv(results_file, index=True, encoding='utf-8')

	# TO DO: Post-process the counters to remove counts from repeat entries (for smaller k-mer sizes)


# To check results using bash
#for sketch_index in range(len(sketches)):
#	if os.path.basename(sketches[sketch_index].input_file_name) == 'G000312105.fna':
#		print(sketch_index)
#		to_print_index = sketch_index

#with open('/home/dkoslicki/Dropbox/Repositories/CMash/CMash/data/kmers.txt','w') as fid:
#	for kmer in sketches[to_print_index]._kmers:
#		fid.write('%s\n' % kmer)


