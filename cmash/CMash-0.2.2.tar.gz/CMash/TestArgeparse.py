import argparse
import multiprocessing
import os

def main():
	parser = argparse.ArgumentParser(description="This is a description of the program", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument('-p', '--prime', help='Prime (for modding hashes)', default=9999999999971)
	parser.add_argument('-f', '--force', action="store_true", help="Force overwriting of results")
	parser.add_argument('-t', '--threads', type=int, help="Number of threads to use", default=multiprocessing.cpu_count())
	parser.add_argument('-n', '--num_hashes', type=int, help="Number of hashes to use.", default=500)
	parser.add_argument('-k', '--k_size', type=int, help="K-mer size", default=21)
	parser.add_argument('in_file', help="Input file: file containing file names of training genomes.")
	parser.add_argument('out_file', help='Output file (in HDF5 format)')
	args = parser.parse_args()

	print(args.prime)
	print(args.force)
	print(args.threads)
	print(args.num_hashes)
	print(args.k_size)
	print(args.in_file)
	print(args.out_file)

if __name__ == "__main__":
	main()
