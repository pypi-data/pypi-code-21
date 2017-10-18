swap = -1
flip_and_swap = -1
palindromic_to_swap = -1

to_flip = 1

def flip_swap_remove(assigned_table, tol=0.08):

    snptype = assigned_table.SNPType.str

    swap_idx = snptype.contains("swap|^inferrable_palindromic$")
    flip_idx = snptype.contains("flip|^inferrable_palindromic$")
    remove_idx = snptype.contains("incompatible|noninferrable_palindromic")

    to_swap = list(assigned_table.ix[swap_idx].index.to_series())
    to_flip = list(assigned_table.ix[flip_idx].index.to_series())
    to_remove = list(assigned_table.ix[remove_idx].index.to_series())

    return to_swap, to_flip, to_remove


def swap_dosages(dosages, to_swap, to_remove):

    if list(dosages.columns)[0].endswith("_dose"):
        to_remove = [s + "_dose" for s in to_remove]
        to_swap = [s + "_dose" for s in to_swap]

    dosages = dosages.drop(to_remove, axis=1)
    dosages.loc[:, to_swap] = 2 - dosages.loc[:, to_swap]

    return dosages


def swap_alleles(row):
    row["REF"], row["ALT"] = row["ALT"], row["REF"]
    return row


def flip_alleles(a):
    return {"A": "T", "T": "A", "C": "G", "G": "C"}[a]


def flip_swap_remove_exposure_alleles(exposure, to_flip, to_swap, to_remove):

    exposure = exposure.drop(to_remove)

    exposure.loc[to_swap] = exposure.loc[to_swap].apply(swap_alleles, axis=1)
    exposure.loc[to_flip, "REF"] = exposure.loc[to_flip, "REF"].apply(flip_alleles)
    exposure.loc[to_flip, "ALT"] = exposure.loc[to_flip, "ALT"].apply(flip_alleles)

    return exposure
