from unittest import TestCase

import numpy as np

from scattertext.termscoring.RudderScore import RudderScore


class TestRudderScore(TestCase):
	def test_get_scores(self):
		cat_counts, not_cat_counts = self._get_counts()
		scores = RudderScore.get_scores(cat_counts, not_cat_counts)
		np.testing.assert_almost_equal(scores,
		                               np.array([0., 0.5, 0., 0.5, 1.,
		                                         0.6149725, 0.7269922, 0.0126812,
		                                         0.0126812, 0.886218]))

	def test_get_scores_zero_all_same(self):
		cat_counts = np.array([0, 0, 0, 0, 0, 0, 1, 2])
		not_cat_counts = np.array([1, 1, 2, 1, 1, 1, 1, 2])
		scores = RudderScore.get_scores(cat_counts, not_cat_counts)
		np.testing.assert_almost_equal(scores, [0.5, 0.5, 0, 0.5, 0.5, 0.5, 0.75, 0.5])

	def test_get_scores_zero_median(self):
		cat_counts = np.array([0, 0, 0, 0, 0, 0, 1, 2])
		not_cat_counts = np.array([1, 1, 2, 1, 1, 1, 1, 3])
		RudderScore.get_scores(cat_counts, not_cat_counts)

	def get_scores_for_category(self):
		cat_counts, not_cat_counts = self._get_counts()
		scores = RudderScore.get_scores_for_category(cat_counts, not_cat_counts)
		np.testing.assert_almost_equal(scores,
		                               np.array([0.9300538, 1.0198039,
		                                         0.9300538, 0.9055385, 0.2,
		                                         0.7433034, 0.585235, 0.9861541,
		                                         0.9861541, 0.3605551]))

	def _get_counts(self):
		cat_counts = np.array(    [1,   5,   1,   9,   100, 1, 1, 0, 0, 2])
		not_cat_counts = np.array([100, 510, 100, 199, 0,   1, 0, 1, 1, 0])

		return cat_counts, not_cat_counts
