# author : paul ogier
# coding=utf-8
# Various string cleaning functions, not always orthodox
# Treatment of na values
# Various type conversion (int to str, str to date, split...)
# Various comparison functions using fuzzywuzzy package (python levehstein)

import numpy as np
import pandas as pd


navalues = ['#', None, np.nan, 'None', '-', 'nan', 'n.a.',' ','', '#REF!', '#N/A', '#NAME?', '#DIV/0!', '#NUM!',
            'NaT','NULL']
nadict = {}
for c in navalues:
    nadict[c] = None

separatorlist = [' ', ',', '/', '-', ':', "'", '(', ')', '|', '°', '!', '\n', '_']
motavecS = ['après', 'français', 'francais', 'sous', 'plus', 'repas', 'souris']
accentdict = {'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
              'à': 'a', 'ä': 'a', 'â': 'a', 'á': 'a',
              'ü': 'u', 'ù': 'u', 'ú': 'u', 'û': 'u',
              'ö': 'o', 'ò': 'o', 'ó': 'o', 'ô': 'o', 'ß': 'ss', '@': '(at)'}
specialutf8 = {'\u2026': '', '\u017e': 'z', '\u2018': '', '\u0192': 'f', '\u2013': ' ', '\u0161': 's', '\u2021': '',
               '\u201d': '', '\u201c': '',
               '\u00E6': 'ae'}
removedchars = ['#', '~', '&', '$', '%', '*', '+', '?', '.']


# %%
def format_int_to_str(n, zeropadding=None):
    """
    format an integer to a string, and padd with zeroes if needed
    in case of navalues, it returns None
    in case of a string, it returns the string
    Args:
        n (int): integer to be format
        zeropadding(int): implementation of the zfill method

    Returns:
        str
    Examples
    - format_int_to_str(110) --> '110'
    - format_int_to_str(foo) --> 'foo'
    - format_int_to_str(110,zeropadding=4) --> '0110')
    - format_int_to_str(Nan) --> None
    """
    if pd.isnull(n) or n in navalues:
        return None
    else:
        n = str(n)
        n = n.lstrip().rstrip()
        n=n.split('.')[0]
        if zeropadding is not None:
            n = n.zfill(zeropadding)
        return n


# %%
def split(mystring, seplist=separatorlist):
    """
    Split a string according to the list of separators
    if the string is an navalue, it returns None
    if the separator list is not provided, it used the default defined in the module
    (.separatorlist)
    Args:
        mystring (str): string to be split
        seplist (list): by default separatorlist, list of separators

    Returns:
        list

    """
    if mystring in navalues:
        return None
    else:
        if seplist is None:
            seplist = separatorlist
        for sep in seplist:
            mystring = mystring.replace(sep, ' ')
        mystring = mystring.replace('  ', ' ')
        mylist= mystring.split(' ')
        mylist = list(filter(lambda x:x not in navalues,mylist))
        mylist=list(filter(lambda x:len(x)>0,mylist))
        return mylist


# %%
def format_ascii(s):
    """
    Normalize to the ascii format
    Args:
        s (str): string to be formated

    Returns:
        str
    """
    """
    :param mystring: str
    :return: str, normalized as unicode
    """
    if s in navalues:
        return None
    else:
        s = str(s)
        import unicodedata
        s = unicodedata.normalize('NFKD', s)
        s = s.encode('ASCII', 'ignore').decode('ASCII')
        return s


# %%
def format_ascii_lower(s, encoding='utf-8', min_length=1):
    """
    Normalize to the ascii format and with lower case
    Args:
        s (str): string
        encoding (str): encoding used as input, default 'utf-8'
        min_length (int): minimum length of the ouput result (otherwise return None)

    Returns:
        str
    """

    if s in navalues:
        return None
    else:
        s = str(s)
        s = s.lower()

        s = s.encode(encoding).decode(encoding)

        if encoding == 'utf-8':
            for mydict in [accentdict, specialutf8]:
                for a in mydict.keys():
                    s = s.replace(a, mydict[a])

        s = s.replace('  ', ' ')
        s = format_ascii(s)

        if s is None:
            return None

        s = s.encode(encoding).decode(encoding)
        s = s.replace('  ', ' ').lstrip().rstrip()

        if len(s) >= min_length:
            return s

        else:
            return None


# %%
def word_count(v):
    """
    counts the occurence of words in a panda.Series
    returnes a panda.Series with words as index and number of occurences as data
    Args:
        v (pd.Series): panda.Series containing string values

    Returns:
        pd.Series

    """
    import itertools
    v = v.replace(nadict).dropna().apply(split)
    return pd.Series(list(itertools.chain(*v))).value_counts(dropna=True)


