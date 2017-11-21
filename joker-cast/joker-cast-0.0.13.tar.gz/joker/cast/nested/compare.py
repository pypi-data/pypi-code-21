#!/user/bin/env python3
# coding: utf-8
from copy import deepcopy
import six


tail_for_str = '... +{} trailing characters'
tail_for_arr = '... +{} trailing objects'


def _str_trans(s):
    return s.replace('\n', r'\n').replace('\r', r'\r')


# TODO: test this func
def minify(obj, inplace=False, listlimit=1, strlimit=200):
    """
    Shorten list and strings to reduce verbosity.
    :param listlimit: 
    :param strlimit: 
    :param obj: input structure (dict or list)
    :param inplace: do minification on `obj` or a copy of it
    :return: a structure similar to `structure`(dict or list)
    """

    if not inplace:
        obj = deepcopy(obj)

    if isinstance(obj, list):
        # remove items beyond listlimit
        if len(obj) > listlimit:
            tail = tail_for_arr.format(len(obj)-listlimit)
            obj[listlimit:] = []
        else:
            tail = None

        for x in obj:
            minify(x, True, listlimit, strlimit)

        # append trail if trailing items have been removed
        if tail is not None:
            obj.append(tail)

    elif isinstance(obj, six.string_types):
        if isinstance(obj, six.binary_type):
            obj = obj.decode('utf-8')
        if len(obj) > strlimit:
            tail = tail_for_str.format(len(obj)-strlimit)
            obj = obj[:strlimit] + tail

    elif isinstance(obj, dict):
        for key, val in obj.items():
            val_ = minify(val, True, listlimit, strlimit)
            obj[key] = val_

    return obj


# TODO: test this func
def diff(cat, dog, inplace=False):
    """
    Compare 2 dicts recursively. Cancel out shared keys corresponding to
    values of same structure (recursively type match).
    :param cat: A dict
    :param dog: Another dict
    :param inplace: Cancel out similar fields in place, default False
    :return: (cat, dog) after cancellation
    """
    if not inplace:
        cat = deepcopy(cat)
        dog = deepcopy(dog)

    noncontainer_types = int, six.text_type, six.binary_type, float, type(None)

    cat_keys = set(cat.keys())
    dog_keys = set(dog.keys())
    shared_keys = set.intersection(cat_keys, dog_keys)
    for key in shared_keys:
        cat_val = cat[key]
        dog_val = dog[key]

        if type(cat_val) == type(dog_val):

            # 2 dicts: recursively diff
            if isinstance(cat_val, dict):
                diff(cat_val, dog_val, True)
                # del this key only if both become {}
                if (not cat_val) and (not dog_val):
                    del cat[key]
                    del dog[key]

            # 2 lists: are they empty?
            elif isinstance(cat_val, list):
                # 2 empty lists
                if not (cat_val or dog_val):
                    del cat[key]
                    del dog[key]

                # 2 non-empty lists
                elif cat_val and dog_val:
                    # assuming all lists are homogeneous
                    # TODO: check if the lists are homogeneous
                    cat[key] = [cat_val[0]]
                    dog[key] = [dog_val[0]]
                    cat_ = {'v': cat_val[0]}
                    dog_ = {'v': dog_val[0]}
                    diff(cat_, dog_, True)
                    if (not cat_val[0]) and (not dog_val[0]):
                        del cat[key]
                        del dog[key]

            elif isinstance(cat_val, noncontainer_types):
                del cat[key]
                del dog[key]

    return bool(cat and dog), cat, dog
