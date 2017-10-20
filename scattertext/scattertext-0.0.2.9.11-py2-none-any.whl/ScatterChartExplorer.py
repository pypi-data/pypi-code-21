import numpy as np

from scattertext import ScatterChart
from scattertext import percentile_alphabetical
from scattertext.Corpus import Corpus
from scattertext.DocsAndLabelsFromCorpus import DocsAndLabelsFromCorpus, DocsAndLabelsFromCorpusSample


class ScatterChartExplorer(ScatterChart):
	def __init__(self,
	             corpus,
	             **kwargs):
		'''See ScatterChart.  This lets you click on terms to see what contexts they tend to appear in.

		'''
		assert isinstance(corpus, Corpus)
		ScatterChart.__init__(self, corpus, **kwargs)

	def to_dict(self,
	            category,
	            category_name=None,
	            not_category_name=None,
	            scores=None,
	            metadata=None,
	            max_docs_per_category=None,
	            transform=percentile_alphabetical,
	            alternative_text_field=None):
		'''

		Parameters
		----------
		category : str
			Category to annotate.  Exact value of category.
		category_name : str, optional
			Name of category which will appear on web site. Default None is same as category.
		not_category_name : str, optional
			Name of ~category which will appear on web site. Default None is same as "not " + category.
		scores : np.array, optional
			Scores to use for coloring.  Defaults to None, or np.array(self.term_doc_matrix.get_scaled_f_scores(category))
		metadata, None or array-like.
		  List of metadata for each document.  Defaults to a list of blank strings.
		max_docs_per_category, None or int, optional
		  Maximum number of documents to store per category.  Defaults to 4.
		transform : function, optional
			Function for ranking terms.  Defaults to scattertext.Scalers.percentile_lexicographic.
		alternative_text_field : str or None, optional
			Field in from dataframe used to make corpus to display in place of parsed text. Only
			can be used if corpus is a ParsedCorpus instance.
		Returns
		-------
		dictionary {info: {category_name: ..., not_category_name},
												 docs: {'texts': [doc1text, ...],
												        'labels': [1, 0, ...],
												        'meta': ['<b>blah</b>', '<b>blah</b>']}
		                     data: {term:, x:frequency [0-1], y:frequency [0-1],
		                            s: score,
		                            bg: background score,
		                            as: association score,
		                            cat25k: freq per 25k in category,
		                            cat: count in category,
		                            ncat: count in non-category,
		                            catdocs: [docnum, ...],
		                            ncatdocs: [docnum, ...]
		                            ncat25k: freq per 25k in non-category}}
		'''
		j = ScatterChart.to_dict(self,
		                         category,
		                         category_name=category_name,
		                         not_category_name=not_category_name,
		                         scores=scores,
		                         transform=transform)
		docs_getter = self._make_docs_getter(max_docs_per_category, alternative_text_field)
		j['docs'] = self._get_docs_structure(docs_getter, metadata)
		return j

	def _make_docs_getter(self, max_docs_per_category, alternative_text_field):
		if max_docs_per_category is None:
			docs_getter = DocsAndLabelsFromCorpus(self.term_doc_matrix,
			                                      alternative_text_field=alternative_text_field)
		else:
			docs_getter = DocsAndLabelsFromCorpusSample(self.term_doc_matrix,
			                                            max_docs_per_category,
			                                            alternative_text_field=alternative_text_field)
		if self.scatterchartdata.use_non_text_features:
			docs_getter = docs_getter.use_non_text_features()
		return docs_getter

	def _get_docs_structure(self, docs_getter, metadata):
		if metadata is not None:
			return docs_getter.get_labels_and_texts_and_meta(np.array(metadata))
		else:
			return docs_getter.get_labels_and_texts()

	def _add_term_freq_to_json_df(self, json_df, term_freq_df, category):
		ScatterChart._add_term_freq_to_json_df(self, json_df, term_freq_df, category)
		json_df['cat'] = term_freq_df[category + ' freq'].astype(np.int)
		json_df['ncat'] = term_freq_df['not cat freq'].astype(np.int)
