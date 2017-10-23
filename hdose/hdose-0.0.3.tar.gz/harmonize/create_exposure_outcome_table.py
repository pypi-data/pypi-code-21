from numpy import float64


def create_exposure_outcome_table(exposure, outcome):

    exposure, outcome = exposure.copy(), outcome.copy()

    cols_to_keep_exposure = "REF ALT AF".split()
    cols_to_keep_outcome = "A1 A2 FreqA1".split()

    cols_to_drop_exposure = [c for c in exposure.columns if c not in cols_to_keep_exposure]
    cols_to_drop_outcome = [c for c in outcome.columns if c not in cols_to_keep_outcome]

    exposure = exposure.drop(cols_to_drop_exposure, 1)
    outcome = outcome.drop(cols_to_drop_outcome, 1)

    df = outcome.join(exposure)
    df.columns = "O1 O2 OAF E1 E2 EAF".split()

    df.loc[:, "O2"] = df.O2.str.upper()

    df.loc[:, ["OAF", "EAF"]] = df.loc[:, ["OAF", "EAF"]].astype(float64)
    df.loc[:, "EAF"] = 1 - df.EAF

    return df["E1 E2 O1 O2 OAF EAF".split()].reset_index()
