#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    Created on Mon Oct 16 17:12:32 2017

    @author: paulblankley
    """
import numpy as np
import os
from chemkin207 import ReactionSet

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def test_reaction_rates():
    x = np.array([[1.],[2.],[1.]])
    path = os.path.join(BASE_DIR, 'test_xmls/reaction_rate_1.xml')
    rrr = ReactionSet(path)
    assert(np.array_equal(rrr.progress_rates(x,10),[40.0,10.0]))
    assert(np.array_equal(rrr.reaction_rates(x,10),[-60.0,-70.0,70.0]))

def test_reaction_coef():
    path = os.path.join(BASE_DIR, 'test_xmls/reaction_coef_1.xml')
    rrr = ReactionSet(path)
    assert(rrr.reaction_coefs(900)[0][0]==0.00044989777442266471)
    assert(rrr.reaction_coefs(900)[1][0]==1.5783556022951033)

def test_reaction_rates_rev():
    x = np.array([2., 1., .5, 1., 1., 1., .5, 1.]).T
    path = os.path.join(BASE_DIR, 'test_xmls/rxns_rev.xml')
    rrr = ReactionSet(path)
    assert(np.isclose(rrr.progress_rates(x,750), [-3.43641832e+16, -5.88589924e+11, 1.36640381e+12,  \
                                                 -5.51788793e+14, 1.45474612e+13,  6.75189291e+13, \
                                                 1.62500000e+13, 7.82443985e+12, 2.55000887e+13,   \
                                                 2.69382512e+13, 2.84197199e+12]).all())
    assert(np.isclose(rrr.reaction_rates(x,750),[3.42304562795e16,-3.38308977852e16,-3.52979102957e+16, \
                                      4.07078984572e+13,5.86479724945e+14,3.44028050967e+16, \
                                      -7.63606068937e+13,-5.52803118677e+13]).all())

def test_reaction_coef_rev():
    path = os.path.join(BASE_DIR, 'test_xmls/rxns_rev.xml')
    rrr = ReactionSet(path)
    assert(np.isclose(rrr.reaction_coefs(200)[0][0], 19066566282.668961))
    assert(np.isclose(rrr.reaction_coefs(200)[0][1], 2.43147163435558e+27))

def test_reaction_rates_rev_low():
    x = np.array([2., 1., .5, 1., 1., 1., .5, 1.]).T
    path = os.path.join(BASE_DIR, 'test_xmls/rxns_rev.xml')
    rrr = ReactionSet(path)
    try:
        rrr.progress_rates(x,190)
    except ValueError as err:
        assert(type(err)==ValueError)
    try:
        rrr.reaction_rates(x,190)
    except ValueError as err:
        assert(type(err)==ValueError)
    try:
        rrr.reaction_rates(x,10)
    except FloatingPointError as err:
        assert(type(err)==FloatingPointError)
    # bonus test
    try:
        rrr.reaction_rates(x,'f')
    except ValueError as err:
        assert(type(err)==ValueError)
    try:
        rrr.progress_rates(x,'f')
    except ValueError as err:
        assert(type(err)==ValueError)

def test_reaction_rates_rev_high():
    x = np.array([2., 1., .5, 1., 1., 1., .5, 1.]).T
    path = os.path.join(BASE_DIR, 'test_xmls/rxns_rev.xml')
    rrr = ReactionSet(path)
    try:
        rrr.progress_rates(x,3501)
    except ValueError as err:
        assert(type(err)==ValueError)
    try:
        rrr.reaction_rates(x,10000)
    except ValueError as err:
        assert(type(err)==ValueError)
    try:
        rrr.reaction_rates(x,float('inf'))
    except FloatingPointError as err:
        assert(type(err)==FloatingPointError)
    # bonus test
    try:
        rrr.reaction_rates('12,34,5,2,1',1300)
    except ValueError as err:
        assert(type(err)==ValueError)
    try:
        rrr.progress_rates('12,34,5,2,1',1300)
    except ValueError as err:
        assert(type(err)==ValueError)

def test_set_params():
    path = os.path.join(BASE_DIR, 'test_xmls/reaction_coef_1.xml')
    rrr = ReactionSet(path)
    rrr.reaction_coefs(900)
    rrr.set_params(1,k=10,coeftype='Constant')
    assert(rrr.reaction_coefs(900)[1][0]==10.0)

def test_init_value_error(): # Hits test in get_reaction
    try:
        path = os.path.join(BASE_DIR, 'test_xmls/reaction_init_value_1.xml')
        rrr = ReactionSet(path)
    except ValueError as err:
        assert(type(err) == ValueError)


def test_init_A_error():
    try:
        path = os.path.join(BASE_DIR, 'test_xmls/reaction_init_value_2.xml')
        rrr = ReactionSet(path)
    except ValueError as err:
        assert(type(err) == ValueError)


def test_coef_type_error():
    try:
        path = os.path.join(BASE_DIR, 'test_xmls/reaction_init_type_1.xml')
        rrr = ReactionSet(path)
    except ValueError as err:
        assert(type(err) == ValueError)


def test_T_val_error():
    path = os.path.join(BASE_DIR, 'test_xmls/reaction_rate_1.xml')
    rrr = ReactionSet(path)
    T = -1
    try:
        rrr.reactions[0].reaction_coef(T)
    except ValueError as err:
        assert(type(err) == ValueError)


def test_T_type_error():
    path = os.path.join(BASE_DIR, 'test_xmls/reaction_rate_1.xml')
    rrr = ReactionSet(path)
    T = 'fsag'
    try:
        rrr.reactions[0].reaction_coef(T)
    except TypeError as err:
        assert(type(err) == TypeError)


def test_progress_rate_x_shape_error():
    path = os.path.join(BASE_DIR, 'test_xmls/reaction_rate_1.xml')
    rrr = ReactionSet(path)
    try:
        rrr.reactions[0].progress_rate(np.array([[1],[2],[3],[4]]),1)
    except ValueError as err:
        assert (type(err) == ValueError)



def test_progress_rate_T_error():
    path = os.path.join(BASE_DIR, 'test_xmls/reaction_rate_1.xml')
    rrr = ReactionSet(path)
    try:
        rrr.reactions[0].progress_rate(np.array([[1],[2],[3]]),-144)
    except ValueError as err:
        assert (type(err) == ValueError)


def test_progress_rate_T_error_2():
    path = os.path.join(BASE_DIR, 'test_xmls/reaction_rate_1.xml')
    rrr = ReactionSet(path)
    try:
        rrr.reactions[0].progress_rate(np.array([[1],[2],[3]]), 'f')
    except ValueError as err:
        assert (type(err) == ValueError)

def test_progress_rate_T_error_3():
    path = os.path.join(BASE_DIR, 'test_xmls/reaction_rate_1.xml')
    rrr = ReactionSet(path)
    try:
        rrr.reactions[0].progress_rate(np.array([[1],[2],[3]]), [1,2,3])
    except TypeError as err:
        assert (type(err) == TypeError)

def test_reaction_rate_x_shape_error():
    path = os.path.join(BASE_DIR, 'test_xmls/reaction_rate_1.xml')
    rrr = ReactionSet(path)
    try:
        rrr.reactions[0].reaction_rate(np.array([[1],[2],[3],[4]]),1)
    except ValueError as err:
        assert (type(err) == ValueError)


def test_reaction_rate_T_error():
    path = os.path.join(BASE_DIR, 'test_xmls/reaction_rate_1.xml')
    rrr = ReactionSet(path)
    try:
        rrr.reactions[0].reaction_rate(np.array([[1],[2],[3]]),-144)
    except ValueError as err:
        assert (type(err) == ValueError)

def test_reaction_rate_T_error_2():
    path = os.path.join(BASE_DIR, 'test_xmls/reaction_rate_1.xml')
    rrr = ReactionSet(path)
    try:
        rrr.reactions[0].reaction_rate(np.array([[1],[2],[3]]), 'f')
    except ValueError as err:
        assert (type(err) == ValueError)


def test_arrhenius_k_overflow():
    path = os.path.join(BASE_DIR, 'test_xmls/reaction_arr_over_1.xml')
    rrr = ReactionSet(path)
    try:
        rrr.reactions[0]._arrhenius(100)
    except OverflowError as err:
        assert (type(err) == OverflowError)

def test_mod_arrhenius_k_overflow():
    path = os.path.join(BASE_DIR, 'test_xmls/reaction_arr_over_2.xml')
    rrr = ReactionSet(path)
    try:
        rrr.reactions[0]._mod_arrhenius(100)
    except OverflowError as err:
        assert (type(err) == OverflowError)


def test_set_param_error_A_type():
    path = os.path.join(BASE_DIR, 'test_xmls/reaction_rate_1.xml')
    rrr = ReactionSet(path)
    try:
        rrr.set_params(0, A = 'f')
    except ValueError as err:
        assert (type(err) == ValueError)

def test_set_param_error_A_type2():
    path = os.path.join(BASE_DIR, 'test_xmls/reaction_rate_1.xml')
    rrr = ReactionSet(path)
    try:
        rrr.set_params(0, A = [1,2])
    except TypeError as err:
        assert (type(err) == TypeError)

def test_set_param_error_b_type():
    path = os.path.join(BASE_DIR, 'test_xmls/reaction_rate_1.xml')
    rrr = ReactionSet(path)
    try:
        rrr.set_params(0, b = [1,2])
    except TypeError as err:
        assert (type(err) == TypeError)

def test_set_param_error_b_type2():
    path = os.path.join(BASE_DIR, 'test_xmls/reaction_rate_1.xml')
    rrr = ReactionSet(path)
    try:
        rrr.set_params(1, b = 'f')
    except ValueError as err:
        assert (type(err) == ValueError)

def test_set_param_error_E_type():
    path = os.path.join(BASE_DIR, 'test_xmls/reaction_rate_1.xml')
    rrr = ReactionSet(path)
    try:
        rrr.set_params(0, E = [1,2,3])
    except TypeError as err:
        assert (type(err) == TypeError)

def test_set_param_error_E_type2():
    path = os.path.join(BASE_DIR, 'test_xmls/reaction_rate_1.xml')
    rrr = ReactionSet(path)
    try:
        rrr.set_params(1, E = 'sefg')
    except ValueError as err:
        assert (type(err) == ValueError)

def test_set_param_error_R_type():
    path = os.path.join(BASE_DIR, 'test_xmls/reaction_rate_1.xml')
    rrr = ReactionSet(path)
    try:
        rrr.set_params(0, R = [1,2,33])
    except TypeError as err:
        assert (type(err) == TypeError)

def test_set_param_error_R_type2():
    path = os.path.join(BASE_DIR, 'test_xmls/reaction_rate_1.xml')
    rrr = ReactionSet(path)
    try:
        rrr.set_params(1, R = 'setttg')
    except ValueError as err:
        assert (type(err) == ValueError)

def test_set_param_error_k_type():
    path = os.path.join(BASE_DIR, 'test_xmls/reaction_rate_1.xml')
    rrr = ReactionSet(path)
    try:
        rrr.set_params(0, k = [-1,2,33])
    except TypeError as err:
        assert (type(err) == TypeError)

def test_set_param_error_k_type2():
    path = os.path.join(BASE_DIR, 'test_xmls/reaction_rate_1.xml')
    rrr = ReactionSet(path)
    try:
        rrr.set_params(1, k = 'seyretttg')
    except ValueError as err:
        assert (type(err) == ValueError)

def test_set_param_error_coeftype():
    path = os.path.join(BASE_DIR, 'test_xmls/reaction_rate_1.xml')
    rrr = ReactionSet(path)
    try:
        rrr.set_params(1, coeftype = 'seyretttg')
    except ValueError as err:
        assert (type(err) == ValueError)

# Parser section of testing
## UPDATE FOR NEW PARSER
## UPDATE the expected dict to match the output
def test_working_xml():
    # Test a standard output
    expected_dict = {'reactions': [{'reversible': False, 'coeftype': 'Arrhenius', 'b': 0, 'k': 0, 'A': 35200000000.0, 'E': 71400.0, \
                    'vprime': np.array([[1.],[0.],[0.],[0.],[0.],[1.]]), 'v2prime': np.array([[0.],[1.],[1.],[0.],[0.],[0.]])},\
                   {'reversible': False, 'coeftype': 'modifiedArrhenius', 'k': 0, 'A': 0.0506, 'b': 2.7, 'E': 26300.0,\
                    'vprime': np.array([[0.],[1.],[0.],[1.],[0.],[0.]]), 'v2prime': np.array([[1.],[0.],[1.],[0.],[0.],[0.]])},\
                   {'reversible': False, 'coeftype': 'Constant', 'A': 0, 'b': 0, 'E': 0, 'k': 1000.0, \
                    'vprime': np.array([[0.],[0.],[1.],[1.],[0.],[0.]]), 'v2prime': np.array([[1.],[0.],[0.],[0.],[1.],[0.]])}],\
                    'species': np.array(['H', 'O', 'OH', 'H2', 'H2O', 'O2'])} \

    path = os.path.join(BASE_DIR, "test_xmls/rxns.xml")
    actual_dict = ReactionSet(path).get_params()
    expected_species = np.array(['H', 'O', 'OH', 'H2', 'H2O', 'O2'])

    # Test for each reactions relevant information
    for index, expected_dict_index in enumerate(expected_dict['reactions']):
        cur_dict_index = actual_dict['reactions'][index]
        assert cur_dict_index['reversible'] == expected_dict_index['reversible']
        assert cur_dict_index['coeftype'] == expected_dict_index['coeftype']
        assert cur_dict_index['b'] == expected_dict_index['b']
        assert cur_dict_index['k'] == expected_dict_index['k']
        assert cur_dict_index['A'] == expected_dict_index['A']
        assert cur_dict_index['E'] == expected_dict_index['E']
        for i, ele in enumerate(cur_dict_index['vprime']):
            assert ele == expected_dict_index['vprime'][i]
        for i, ele in enumerate(cur_dict_index['v2prime']):
            assert ele == expected_dict_index['v2prime'][i]

    # Test for the new species entry
    for index, ele in enumerate(expected_dict):
        assert expected_species[index] == actual_dict['species'][index]


    # previous test
    #assert np.array_equal(actual_dict['species'], expected_dict['species'])
    #for i in range(len(expected_dict['A'])):
    #    assert actual_dict['A'][i] == expected_dict['A'][i] or actual_dict['A'][i] == 0
    #    assert actual_dict['b'][i] == expected_dict['b'][i] or actual_dict['b'][i] == 0
    #    assert actual_dict['E'][i] == expected_dict['E'][i] or actual_dict['E'][i] == 0
    #    assert actual_dict['k'][i] == expected_dict['k'][i] or actual_dict['k'][i] == 0
    #assert np.array_equal(actual_dict['coeftype'], expected_dict['coeftype'])
    #assert np.array_equal(actual_dict['vprime'], expected_dict['vprime'])
    #assert np.array_equal(actual_dict['v2prime'], expected_dict['v2prime'])

def test_xml_file_not_found():
    # Test for an empty xml file
    try:
        path = os.path.join(BASE_DIR, "test_xmls/the_ghost_of_files.xml")
        ReactionSet(path)
    except FileNotFoundError as err:
        assert(type(err)==FileNotFoundError)


def test_empty_xml_file():
    # Test for an empty xml file
    try:
        path = os.path.join(BASE_DIR, "test_xmls/rxns_test_empty_file.xml")
        ReactionSet(path)
    except FileNotFoundError as err:
        assert(type(err)==FileNotFoundError)


def test_missing_arrhenius_parameters():
    # Test for an empty xml file
    try:
        path = os.path.join(BASE_DIR, "test_xmls/rxns_test_missing_arrhenius_parameters.xml")
        ReactionSet(path)
    except AttributeError as err:
        assert(type(err)==AttributeError)


def test_missing_constant_parameters():
    # Test for an empty xml file
    try:
        path = os.path.join(BASE_DIR, "test_xmls/rxns_test_missing_constant_parameters.xml")
        ReactionSet(path)
    except AttributeError as err:
        assert(type(err)==AttributeError)


def test_missing_modified_arrhenius_parameters():
    # Test for an empty xml file
    try:
        path = os.path.join(BASE_DIR, "test_xmls/rxns_test_missing_modified_arrhenius_parameters.xml")
        ReactionSet(path)
    except AttributeError as err:
        assert(type(err)==AttributeError)


def test_missing_reactants():
    # Test for an empty xml file
    try:
        path = os.path.join(BASE_DIR, "test_xmls/rxns_test_missing_reactants.xml")
        ReactionSet(path)
    except AttributeError as err:
        assert(type(err)==AttributeError)


def test_missing_reactions():
    # Test for an empty xml file
    try:
        path = os.path.join(BASE_DIR, "test_xmls/rxns_test_missing_reactions.xml")
        ReactionSet(path)
    except ValueError as err:
        assert(type(err)==ValueError)


def test_missing_species():
    # Test for an empty xml file
    try:
        path = os.path.join(BASE_DIR, "test_xmls/rxns_test_missing_species.xml")
        ReactionSet(path)
    except AttributeError as err:
        assert(type(err)==AttributeError)


def test_unexpected_reactant():
    # Test for an empty xml file
    try:
        path = os.path.join(BASE_DIR,"test_xmls/rxns_test_unexpected_reactant.xml")
        ReactionSet(path)
    except ValueError as err:
        assert(type(err)==ValueError)


# This part of tests check the functionality of reaction_dict['reversible']
def test_reversible_missing_tag():
    # Test for missing reversible tag
    try:
        path = os.path.join(BASE_DIR, "test_xmls/rxns_test_reversible_missing_tag.xml")
        ReactionSet(path)
    except ValueError as err:
        assert(type(err) == ValueError)

def test_type_missing_tag():
    # Test for missing type tag
    try:
        path = os.path.join(BASE_DIR, "test_xmls/rxns_test_type_missing_tag.xml")
        ReactionSet(path)
    except ValueError as err:
        assert(type(err) == ValueError)

def test_reversible_tag_error():
    # Test for invalid reversible tag attribute: i.e. not yes nor no
    try:
        path = os.path.join(BASE_DIR, "test_xmls/rxns_test_reversible_tag_error.xml")
        ReactionSet(path)
    except ValueError as err:
        assert(type(err) == ValueError)

# UPDATE FOR NEW PARSER
# Update new form of input
# This test case is not complete, still need to test for the NASA inputs
def test_reversible_input():
    # Test a standard output
    expected_dict = {'reactions': [{'reversible': False, 'coeftype': 'Arrhenius', 'b': 0, 'k': 0, 'A': 35200000000.0, 'E': 71400.0, \
                    'vprime': np.array([[1.],[0.],[0.],[0.],[0.],[1.]]), 'v2prime': np.array([[0.],[1.],[1.],[0.],[0.],[0.]])},\
                   {'reversible': True, 'coeftype': 'modifiedArrhenius', 'k': 0, 'A': 0.0506, 'b': 2.7, 'E': 26300.0,\
                    'vprime': np.array([[0.],[1.],[0.],[1.],[0.],[0.]]), 'v2prime': np.array([[1.],[0.],[1.],[0.],[0.],[0.]])},\
                   {'reversible': False, 'coeftype': 'Constant', 'A': 0, 'b': 0, 'E': 0, 'k': 1000.0, \
                    'vprime': np.array([[0.],[0.],[1.],[1.],[0.],[0.]]), 'v2prime': np.array([[1.],[0.],[0.],[0.],[1.],[0.]])}],\
                    'species': np.array(['H', 'O', 'OH', 'H2', 'H2O', 'O2'])}

    path = os.path.join(BASE_DIR, "test_xmls/rxns_test_reversible_input.xml")
    actual_dict = ReactionSet(path).get_params()

    # Test for each reactions relevant information
    for index, expected_dict_index in enumerate(expected_dict['reactions']):
        cur_dict_index = actual_dict['reactions'][index]
        #assert cur_dict_index['reversible'] == expected_dict_index['reversible']
        assert cur_dict_index['coeftype'] == expected_dict_index['coeftype']
        assert cur_dict_index['b'] == expected_dict_index['b']
        assert cur_dict_index['k'] == expected_dict_index['k']
        assert cur_dict_index['A'] == expected_dict_index['A']
        assert cur_dict_index['E'] == expected_dict_index['E']
        for i, ele in enumerate(cur_dict_index['vprime']):
            assert ele == expected_dict_index['vprime'][i]
        for i, ele in enumerate(cur_dict_index['v2prime']):
            assert ele == expected_dict_index['v2prime'][i]

    expected_species = np.array(['H', 'O', 'OH', 'H2', 'H2O', 'O2'])
    # Test for the new species entry
    for index, ele in enumerate(expected_dict):
        assert expected_species[index] == actual_dict['species'][index]



    #assert np.array_equal(actual_dict['species'], expected_dict['species'])
    #for i in range(len(expected_dict['A'])):
    #    assert actual_dict['A'][i] == expected_dict['A'][i] or actual_dict['A'][i] == 0
    #    assert actual_dict['b'][i] == expected_dict['b'][i] or actual_dict['b'][i] == 0
    #    assert actual_dict['E'][i] == expected_dict['E'][i] or actual_dict['E'][i] == 0
    #    assert actual_dict['k'][i] == expected_dict['k'][i] or actual_dict['k'][i] == 0
    #assert np.array_equal(actual_dict['coeftype'], expected_dict['coeftype'])
    #assert np.array_equal(actual_dict['vprime'], expected_dict['vprime'])
    #assert np.array_equal(actual_dict['v2prime'], expected_dict['v2prime'])
