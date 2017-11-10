from tushare import get_h_data
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd
from utilities import attempt


def tusharePrice(tics=[], year=1, begdate='', enddate='',
                 autype='', index=False):

    if (enddate == ''):
        enddate = datetime.now()
        begdate = enddate - relativedelta(years=year)
    else:
        enddate = datetime.strptime(str(enddate), '%Y%m%d')
        begdate = datetime.strptime(str(begdate), '%Y%m%d')

    enddate = enddate.strftime("%Y-%m-%d")
    begdate = begdate.strftime("%Y-%m-%d")

    rs = {}
    skipped = []
    for tic in tics:
        df = attempt(get_h_data, tic, begdate, enddate, autype, index, 5, 5)
        if not df.empty:
            rs[tic] = df
        else:
            skipped.append(tic)

    if skipped:
        print('Retry %s' % skipped)
        for tic in skipped:
            df = attempt(get_h_data, tic, begdate,
                         enddate, autype, index, 5, 5)
            if not df.empty:
                rs[tic] = df
            else:
                print('Warning: %s is missing. skipped' % tic)

    wp = pd.Panel.from_dict(rs, orient='minor')
    return wp
