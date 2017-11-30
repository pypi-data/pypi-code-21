import ctypes
import random

try:
	valeclib = ctypes.CDLL('libvalec.so')
except:
	raise OSError,"You must install the valection library before using this package. It is available at labs.oicr.on.ca/boutros-lab/software/valection."

def run_directed_sampling(*args, **kwargs):
	"""
	Runs the directed sampling method

	Arguments:
	
	- budget (integer)
	- filename containing calls
	- output filename
	- random seed (optional)
	"""
	run_method("run_directed_sampling", *args, **kwargs)

def run_random_sampling(*args, **kwargs):
	"""
	Runs the random sampling method

	Arguments:
	
	- budget (integer)
	- filename containing calls
	- output filename
	- random seed (optional)
	"""
	run_method("run_random_sampling", *args, **kwargs)

def run_equal_per_caller(*args, **kwargs):
	"""
	Runs the equal per caller sampling method

	Arguments:
	
	- budget (integer)
	- filename containing calls
	- output filename
	- random seed (optional)
	"""
	run_method("run_equal_per_caller", *args, **kwargs)

def run_equal_per_overlap(*args, **kwargs):
	"""
	Runs the equal per overlap sampling method

	Arguments:
	
	- budget (integer)
	- filename containing calls
	- output filename
	- random seed (optional)
	"""
	run_method("run_equal_per_overlap", *args, **kwargs)

def run_increasing_with_overlap(*args, **kwargs):
	"""
	Runs the increasing with overlap sampling method

	Arguments:
	
	- budget (integer)
	- filename containing calls
	- output filename
	- random seed (optional)
	"""
	run_method("run_increasing_with_overlap", *args, **kwargs)

def run_decreasing_with_overlap(*args, **kwargs):
	"""
	Runs the increasing with overlap sampling method

	Arguments:
	
	- budget (integer)
	- filename containing calls
	- output filename
	- random seed (optional)
	"""
	run_method("run_decreasing_with_overlap", *args, **kwargs)

def run_method(selection_method, budget, calls_filename, output_filename, seed=None):
	if seed is None:
		seed =  random.randint(0, 100000)

	func = getattr(valeclib, selection_method)
	func(
		budget,
		calls_filename.encode('ascii'),
		output_filename.encode('ascii'),
		seed,
	)