# %%
def convert_str_to_date(myserie, datelim=None, dayfirst=True,  sep=None):
    """
    convert string to date
    :param myserie: pandas.Series, column to be converted
    :param datelim: datetime, default Today, date that is superior to all dates in the Serie. Is used to check whether the conversion
            is successful or not.
    :param dayfirst: boolean, default True, in the event that the automatic cheks are not able to arbitrate between day and month column
            is used to nominally select the correct group of digits as day (in this case, the first)
    :param sep: string, default None  If not given  the function will look for '-' , '/' , '.'
    :return: pandas.Series
    
    The date must be in the first 10 digits of the string, the first part separated by a space
    '2016.10.11 13:04' --> ok
    to check whether the conversion is correct:
    the date max must be lower than the datelim
    the variance of the month shall be lower than the variance of the days column
    
    """

    from datetime import datetime
    # clean a bit the string
    myserie = pd.Series(myserie).astype(str).replace(nadict)
    # check datelim
    if datelim is None:
        datelim = pd.datetime.now()

    # try automatic conversion via pandas.to_datetime
    try:
        methodepandas = pd.to_datetime(myserie)
        if methodepandas.max() <= datelim and methodepandas.dt.month.std() < methodepandas.dt.day.std():
            return methodepandas
    except:
        pass
    # if not working, try the hard way
    y = pd.DataFrame(index=myserie.index, columns=['ChaineSource'])
    y['ChaineSource'] = myserie
    y.dropna(inplace=True)
    if y.shape[0] == 0:
        myserie = pd.to_datetime(np.nan)
        return myserie

    # find separator
    if sep is None:
        # look for the separator used in the first row of the serie
        extrait = str(y['ChaineSource'].iloc[0])

        extrait = extrait[:min(len(extrait.split(' ')[0]),
                               10)]  # on sélectionne les 10 premiers caractères ou les premiers séparés par un espace

        if '/' in extrait:
            sep = '/'
        elif '-' in extrait:
            sep = '-'
        elif '.' in extrait:
            sep = '.'
        else:
            print(myserie.name, ':sep not found,Extrait: ', y['ChaineSource'].dropna().iloc[0])

    # split the first 10 characters (or the first part of the string separted by a blankspace using the separator
    # The split is done is three columns
    y['ChaineTronquee'] = y['ChaineSource'].apply(lambda r: r.split(' ')[0][:min(len(r.split(' ')[0]), 10)])
    y['A'] = y['ChaineTronquee'].apply(lambda r: int(r.split(sep)[0]))
    y['B'] = y['ChaineTronquee'].apply(lambda r: int(r.split(sep)[1]))
    y['C'] = y['ChaineTronquee'].apply(lambda r: int(r.split(sep)[2]))
    localList = ['A', 'B', 'C']

    year = None
    for i in localList:
        if y[i].max() >= 1970:
            year = i
    if year is None:
        print(myserie.name, ':Year not found')
        myserie = pd.to_datetime(np.nan)
        return myserie
    localList.remove(year)

    day = None
    month = None

    i0 = localList[0]
    i1 = localList[1]
    # méthode par mois max
    if y[i0].max() > 12:
        month = i1
        day = i0
    elif y[i1].max() > 12:
        month = i0
        day = i1
    else:
        tempdayi0 = y.apply(lambda r: datetime(year=r[year], month=r[i1], day=r[i0]), axis=1)
        tempdayi1 = y.apply(lambda r: datetime(year=r[year], month=r[i0], day=r[i1]), axis=1)

        # méthode par datelimite
        if tempdayi0.max() > datelim:
            day = i1
            month = i0
        elif tempdayi1.max() > datelim:
            day = i0
            month = i1
        # méthode par variance:
        else:
            if tempdayi0.dt.day.std() > tempdayi0.dt.month.std():
                day = i0
                month = i1
            elif tempdayi1.dt.day.std() > tempdayi1.dt.month.std():
                day = i1
                month = i0
            # méthode par hypothèse:
            else:
                # Cas YYYY - MM -DD
                if year == 'A':
                    print(myserie.name, 'utilisation hypothèse,YYYY - MM -DD')
                    day = 'C'
                    month = 'B'
                # Cas DD - MM - YYYY
                elif year == 'C' and dayfirst:
                    print(myserie.name, 'utilisation hypothèse,DD - MM - YYYY')
                    day = 'A'
                    month = 'B'
                # Cas DD - MM - YYYY
                elif year == 'C' and dayfirst == False:
                    print(myserie.name, 'utilisation hypothèse,MM - DD - YYYY')
                    day = 'A'
                    month = 'B'
                # Cas DD - YYYY - MM ?
                elif year == 'B':
                    print(myserie.name, 'utilisation hypothèse,DD - YYYY - MM')
                    day = 'A'
                    month = 'C'

    y['return'] = y.apply(lambda r: datetime(year=r[year], month=r[month], day=r[day]), axis=1)
    y.loc[y['return'].dt.year == 1970, 'return'] = pd.to_datetime(np.nan)
    myserie.loc[myserie.index] = pd.to_datetime(np.nan)
    myserie.loc[y.index] = pd.to_datetime(y['return'])
    myserie = pd.to_datetime(myserie)
    return myserie


