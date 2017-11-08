import pandas as pd
import numpy as np


def build_random_region_dataframe():
    df = pd.DataFrame(columns=['chr', 'start', 'stop', 'strand', 'gene'],
                      index=np.arange(100))
    df['chr'] = "chr" + pd.Series(index=df.index, data=np.random.randint(1, 22, len(df))).map(str)
    df['start'] = pd.Series(index=df.index, data=np.random.randint(1, 1000000000, len(df)))
    df['stop'] = pd.Series(index=df.index, data=np.random.randint(1, 1000000000, len(df)))
    df['strand'] = '*'
    df['gene'] = 'gene' + pd.Series(index=df.index, data=np.random.randint(1, 22, len(df))).map(str)
    df['sample_name'] = 'sample' + pd.Series(index=df.index, data=np.random.randint(1, 20, len(df))).map(str)
    return df