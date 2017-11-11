from metadate import parse_date
import pandas as pd
qs = pd.read_csv("~/cancellation_data.csv")["reply_message"]
qs = [x for x in qs if isinstance(x, str)]
for q in qs:
    try:
        mp = parse_date(q)
    except:
        print(q)
        raise
    if mp is not None:
        print(mp.matches)
