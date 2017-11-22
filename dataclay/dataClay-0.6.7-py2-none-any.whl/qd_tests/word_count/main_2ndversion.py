#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys

from WordCount import TextStats, TextCollection

__author__ = 'Alex Barcelo <alex.barcelo@bsc.es>'
__copyright__ = '2017 Barcelona Supercomputing Center (BSC-CNS)'


if __name__ == "__main__":
    from pycompss.api.api import waitForAllTasks

    # Get the dataset (word collection) _persistent_ name
    nameDataset = sys.argv[1]

    data = TextCollection.get_by_alias(nameDataset)

    result = TextStats(dict())
    result.make_persistent()

    for text in data:
        partialResult = text.word_count()
        result.merge_with(partialResult)

    # Wait for result to end its reduction
    waitForAllTasks()

    print "Most used words in text:\n%s" % result.top_words(10)
    print "Words: %d" % result.get_total()
