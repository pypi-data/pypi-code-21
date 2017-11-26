#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from builtins import *

from collections import OrderedDict
import re
import string

def lexical(token):
    """
    Extract lexical features from given token
    There are 3 kinds of lexical features, take 'Hello' as an example:

    1. lowercase: 'hello'
    2. first4: 'hell'
    3. last4: 'ello'
    """
    lowercase = token.lower()
    first4 = lowercase[:4]
    last4 = lowercase[-4:]
    return OrderedDict([
            ('lowercase', lowercase), 
            ('first4', first4),
            ('last4', last4)
            ])
            
def _char_shape(char):
    if char in string.ascii_uppercase:
        return 'A'
    if char in string.ascii_lowercase:
        return 'a'
    if char in string.digits:
        return '0'
    else:
        return char

def _shape(token):
    return ''.join([_char_shape(char) for char in token])

def _contains_a_letter(token):
    regex = r'[A-Za-z]'
    if re.search(regex, token):
        return True
    else:
        return False
    
def _contains_a_capital(token):
    regex = r'[A-Z]'
    if re.search(regex, token):
        return True
    else:
        return False

def _begins_with_capital(token):
    return _char_shape(token[0]) == 'A'

def _all_capital(token):
    regex = r'^[A-Z]+$'
    if re.match(regex, token):
        return True
    else:
        return False

def _contains_a_digit(token):
    regex = r'\d'
    if re.search(regex, token):
        return True
    else:
        return False

def _all_digit(token):
    regex = r'^\d+$'
    if re.match(regex, token):
        return True
    else:
        return False

def _contains_a_punctuation(token):
    return len(set(string.punctuation) & set(token)) > 0

def _consists_letters_n_digits(token):
    shape = _shape(token)
    return set(shape.lower()) == set('a0')

def _consists_digits_n_punctuations(token):
    shape = _shape(token)
    lower_shape = shape.lower()
    return set(lower_shape) <= set(string.punctuation+'0') and len(lower_shape) >= 2
    
def orthographic(token):
    """
    Extract orthographic features from a given token
    
    There are 11 kinds of orthographic features, take 'Windows10' as an example:

    1. shape: 'Aaaaaaa00'
    2. length: 9
    3. contains_a_letter: True
    4. contains_a_capital: True
    5. begins_with_capital: True
    6. all_capital: False
    7. contains_a_digit: True
    8. all_digit: False
    9. contains_a_punctuation: False
    10. consists_letters_n_digits: True
    11. consists_digits_n_punctuations: False
    """

    return OrderedDict([
                    ('shape', _shape(token)), 
                    ('length', len(token)), 
                    ('contains_a_letter', _contains_a_letter(token)), 
                    ('contains_a_capital', _contains_a_capital(token)),
                    ('begins_with_capital', _begins_with_capital(token)), 
                    ('all_capital', _all_capital(token)), 
                    ('contains_a_digit', _contains_a_digit(token)),
                    ('all_digit', _all_digit(token)),
                    ('contains_a_punctuation', _contains_a_punctuation(token)),
                    ('consists_letters_n_digits', _consists_letters_n_digits(token)),
                    ('consists_digits_n_punctuations', _consists_digits_n_punctuations(token)),
                   ])