# %%
def rmv_end_str(w, s):
    """
    remove str at the end of tken
    :param w: str, token to be cleaned
    :param s: str, string to be removed
    :return: str
    """
    if w.endswith(s):
        w = w[:-len(s)]
    return w


def rmv_end_list(w, mylist):
    """
    removed string at the end of tok
    :param w: str, word to be cleaned
    :param mylist: list, ending words to be removed
    :return: str
    """
    if type(mylist) == list:
        mylist.sort(key=len)
        for s in mylist:
            w = rmv_end_str(w, s)
    return w


# %%
def replace_list(mylist, mydict):
    """
    replace values in a list
    :param mylist: list to be replaced
    :param mydict: dictionary of correct values
    :return: list
    """
    newlist = []
    for m in mylist:
        if m in mydict.keys():
            newlist.append(mydict[m])
        else:
            newlist.append(m)
    return newlist


# %%

def rmv_stopwords(myword, stopwords=None, endingwords=None, replacedict=None):
    """
    remove stopwords, ending words, replace words
    :param myword: str,word to be cleaned
    :param stopwords: list, default None, list of words to be removed
    :param endingwords: list, default None, list of words to be removed at the end of tokens
    :param replacedict: dict, default None, dict of words to be replaced
    :return: str, cleaned string
    """
    if pd.isnull(myword):
        return None
    elif len(myword) == 0:
        return None
    else:
        mylist = split(myword)

        mylist = [m for m in mylist if not m in stopwords]

        if endingwords is not None:
            newlist = []
            for m in mylist:
                newlist.append(rmv_end_list(m, endingwords))
            mylist = list(set(newlist)).copy()

        if replacedict is not None:
            mylist = list(set(replace_list(mylist, replacedict)))

        myword = ' '.join(mylist)
        myword = myword.replace('  ', ' ')
        myword = myword.lstrip().rstrip()

        if len(myword) == 0:
            return None
        else:
            return myword

# %%
def calculate_token_frequency(v):
    """
    calculate the frequency a token is used in a particular column
    returns a Series of float in [0,1]
    Args:
        v (pd.Series): column to be evaluated

    Returns:
        pd.Series
    """
    wordlist = word_count(v)

    def countoccurences(r, word_list):
        if pd.isnull(r):
            return None
        else:
            mylist = r.split(' ')
            count = 0
            for m in mylist:
                if m in word_list.index:
                    count += word_list.loc[m]
            return count

    x = v.apply(lambda r: countoccurences(r, word_list=wordlist))
    x.fillna(x.max(), inplace=True)
    x = x / x.max()
    return x


def calculate_cat_frequency(v):
    """
    calculate the frequency a category is used in a particular column
    Args:
        v (pd.Series):

    Returns:
        pd.Series
    """
    catlist = v.value_counts()

    def countcat(r, category_list):
        if pd.isnull(r):
            return None
        else:
            if r in category_list.index:
                return catlist.loc[r]

    x = v.apply(lambda r: countcat(r, category_list=catlist))
    x.fillna(x.max(), inplace=True)
    x = x / x.max()
    return x

def acronym(s):
    """
    make an acronym of the string: take the first line of each token
    Args:
        s (str):

    Returns:
        str
    """
    m=split(s)
    if m is None:
        return None
    else:
        a= ''.join([s[0] for s in m])
        return a

# %%
def makeliststopwords(myserie, minlength=1, threshold=50, rmvwords=None, addwords=None, rmvdigits=True):
    """
    calculate the most common tokens found in a column
    :param myserie: pandas.Series, column to be evaluated
    :param minlength: int, default 1, min length of the token
    :param threshold: int, default 50, length of the first extract of stopwords, not counting words removed or words added
    :param rmvwords: list, default None, list of words to be removed from the list of stopwords
    :param addwords: list, default None, list of words to be added to the list of stopwords
    :param rmvdigits: boolean, default True, use digits in stopwords or not
    :return: list, list of stopwords
    """

    stopwords = word_count(myserie).index[:threshold].tolist()
    stopwords = [s for s in stopwords if len(s) >= minlength]
    if rmvdigits:
        stopwords = [s for s in stopwords if s.isdigit() == False]
    if rmvwords is not None:
        stopwords = [s for s in stopwords if not s in rmvwords]
    # noinspection PyAugmentAssignment
    if addwords is not None:
        stopwords +=list(addwords)
    stopwords = list(set(stopwords))
    return stopwords
