#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
Dimensional works with a regular dict.
Problem with regular dicts:
the order of their keys isn't guaranteed.
From a functional point of view this is not a problem:
'm.s-1' are absolutely equivalent to 's-1.m'.
But from a testing point of view, these two strings differ from each other.
Consequentially, the following tests pass
for any of several equivalent strings.
"""

import pytest

from dimensionalquantity import Dimensional as D
from dimensionalquantity import DimQuant as DQ
from dimensionalquantity import Translator

@pytest.fixture(scope="function")
def translator():
    yield Translator()

def test_SI_dimensions(translator):
    # http://www.bipm.org/en/publications/si-brochure/section1-3.html
    assert( translator.translate('m').dimensions==D({'L': 1}) )
    assert( translator.translate('s').dimensions==D({'t': 1}) ) # 't' instead of suggested (by SI) 'T' because
    assert( translator.translate('K').dimensions==D({'T': 1}) ) # the suggested \theta doesn't quite work, hence 'T' here.
    assert( translator.translate('A').dimensions==D({'i': 1}) ) # lower case 'i' instead of upper 'I' to avoid confusion between (1, l, I) (one, lower L, upper i)
    assert( translator.translate('mol').dimensions==D({'N': 1}) )
    assert( translator.translate('cd').dimensions==D({'J': 1}) )
    assert( translator.translate('kg').dimensions==D({'M': 1}) )

@pytest.mark.parametrize('dim_string,expected_dimension',(
                         ('m',  D({'L': 1})),
                         ('m2',  D({'L': 2})),
                         ('m-2',  D({'L': -2})),
                         ))
def test_SI_dimension_m_multiples(translator, dim_string, expected_dimension):
    q0 = translator.translate(dim_string).dimensions
    assert( q0==expected_dimension )

@pytest.mark.parametrize('string, expected_dimension',(
                         ('(kg.s)-2/((m3/K)-3/A2)',
                             D({'M': -2.0, 't': -2.0, 'L': 9.0, 'T': -3.0, 'i': 2.0})),
                         ('(kg.s)2/((m3/K)-3/A2)',
                             D({'M': 2.0, 't': 2.0, 'L': 9.0, 'T': -3.0, 'i': 2.0})),
                         ('(kg.s)2/(m3/K)-3/A2',
                             D({'M': 2.0, 't': 2.0, 'L': 9.0, 'T': -3.0, 'i': -2.0})),
                         ('(kg.s)2/(m3/K)-3/A-2',
                             D({'M': 2.0, 't': 2.0, 'L': 9.0, 'T': -3.0, 'i': 2.0})),
                         ('(kg.s)2/(m3/K)3/A-2',
                             D({'M': 2.0, 't': 2.0, 'L': -9.0, 'T': 3.0, 'i': 2.0})),
                        ))
def test_translating_complex_strings(translator, string, expected_dimension):
    res = translator.translate(string).dimensions
    assert( res==expected_dimension )

def test_unknown_unit_prefix_raises_KeyError(translator):
    with pytest.raises(KeyError):
        translator.translate('wm') # while 'm' exists as SI unit, the 'w' prefix doesn't and thus this error
    with pytest.raises(ValueError):
        translator.translate('w') # this unit doesn't exist in the SI base units (also not in extended because lower case)

@pytest.mark.parametrize('expected_strs,dimensions',(
                         ( ('m'),
                             D({'L':1})),
                         ( ('m'),
                             {'L':1}),
                         ( ('m.s-1','s-1.m'),
                             D({'L':1, 't':-1})),
                         ))
def test_reverse_unit_lookup(translator, expected_strs, dimensions):
    real_str = translator.reverse_unit_lookup(dimensions)
    passed = False
    for possible_str in expected_strs:
        if possible_str==real_str:
            passed = True
            break
    if not passed: # raise assertion error which highlights the difference
        assert( possible_str==real_str )

def test_reverse_unit_lookup_wrong_input_type(translator):
    with pytest.raises(TypeError):
        translator.reverse_unit_lookup(0)

@pytest.fixture(scope="function")
def setup_and_clean_DQ_with_basic_Translator():
    _t = DQ._T
    DQ.register_translator(_t)
    yield
    # teardown: reset original Translator() as the translator used in DQ
    DQ.register_translator(_t)

def test_register_unit_LUT(setup_and_clean_DQ_with_basic_Translator):
    with pytest.raises(KeyError):
        q_fanta = DQ('1 fanta') # this unit doesn't exist hence the KeyError

    fantasy_unit_LUT = {'fanta': DQ('2.54 cm')}
    translator = Translator()
    translator.register_unit_LUT(fantasy_unit_LUT)
    DQ.register_translator(translator)

    q_si = 2*DQ('2.54 cm')
    q_fanta = DQ('2 fanta') # now it does exist
    assert( q_si==q_fanta )

def test_register_unit_LUT_override(setup_and_clean_DQ_with_basic_Translator):
    # the `setup_and_clean_DQ_with_basic_Translator` ensures
    # DQ doesn't suddenly come with weird LUTs preregistered
    # despite the following having been registered in a prev test;
    # in other words, this is supposed to test whether the teardown was executed correctly
    with pytest.raises(KeyError):
        q_fanta = DQ('1 fanta') # this unit doesn't exist hence the KeyError

    pre_T = DQ._T
    q_si_before_overwritten = 2*DQ('2.54 cm')

    fantasy_unit_LUT = {'fanta': DQ('2.54 cm')}
    translator = Translator()
    translator.register_unit_LUT(fantasy_unit_LUT, override=True)
    DQ.register_translator(translator)

    assert(id(pre_T) != DQ._T) # since overwritten

    q_fanta = DQ('2 fanta') # now it does exist
    assert( q_si_before_overwritten==q_fanta )

    with pytest.raises(KeyError):
        q_si_after_overwritten = DQ('2.54 cm') # no longer recognized because LUT is overwritten

def test_register_prefix_LUT(setup_and_clean_DQ_with_basic_Translator):
    with pytest.raises(KeyError):
        q_fanta = DQ('1 qm') # `m` is known, but prefix `q` not
    
    fantasy_prefix_LUT = {'q': 3.14}
    translator = Translator()
    translator.register_prefix_LUT(fantasy_prefix_LUT)
    DQ.register_translator(translator)

    assert(DQ('1 qm') == DQ('314 cm')) # `c` prefix is still known

def test_register_prefix_LUT_override(setup_and_clean_DQ_with_basic_Translator):
    with pytest.raises(KeyError):
        q_fanta = DQ('1 qm') # `m` is known, but prefix `q` not
    
    q_before_override = DQ('314 cm')

    fantasy_prefix_LUT = {'q': 3.14}
    translator = Translator()
    translator.register_prefix_LUT(fantasy_prefix_LUT, override=True)
    DQ.register_translator(translator)

    assert(DQ('1 qm') == q_before_override)

    with pytest.raises(KeyError):
        q_after_override = DQ('314 cm')

def test_register_unit_LUT_with_already_existing(setup_and_clean_DQ_with_basic_Translator):
    redundant_unit_LUT = {'m': DQ('100 cm')}
    translator = Translator()
    with pytest.raises(ValueError):
        translator.register_unit_LUT(redundant_unit_LUT)

def test_register_prefix_LUT_with_already_existing(setup_and_clean_DQ_with_basic_Translator):
    redundant_unit_LUT = {'m': 1e-2/10}
    translator = Translator()
    with pytest.raises(ValueError):
        translator.register_prefix_LUT(redundant_unit_LUT)

def test_register_prefix_LUT_with_more_than_1_letter(setup_and_clean_DQ_with_basic_Translator):
    notimplemented_prefix = {'da': 10}
    translator = Translator()
    with pytest.raises(NotImplementedError):
        translator.register_prefix_LUT(notimplemented_prefix)
