def multiindex_col_ix(df, col):
    return df.index.names.index(col)

def unique_vals_multiindex(df, col):
    return df.index.levels[multiindex_col_ix(df, col)]
