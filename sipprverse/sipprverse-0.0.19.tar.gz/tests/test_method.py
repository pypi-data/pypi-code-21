#!/usr/bin/env python 3
# import pytest
__author__ = 'adamkoziol'

# test_capitalize.py


def capital_case(x):
    return x.capitalize()


def test_capital_case():
    assert capital_case('semaphore') == 'Semaphore'
