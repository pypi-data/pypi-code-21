# -*- coding: utf-8 -*-
import types


class HashHelper(object):

    @staticmethod
    def nice_hash(o):
        """
        Makes a hash from a dictionary, list, tuple or set to any level, that contains
        only other hashable types (including any lists, tuples, sets, and
        dictionaries).
        Taken from: http://stackoverflow.com/a/8714242
        """
        import copy

        if isinstance(o, (set, tuple, list)):
            return tuple([HashHelper.nice_hash(e) for e in o])
        elif isinstance(o, dict):
            new_o = copy.deepcopy(o)
            for k, v in new_o.items():
                new_o[k] = HashHelper.nice_hash(v)
            return hash(tuple(frozenset(sorted(new_o.items()))))
        else:
            return hash(o)


class DictionaryHelper(object):

    @staticmethod
    def get_value(dictionary, path_dictionary):
        """
        Retrieve the value from nested dictionary structure by nested key.
        Supports lists, sets, tuples, dictionaries and all nested into themselves.

        :param dict dictionary: nested dictionary with complex structure
        :param object path_dictionary: nested (or not) path in nested dictionary
         to retrieve data by
        :return: the sub-dictionary found by the path in nested dictionary
        :rtype: object
        :raises ValueError: raises :class:ValueError if nothing can be found by specified path
        :raises KeyError: raises :class:KeyError if specified path is incorrect,
        containing illogical multiple choices or conditions.
        """
        return DictionaryHelper.__inner_get(dictionary, path_dictionary)

    @staticmethod
    def __inner_get(dictionary, path_dictionary):
        """"""
        # Check if we have set or single value in path
        if type(path_dictionary) is list or type(path_dictionary) is tuple:
            raise KeyError('Lists and tuples are not supported in path_dictionary')
        elif type(path_dictionary) is set:
            if len(path_dictionary) > 1:
                raise KeyError('Condition path has multiple conditions')
            for cond in path_dictionary:
                return dictionary[cond]
        elif type(path_dictionary) is str:
            return dictionary[path_dictionary]
        elif type(path_dictionary) is dict:
            conditions = path_dictionary.keys()
            if len(conditions) > 1:
                raise KeyError('Condition path has multiple conditions')
            elif len(conditions) == 0:
                raise KeyError('Condition path has zero conditions')
            if conditions[0] not in dictionary:
                    raise ValueError('Dictionary did not contain condition sub path')
            else:
                return DictionaryHelper.__inner_get(dictionary[conditions[0]], path_dictionary[conditions[0]])
        else:
            raise KeyError('Type ' + type(path_dictionary) + ' is not supported by dictionary path')

    @staticmethod
    def matches(condition, state):
        return DictionaryHelper.__inner_match(condition, state)

    @staticmethod
    def __inner_match(condition, state):
        """Method matches"""
        if type(condition) is dict:
            for ck in condition.keys():
                if ck not in state:
                    return False
                else:
                    if not DictionaryHelper.__inner_match(condition[ck], state[ck]):
                        return False
            return True
        elif type(condition) is list or type(condition) is set or type(condition) is tuple:
            for ck in condition:
                if not DictionaryHelper.__inner_match(ck, state):
                    return False
            return True
        elif isinstance(condition, types.FunctionType):
            return condition(state)
        else:
            if type(state) is dict:
                return condition in state
            elif type(state) is list or type(condition) is set or type(condition) is tuple:
                return condition in state
            else:
                return condition == state
