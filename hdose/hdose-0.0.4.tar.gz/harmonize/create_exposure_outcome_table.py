from numpy import float64


def create_exposure_outcome_table(dosage_info, gwas):

    dosage_info, gwas = dosage_info.copy(), gwas.copy()

    cols_to_keep_dosage_info = "REF ALT AF".split()
    cols_to_keep_gwas = "A1 A2 FreqA2".split()

    cols_to_drop_dosage_info = [c for c in dosage_info.columns if c not in cols_to_keep_dosage_info]
    cols_to_drop_gwas = [c for c in gwas.columns if c not in cols_to_keep_gwas]

    dosage_info = dosage_info.drop(cols_to_drop_dosage_info, 1)
    gwas = gwas.drop(cols_to_drop_gwas, 1)

    df = gwas.join(dosage_info)

    df = df.rename(columns={"A1": "G1", "A2": "G2", "FreqA2": "GAF", "REF": "D1", "ALT": "D2", "AF": "DAF"})

    df.loc[:, "G2"] = df.G2.str.upper()
    df.loc[:, ["GAF", "DAF"]] = df.loc[:, ["GAF", "DAF"]].astype(float64)

    return df["D1 D2 G1 G2 GAF DAF".split()].reset_index()
