#!/usr/bin/env python3
"""Console interface"""
import argparse

def get_arguments():
	"Return paths to text and rules' files getted from console"
	parser = argparse.ArgumentParser()

	parser.add_argument("-t", "--target", help="Path to file with target text", default="")
	parser.add_argument("-r", "--rules", help="Path to file with rules", default="")

	args = parser.parse_args()
	return (args.target, args.rules)
