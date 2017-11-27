import collections
import csv

import openpyxl


def csv_to_dict(filepath, key_cols):
	"""
	Parse a csv file.  Return a dict with key_cols as the keys.  For example
	if the key_cols were ('A', 'B', 'C') the output would be:
	output[(A, B, C)] = fields
	where A, B, and C are the values of the respective columns on a given line and
	fields is a dict mapping the other column names to the values from that line.
	"""
	out = {}
	with open(filepath) as infile:
		reader = csv.DictReader(infile)
		for line in reader:
			values = dict(line)
			key = tuple([values.pop(key_col) for key_col in key_cols])
			out[key] = values
	return out


def sort_dict(d, key=None):
	"""Return an OrderedDict of d sorted."""
	out = collections.OrderedDict()
	for k in sorted(d, key=key):
		out[k] = d[k]
	return out


def group_dicts_by(dict_list, key):
	agged_data = collections.defaultdict(list)
	for d in dict_list:
		agged_data[d[key]].append(d)
	return agged_data


def xlsx_dict_reader(filepath):
	wb = openpyxl.load_workbook(filepath)
	ws = wb.active
	header_row = None
	for row in ws.rows:
		row_values = [cell.value for cell in row]
		if header_row is None:
			header_row = row_values
		else:
			yield dict(zip(header_row, row_values))
