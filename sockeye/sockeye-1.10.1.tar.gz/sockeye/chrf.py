# Copyright 2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You may not
# use this file except in compliance with the License. A copy of the License
# is located at
#
#     http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied. See the License for the specific language governing
# permissions and limitations under the License.

from collections import Counter
import re

"""
NOTE:
This code is deprecated and no longer used by saar_test_model.py.
It is left here for archiving purposes and may be of use to someone in the future.
"""


def extract_ngrams(s, n):
    """
    Yields counts of character n-grams from string s of order n.
    """
    return Counter([s[i:i + n] for i in range(len(s) - n + 1)])


def delete_whitespace(s):
    return re.sub("\s+", "", s)


def recall(ngrams_hypothesis, ngrams_reference):
    """
    Computes Recall on two Counter objects storing ngram counts.
    """
    if not ngrams_reference:
        return 0.0
    return 1 - sum((ngrams_reference - ngrams_hypothesis).values()) / float(sum(ngrams_reference.values()))


def precision(ngrams_hypothesis, ngrams_reference):
    """
    Computes Precision on two Counter objects storing ngram counts.
    """
    if not ngrams_hypothesis:
        return 0.0
    return 1 - sum((ngrams_hypothesis - ngrams_reference).values()) / float(sum(ngrams_hypothesis.values()))


def chrf(hypothesis: str, reference: str, max_order: int = 6, beta: float = 3.0, trim: bool = True) -> float:
    """
    Computes chrF score on hypothesis String given reference String as described in
    'CHRF: character n-gram F-score for automatic MT evaluation' by Maja Popovic.
    [http://www.statmt.org/wmt15/pdf/WMT49.pdf]

    :param hypothesis: Hypothesis string
    :param max_order: up to which order to compute n-grams
    :param beta: weight on recall compared to precision
    :param trim: whether to trim whitespaces from reference and hypothesis
    """
    if max_order == 0:
        return 0.0

    if trim:
        hypothesis = delete_whitespace(hypothesis)
        reference = delete_whitespace(reference)

    avg_recall = 0.0
    avg_precision = 0.0
    for order in range(1, max_order + 1):
        ngrams_reference = extract_ngrams(reference, order)
        ngrams_hypothesis = extract_ngrams(hypothesis, order)
        avg_recall += recall(ngrams_hypothesis, ngrams_reference)
        avg_precision += precision(ngrams_hypothesis, ngrams_reference)
    avg_recall /= max_order
    avg_precision /= max_order
    if avg_precision + avg_recall == 0:
        return 0.0

    beta_square = beta ** 2
    return (1 + beta_square) * ((avg_precision * avg_recall) / (beta_square * avg_precision + avg_recall))
