
import numpy as np
import pandas as pd
from collections import Counter


def transition_matrix(states):
    """
    Creates a numpy array containing the probability of transition from one state to another. Must 
    pass states as a list of lists, where each inner list is an observation of state changes.
    
    For example:
    states = [
    [2,1,3,1,2,3,1],
    [1,2,2,2]
    ]
    
    Produces:
    array([[ 0.        ,  0.66666667,  0.33333333],
           [ 0.25      ,  0.5       ,  0.25      ],
           [ 1.        ,  0.        ,  0.        ]])
    """

    max_state = max([max(l) for l in states]) + 1
    out = np.zeros((max_state,max_state))
    for (x,y), c in Counter(
        [transition for state_list in states for transition in \
         zip(state_list, state_list[1:])]).items():
        out[x,y] = c
        
    return out/out.sum(axis=1)[:,None]

def _map_to_numbers(string_list):
    """
    Returns a tuple of mapping from numbers to strings, then from strings to numbers
    """
    return {i: item for i, item in enumerate(string_list)}, {item: i for i, item in enumerate(string_list)}
    
def transition_dataframe(states):
    """
    Creates a pandas dataframe containing the probability of transition from one state to another. Must 
    pass states as a list of lists, where each inner list is an observation of state changes.
    
    For example:
    states = [
        ['b','a','c','a','b','c','a'],
        ['a','b','b','b']
    ]
    
    Produces:     a             b            c
         a  [ 0.        ,  0.66666667,  0.33333333],
         b  [ 0.25      ,  0.5       ,  0.25      ],
         c  [ 1.        ,  0.        ,  0.        ]
    """
    unique_states = sorted(set([state for state_list in states for state in state_list]))
    #get dicts which map 0, 1, 2, etc. to given states
    number_to_string_map, string_to_number_map = _map_to_numbers(unique_states) 
    #transform strings to mapped numbers
    state_numbers = [[string_to_number_map[state] for state in state_list] for state_list in states]
    out = pd.DataFrame(transition_matrix(state_numbers))
    return out.rename(columns=number_to_string_map, index=number_to_string_map)