from i18n_base import get_files_in_dir_with_subdirs, ignore_files, iterate_items, convert_to_unicode
import pandas as pd
import requests
import json
import os
import logging
log = logging.getLogger('qordoba')

KEY_COUNT = 0
"""
1. test with subdirs etc. ob das get_files_in_dir_with_subdirs wirklich functioniert auf allen ebenen
2. in index_lookup. instead of == could say 99%match. e.g. "Ruby is fun." vs "Ruby is fun"
"""
def generate_new_key(value):
	global KEY_COUNT
	KEY_COUNT += 1
	r = requests.post('https://qordoba-devel.appspot.com/convert', data = {'text': value})
	keywords = r.json()["keywords"]
	key = '.'.join(keywords)
	return key

def strip_qoutes(string):
    if string[:1] == "'" and string[-1] == "'" or string[:1] == '"' and string[-1] == '"':
        string = string[1:-1].strip()
        string = strip_qoutes(string)
    return string

def get_all_key_values(json_dictionary, path, c):
	""""iteratsed through (nested) dict and gives back joined keys (joined with .) and their values
	input should be json_dictionary,empty list(), empty dict()
	"""
	for key, value in iterate_items(json_dictionary):

		path.append(key)
		if type(value) is not dict:
			s_path = '.'.join(path)
			c[s_path] = value
		else:
			get_all_key_values(value, path, c)
		path.pop()

	return c

def get_nested_dictionary(file):
	if 'json' in file[-4:]:
		json_data = json.loads(open(file, "r").read())
		return json_data


def accumulate_existing_i18n_key_value_pairs_from_all_files(i18n_file_list):
	"""
	Getting key values from json or nested json dict
	"""
	sum_of_keys_values_from_i18n_files = dict()
	for file_list in i18n_file_list:
		#this is important due to subdirs
		for file in file_list:
			log.info('Reading in existing i18n-file `{}`.'.format(file))
			dictionary = get_nested_dictionary(file)
			key_value_pairs = get_all_key_values(dictionary, list(), dict())
			key_value_pairs = convert_to_unicode(key_value_pairs)
			sum_of_keys_values_from_i18n_files[file] = key_value_pairs

	# return self.convert(sum_of_keys_values_from_i18n_files)
	return sum_of_keys_values_from_i18n_files

def index_lookup(stringLiteral, localization_k_v):
	# checks if stringLiteral exists in values, gives back corresponding key or None
	for i18n_file in localization_k_v:
		for key, value in localization_k_v[i18n_file].items():
			if value.strip() == stringLiteral.strip():
				return key, i18n_file
			if key.strip() == stringLiteral.strip():
				return key, i18n_file
	return (None, None)

def add_existing_i18n_keys_to_df(existing_i18nfiles, df):
	"""Reading in list of i18n-filepaths and current df.
	Giving out the new df with existing keys added.
	"""
	#validating that the file is a proper i18n-json format
	i18n_file_list = []
	for loc_file in existing_i18nfiles: 
		if not loc_file.startswith('.') and loc_file.endswith('json'):
			i18n_file_list.append(existing_i18nfiles)
		else:
			log.info("Skipping file `{}`. Not a valid json i18n-file".format(loc_file))

	log.info(" ... searching for existing keys.")
	#accumulate all key-values-pairs from the i18n-file
	existing_i18n_key_value_pairs = accumulate_existing_i18n_key_value_pairs_from_all_files(i18n_file_list)
	
	for column in df:
			for i in range(len(df.index)):
				#stripping quotes from start and end of sting
				try:

					if index_lookup(df[column][i]["value"], existing_i18n_key_value_pairs) == (None, None):
						continue
					else:
						key, i18n_file = index_lookup(df[column][i]["value"], existing_i18n_key_value_pairs)
						df[column][i]["existing_key"] = {"key":key, "i18n_file": i18n_file}
				except TypeError:
					continue
	

				# df['existing_keys'], df['existing_localization_file'] = izip(*df.iloc[:, -1].apply(lambda x: self.index_lookup(x, localization_k_v)))
	return df


def generate(_curdir, report_dir=None, existing_i18nfiles=None):
	""" Given localization files exists, gives back existing keys.
	Further, generating new keys for values
	"""
	report_files = get_files_in_dir_with_subdirs(report_dir)
	report_files = ignore_files(report_files)
	
	for single_report_path in report_files:
		"""
	    Validate report
	    """
		if not single_report_path.endswith(".json"):
			continue

		log.info("  " + u"\U0001F4AB" + u"\U0001F52E" + " .. starting to generate new keys for you - based on the extracted Strings from your files.\n (This could Take some time) \n\n ")
		log.info("\b")

		df = pd.read_json(single_report_path)
		for column in df:
			for i in range(len(df.index)):
				try:
					#stripping quotes from start and end of sting
					df[column][i]["value"] = strip_qoutes(df[column][i]["value"])
					key = generate_new_key(df[column][i]["value"])
					df[column][i]["generated_key"] = {"key": key}
				except TypeError:
					continue
				if KEY_COUNT%20 == 0:
					log.info("{} keys created ".format(KEY_COUNT))

		if existing_i18nfiles:
			i18n_files = get_files_in_dir_with_subdirs(existing_i18nfiles)
			i18n_files = ignore_files(i18n_files)
			df = add_existing_i18n_keys_to_df(i18n_files, df)
		
		log.info("Process completed. " + u"\U0001F680" + u"\U0001F4A5")
		#report ueberschreiben
		os.remove(single_report_path)
		df.to_json(single_report_path)

# python cli.py i18n-generate -r /Users/franzi/Workspace/artifacts_stringExtractor/testing/test_report --existing_i18nfiles /Users/franzi/Workspace/artifacts_stringExtractor/testing/test_i18n_existing --traceback


