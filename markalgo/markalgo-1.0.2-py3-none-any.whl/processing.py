#!/usr/bin/env python3
"Replacement algorithm"
import logging

def process_file(file, rules):
	"Process file with given set of rules"
	return process_text(file.read(), rules)


def process_text(text, rules):
	"Process given text with given set of rules"
	is_final_step = False
	result = text
	while not is_final_step:
		result, is_final_step = _process_step(result, rules)
	return result


def _process_step(text, rules):
	for _rule in rules:
		result = _rule.process_text(text)
		if result[1]:
			logging.debug("Rule %s was succesfully used, result:%s",
						_rule,
						result[0])
			return (result[0], _rule.final)
	return (text, True)
