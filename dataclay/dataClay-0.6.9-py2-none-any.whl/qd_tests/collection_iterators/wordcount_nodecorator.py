from . import LocalIteration
from collections import defaultdict


@task()
def reduce_count(ret_func_1, ret_func_2):
    """Perform a reduction of the word counting.

    Inputs are dictionaries, and the output is a merged dictionary containing
    the sum across the words in the two dictionaries.
    """
    for k, v in ret_func_1.iteritems():
        ret_func_2[k] += v
    # This is destructive regarding ret_func_2, but the algorithm
    # knows that it becomes irrelevant.
    return ret_func_2


@task()
def word_count(collection):
    """Perform a word count.
    :param collection: Something iterable containing words
    :return: A dictionary of {"word": #n}
    """
    result = defaultdict(int)
    for word in collection:
        result[word] += 1
    return result


if __name__ == "__main__":
    my_collection = get_data()

    my_collection.get_local_iterator()
    result = list()
    for local_it in my_collection.get_local_iterators():
        partial_result = word_count(local_it)
        result.append(partial_result)

    merge_binary_tree(result, reduce_count)
