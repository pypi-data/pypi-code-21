#!/usr/bin/env python3
"""Main module """
import logging

from markalgo import console
from markalgo import processing
from markalgo import rules

def main():
	"""Entry point for the application script"""
	target_path, rules_path = console.get_arguments()
	logging.info("Target is on the path %s", target_path)
	logging.info("Rules is on the path %s", rules_path)
	with open(rules_path) as rule_file:
		rules_list = rules.read_all_rules_from_csv_file(rule_file)
	with open(target_path) as file:
		print("Result: {}".format(processing.process_file(file, rules_list)))


main()
