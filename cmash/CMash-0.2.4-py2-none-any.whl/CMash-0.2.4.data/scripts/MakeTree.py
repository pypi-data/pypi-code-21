# This script (to be imported to MinHash.py) will make a tree structure from a bunch of sketches, suitable for querying
from scipy.cluster.hierarchy import dendrogram, linkage, to_tree
import sys
import os
try:
	from CMash import MinHash as MH
except ImportError:
	try:
		import MinHash as MH
	except ImportError:
		sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
		from CMash import MinHash as MH

training_data = "/home/dkoslicki/Dropbox/Repositories/CMash/CMash/data/test2.h5"
sketches = MH.import_multiple_from_single_hdf5(training_data)

# Cluster the sketches based on jaccard + ward
A = MH.form_jaccard_matrix(sketches)
Z = linkage(A, 'ward')
dendrogram(Z)
tree = to_tree(Z)
tree.get_count()
tree.get_left()
tree.is_leaf()
tree.pre_order(lambda x: x.id)  # get the names of the nodes in the tree/subtree

# Put all the kmer counts in a dictionary
sketches_dicts = list()
for sketch_i in range(len(sketches)):
	kmer_dict = dict()
	for kmer in sketches[sketch_i]._kmers:
		kmer_dict[kmer] = True
	sketches_dicts.append(kmer_dict)

class Kmer_Tree(object):
	def __init__(self):
		self.left = None
		self.right = None
		self.data = None
		self.id = None

	def query(self, kmer):
		this_level = [self]
		locations = list()
		while this_level:
			next_level = list()
			for n in this_level:
				if kmer in n.data:
					if n.id:
						locations.append(n.id)
					else:
						next_level.append(n.left)
						next_level.append(n.right)
			this_level = next_level
		return locations

# Make the tree where nodes have dictionaries containing all the subsequent node k-mers
kmer_tree = Kmer_Tree()
kmer_tree.data = dict()
for sketch in sketches_dicts:
	kmer_tree.data.update(sketch)
this_level_query = [tree]
this_level_update = [kmer_tree]
while this_level_query:
	next_level_query = list()
	next_level_update = list()
	for (n_query, n_update) in zip(this_level_query, this_level_update):
		if n_query.get_left():
			n_update.left = Kmer_Tree()
			n_update.left.data = dict()
			for index in n_query.get_left().pre_order(lambda x: x.id):
				n_update.left.data.update(sketches_dicts[index])
			if n_query.get_left().is_leaf():
				n_update.left.id = n_query.get_left().id
			next_level_query.append(n_query.get_left())
			next_level_update.append(n_update.left)
		if n_query.get_right():
			n_update.right = Kmer_Tree()
			n_update.right.data = dict()
			for index in n_query.get_right().pre_order(lambda x: x.id):
				n_update.right.data.update(sketches_dicts[index])
			if n_query.get_right().is_leaf():
				n_update.right.id = n_query.get_right().id
			next_level_query.append(n_query.get_right())
			next_level_update.append(n_update.right)
	this_level_query = next_level_query
	this_level_update = next_level_update

kmer = 'GATGCAGGAAATGAA'
this_level = [kmer_tree]
locations = list()
while this_level:
	next_level = list()
	for n in this_level:
		if kmer in n.data:
			if n.id:
				locations.append(n.id)
			else:
				next_level.append(n.left)
				next_level.append(n.right)
	this_level = next_level



reload(MH)
CE1 = MH.CountEstimator(n=5, max_prime=1e10, ksize=3, save_kmers='y', input_file_name="CMash/data/PRJNA67111.fna")
CE2 = MH.CountEstimator(n=5, max_prime=1e10, ksize=3, save_kmers='y', input_file_name="CMash/data/PRJNA32727.fna")
CE3 = MH.CountEstimator(n=5, max_prime=1e10, ksize=3, save_kmers='y', input_file_name="CMash/data/PRJNA298068.fna")
CEs = [CE1, CE2, CE3]
tree = MH.make_tree(CEs)
kmer = "ATC"
res = tree.query(kmer)

all_dict = dict()
for sketch in sketches:
	for kmer in sketch._kmers:
		all_dict[kmer] = True

def chunks(l, n):
	"""Yield successive n-sized chunks from l."""
	for i in range(0, len(l), n):
		yield l[i:i + n]

tree_of_dicts = list()
for n in range(int(np.floor(np.log2(len(sketches))))):
	for indicies in chunks(range(len(sketches)), 2**n):
		insert_dict = dict()
		#for index in indicies:
		#	for kmer in sketches[index]._kmers:
		#		insert_dict[kmer] = True
		tree_of_dicts.append(insert_dict)
