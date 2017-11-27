# -*- coding: utf-8 -*-

"""Console script for yake."""

import click
from yake.yake import YakeKeywordExtractor

@click.command()
@click.option('--ngram_size', default=3, help='Maximum ngram size')
@click.option('--input_file', help='Input file')
@click.option('--language', default="en",help='Language')

def keywords(input_file, language, ngram_size):
	#lan="en", n=3, dedupLim=0.8, windowsSize=2, top=20, features=None

	with open(input_file) as fpath:
		text_content = fpath.read()

		myake = YakeKeywordExtractor(lan=language,n=ngram_size)
		results = myake.extract_keywords(text_content)

		for kw in results:
			print(kw[0] +", "+ kw[1])

if __name__ == "__main__":
	main()
