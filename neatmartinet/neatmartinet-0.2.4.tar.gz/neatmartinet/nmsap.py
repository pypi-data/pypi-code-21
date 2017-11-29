import pandas as pd

import neatmartinet as nm

sapdict={'SYSID': 'systemid',
         'LIFNR': 'companyid',
         'NAME1': 'name1',
         'NAME2': 'name2',
         'NAME3': 'name3',
         'NAME4': 'name4',
         'STRAS': 'streetaddress',
         'PSTLZ': 'postalcode',
         'ORT01': 'cityname',
         'LAND1': 'country',
         'KRAUS': 'dunsnumber',
         'STCD1': 'registerid1',
         'STCD2': 'registerid2',
         'STCEG': 'taxid',
         'VBUND': 'kapisid',
         'NATO_CAGE_CODE': 'cageid',
         'KTOKK': 'accounttype'}


def concatenate_names(m):
    """
    This small function concatenate the different company names found across the names columns of SAP (name1, name2..)
    It takes the name found in the first column. If the name in the second column adds information to the first,
    it concatenates (by adding it in brackets). And it continues like this for the other columns
    Args:
        m (list): list of strings

    Returns:
        concatenated list of strings
    Examples:
    name1='KNIGHT FRANK (SA) PTY LTD'
    name2='KNIGHT FRANK'
    name3='ex-batman'
    name4='kapis code 3000'
    concatenate_names([name1,name2,name3,name4]):
        'KNIGHT FRANK (SA) PTY LTD (ex-batman, kapis code 3000)
    """
    #Remove na values
    r = pd.Series(m, index=range(len(m)))
    r.dropna(inplace=True)
    if r.shape[0]==0:
        return None
    elif r.shape[0]==1:
        return r[0]
    else:
        s = r[0]
        for ix in range(1,len(r)):
            #Compare fuzzy matching score with already concatenated string
            s1=nm.format_ascii_lower(s)
            r1=nm.format_ascii_lower(r[ix])
            if r1 is not None or len(r1)>1:
                score=nm.compare_tokenized_strings(s1,r1)
                if pd.isnull(score) or score <0.8:
                    #if score is less than 0.8 add it in brackets
                    if len(s)==len(r[0]):
                        s=s+' ('+r[ix]+')'
                    else:
                        s=s.rstrip(')')+', '+r[ix]+')'
        return s