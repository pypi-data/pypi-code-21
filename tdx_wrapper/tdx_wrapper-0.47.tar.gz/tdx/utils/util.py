from decimal import Decimal, ROUND_HALF_UP
import pandas as pd


def precise_round(num):
    return float(Decimal(str(num)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))


def fillna(df):
    mask = pd.isnull(df.close)
    df.close.fillna(method='pad', inplace=True)
    df.volume.fillna(0, inplace=True)
    df.loc[mask, ["high", "low", "open"]] = df.close[mask]
    return df
