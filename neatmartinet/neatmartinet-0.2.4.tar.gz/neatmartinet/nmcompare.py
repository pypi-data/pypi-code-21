import pandas as pd
import numpy as np
import neatmartinet as nm
from fuzzywuzzy.fuzz import ratio

# %%
def compare_twostrings(a, b, minlength=2):
    """
    compare two strings using fuzzywuzzy.fuzz.ratio
    Args:
        a (str):
        b (str):
        minlength (int): default 3, min string length

    Returns:
        float: number between 0 and 1
    """
    if pd.isnull(a) or pd.isnull(b):
        return None
    elif min([len(a), len(b)]) < minlength:
        return None
    else:
        r = ratio(a, b) / 100
        return r

# %%
def compare_tokenized_strings(a, b, tokenthreshold=0.8, mintokenlength=3):
    """
    compare the percentage of tokens matching using fuzzywuzzy.fuzz ratio
    Args:
        a (str):
        b (str):
        tokenthreshold (float): threshold for a match on a token
        mintokenlength (int):  minimum length of each token

    Returns:
        float: number between 0 and 1
    """
    if pd.isnull(a) or pd.isnull(b):
        return None
    else:
        # exact match
        if a == b:
            return 1
        # split strings by tokens and calculate score on each token
        else:
            # split the string
            a_tokens = [s for s in a.split(' ') if len(s) >= mintokenlength]
            b_tokens = [s for s in b.split(' ') if len(s) >= mintokenlength]
            if len(a_tokens)==0 or len(b_tokens)==0:
                return None
            elif len(a_tokens) >= len(b_tokens):
                long_tokens = a_tokens
                short_tokens = b_tokens
            else:
                long_tokens = b_tokens
                short_tokens = a_tokens
            count = 0.0
            for t_short in short_tokens:
                if t_short in long_tokens:
                    count += 1
                else:
                    t_match_max = 0.0
                    for t_long in long_tokens:
                        t_match = compare_twostrings(t_short, t_long)
                        if t_match> max(tokenthreshold,t_match_max):
                            t_match_max = t_match
                    count += t_match_max

        percenttokensmatching = count / len(short_tokens)
        return  percenttokensmatching


def exactmatch(a, b):
    if pd.isnull(a) or pd.isnull(b):
        return None
    else:
        return int((a == b))


def compare_acronyme(a, b, minaccrolength=3):
    """
    compare the acronym of two strings
    Args:
        a (str):
        b (str):
        minaccrolength (int): minimum length of accronym

    Returns:
        float : number between 0 and 1
    """
    if pd.isnull(a) or pd.isnull(b):
        return None
    else:
        a_acronyme = nm.acronym(a)
        b_acronyme = nm.acronym(b)
        if min(len(a_acronyme), len(b_acronyme)) >= minaccrolength:
            a_score_acronyme = compare_tokenized_strings(a_acronyme, b, mintokenlength=minaccrolength)
            b_score_acronyme = compare_tokenized_strings(b_acronyme, a, mintokenlength=minaccrolength)
            if any(pd.isnull([a_score_acronyme, b_score_acronyme])):
                return None
            else:
                max_score = np.max([a_score_acronyme, b_score_acronyme])
                return max_score
        else:
            return None