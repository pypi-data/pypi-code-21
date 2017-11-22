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


@LocalIteration(iterate_by="collection",
                # reduce_with=max,
                # reduce_with=sum,
                no_wait=False,  # this controls PyCOMPSs' wait_on
                # reduce_schema=my_merge,
                reduce_with=reduce_count)
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
    my_collection = None  # Typically, a get_by_name for a collection class

    ###############################################
    # With decorator magic
    result = word_count(my_collection)
