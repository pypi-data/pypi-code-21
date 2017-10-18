from itertools import product

import pandas as pd

from numpy import isclose, float64


def switch_alleles(a):
    return {"A": "T", "T": "A", "C": "G", "G": "C"}[a]


def _palindrome(m):

    return (m.E1 == m.E2.apply(switch_alleles)) & (m.O1 == m.O2.apply(switch_alleles)) & (m.E1 == m.O1) & (m.E2 == m.O2)


def _non_inferrable_palindrome(m, tolerance):

    return _palindrome(m) & ~_exposure_and_outcome_allele_frequencies_differ_from_fifty_percent(m, tolerance)


def _inferrable_palindrome(m, tolerance):

    return _palindrome(m) & _exposure_and_outcome_allele_frequencies_differ_from_fifty_percent(m, tolerance) & _inverse_allele_frequencies_similar_within_tolerance(m, tolerance)


def _inverse_allele_frequencies_similar_within_tolerance(m, tolerance):

    return pd.Series(isclose(1 - m.OAF, m.EAF, atol=tolerance), index=m.index)


def _exposure_and_outcome_allele_frequencies_differ_from_fifty_percent(m, tolerance):

   outcome_differs = (m.OAF > 0.5 + tolerance) | (m.OAF < 0.5 - tolerance)
   exposure_differs = (m.EAF > 0.5 + tolerance) | (m.EAF < 0.5 - tolerance)

   return outcome_differs & exposure_differs


def _allele_frequencies_similar_within_tolerance(m, tolerance):

    return pd.Series(isclose(m.OAF, m.EAF, atol=tolerance), index=m.index)


def non_inferrable_palindromic_snp(m, tolerance):

    x = _non_inferrable_palindrome(m, tolerance)
    return m.loc[x].rsid


def _fine_snps(m, tolerance):

    similar_af = _allele_frequencies_similar_within_tolerance(m, tolerance)
    not_palindromic = ~_non_inferrable_palindrome(m, tolerance)

    fine = (m.E1 == m.O1) & (m.E2 == m.O2) & (m.E1 != m.E2) & similar_af & not_palindromic
    return fine


def fine_snps(m, tolerance):

    fine = _fine_snps(m, tolerance)

    return m.loc[fine].rsid


def inferrable_palindromic_snp(m, tolerance):

    x = _inferrable_palindrome(m, tolerance) & ~_fine_snps(m, tolerance)

    return m.loc[x].rsid


def _to_swap(m, tolerance):

    return (m.E1 == m.O2) & (m.E2 == m.O1) & (m.E1 != m.E2) & ~_palindromic_to_swap(m, tolerance) & ~_to_flip(m, tolerance)


def to_swap(m, tolerance):

    return m.loc[_to_swap(m, tolerance)].rsid


def palindromic_to_swap(m, tolerance):

    return m.loc[_palindromic_to_swap(m, tolerance)].rsid


def _palindromic_to_swap(m, tolerance):

    return (m.E1 == m.O2) & (m.E2 == m.O1) & (m.E1.apply(switch_alleles) == m.O1) & (m.E2.apply(switch_alleles) == m.O2) & ~_exposure_and_outcome_allele_frequencies_differ_from_fifty_percent(m, tolerance)


def to_flip(m, tolerance):

    return m.loc[_to_flip(m, tolerance)].rsid


def _to_flip(m, tolerance):

    return _allele_frequencies_similar_within_tolerance(m, tolerance) & (m.E1.apply(switch_alleles) == m.O1) & (m.E2.apply(switch_alleles) == m.O2) & ~_palindromic_to_swap(m, tolerance)


def _to_swap_and_flip(m, tolerance):

    return (m.E1.apply(switch_alleles) == m.O2) & (m.E2.apply(switch_alleles) == m.O1) & ~_fine_snps(m, tolerance) & ~_palindrome(m)


def to_flip_and_swap(m, tolerance):

    return m.loc[_to_swap_and_flip(m, tolerance)].rsid

def _incompatible(m, tolerance):

    return ~_to_flip(m, tolerance) & ~_palindromic_to_swap(m, tolerance) & ~_to_swap(m, tolerance) & ~_inferrable_palindrome(m, tolerance) & ~_non_inferrable_palindrome(m, tolerance) & ~_fine_snps(m, tolerance) & ~_to_swap_and_flip(m, tolerance)


def incompatible(m, tolerance):

    return m.loc[_incompatible(m, tolerance)].rsid


def assign_table(m, tolerance):

    m = m.copy()
    d = {
        "fine": fine_snps(m, tolerance),
        "inferrable_palindromic": inferrable_palindromic_snp(m, tolerance),
        "noninferrable_palindromic": non_inferrable_palindromic_snp(m, tolerance),
        "swapped": to_swap(m, tolerance),
        "flipped": to_flip(m, tolerance),
        "flipped_and_swapped": to_flip_and_swap(m, tolerance),
        "palindromic_swapped": palindromic_to_swap(m, tolerance),
        "incompatible": incompatible(m, tolerance)
    }

    for (li, i), (lj, j) in product(d.items(), repeat=2):
        i, j = set(i), set(j)
        if not li == lj:
            assert not i.intersection(j), "{}: {}\n{} {}\n{}".format(li, str(i), lj, str(j), set(i).intersection(j))

    m.insert(len(m.columns), "SNPType", "")
    for l, v in d.items():
        m.loc[v.index, "SNPType"] = l

    return m.set_index("rsid")


def sanity_check_table(m):

    assert m.OAF.dtype == float64
    assert m.EAF.dtype == float64

    okay = (m.OAF <= 1) & (m.OAF >= 0) & (m.EAF <= 1) & (m.EAF >= 0)
    not_okay = ~okay

    assert not_okay.sum() == 0, \
        "The following rows have invalid allele frequencies:\n" + str(m[not_okay])

    valid_alleles = "A T C G".split()
    assert all(m.E1.isin(valid_alleles)) and all(m.E2.isin(valid_alleles)) and all(m.O1.isin(valid_alleles)) and all(m.O2.isin(valid_alleles))
