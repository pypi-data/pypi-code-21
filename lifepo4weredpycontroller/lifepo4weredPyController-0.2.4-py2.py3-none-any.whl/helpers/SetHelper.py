#!/usr/bin/python3
# -*- coding: utf-8 -*-


def areSame(dict, dictToCompare):
    if len(dict) != len(dictToCompare):
        return False
    else:
        return (set() == (set(dict.items()) - set(dictToCompare.items())))
