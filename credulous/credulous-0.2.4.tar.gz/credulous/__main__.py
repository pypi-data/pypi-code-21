from __future__ import absolute_import

from credulous import credulous

import argparse
import os

def main():
	parser = argparse.ArgumentParser(
		description="""
	Tool for generating API credentials. Google API is supported.
	<scopes> is a json with a list of scope URL. The list should be under
	scopes.google""")
	parser.add_argument('--secret',
		required=True,
		help='Path to your client secret json file')
	parser.add_argument('-c', '--credentials-format',
		action='store_true',
		required=False,
		help='Use for Google Credential File Format')
	parser.add_argument('-o', '--output-file',
		required=False,
		help='Specify outputfile')
	parser.add_argument('scopes')
	args = parser.parse_args()
	if args.output_file:
		output_file = args.output_file
	else:
		output_file = args.secret
	if args.credentials_format:
		credulousInstance = credulous.Credulous(
		  args.secret, args.scopes,
		  format_secrets=credulous.format_as_credentials,
	  	output_file=output_file)
	else:
		credulousInstance = credulous.Credulous(
			args.secret, args.scopes, output_file=output_file)
	try:
		credulousInstance.authenticate()
	except Exception as e:
		print("Failed with error: {}".format(e))

if __name__=='__main__':
	main()
