######################################################################
# orgbabelhelper.py
#
# Author: Derek Feichtinger <derek.feichtinger@psi.ch>
#
######################################################################

""" This module provides a number of functions for passing informations between
the org document and python source code blocks."""

import pandas as pd
import datetime as dt
import re

def orgdate_to_date(datestr):
    """Returns a python datetime for the org date given in datestr.

    Allows passing in an empty/whitespace string."""
    if re.match(r'^ *$', datestr):
        return ''

    #m = re.match(r'^\[(\d+-\d+-\d+) +[a-zA-Z]{3}\]$', datestr)
    m = re.match(r'^[\[<](\d+-\d+-\d+) +[a-zA-Z]{3}[\]>]$', datestr)
    if not m:
        raise ValueError("Input String is not a date: >%s<" % datestr)

    return dt.datetime.strptime(m.group(1), '%Y-%m-%d').date()

def date_to_orgdate(date, active=False):
    orgstr = date.strftime("%Y-%m-%d %a")
    if active:
        return "<%s>" % orgstr
    return "[%s]" % orgstr

def orgdate_to_date(datestr):
    """Returns a python datetime for the org date given in datestr.

    Allows passing in an empty/whitespace string."""
    if re.match(r'^ *$', datestr):
        return ''

    #m = re.match(r'^\[(\d+-\d+-\d+) +[a-zA-Z]{3}\]$', datestr)
    m = re.match(r'^[\[<](\d+-\d+-\d+) +[a-zA-Z]{3}[\]>]$', datestr)
    if not m:
        raise ValueError("Input String is not a date: >%s<" % datestr)

    return dt.datetime.strptime(m.group(1), '%Y-%m-%d').date()

def date_to_orgdate(date, active=False):
    orgstr = date.strftime("%Y-%m-%d %a")
    if active:
        return "<%s>" % orgstr
    return "[%s]" % orgstr

# NOTANGLE-END

def orgtable_to_dataframe(tbl, index=None, datecols=None):
    """Read an org table into a data frame.

    Parameters
    ----------
    tbl : org table passed in by src block header
    index : name or index of column to use for index, optional
    datecols : 'auto' or list of column names, optional. Try
        to convert cells in these columns to python datetime objects. 

    Returns
    -------
    Pandas data frame

    Make sure you use ':colnames no' in your src block header. Else
    the table's first row containing the column names will not be
    available to the python code.

    """
    df = pd.DataFrame(tbl)
    df.columns = df.iloc[0,:]
    df = df.iloc[1:,:]
    df.columns.name = ""

    if datecols is None:
        datecols = []
    elif datecols == "auto":
        datecols = df.columns

    for col in datecols:
        try:
            df[col] = df[col].apply(orgdate_to_date)
            df[col] = pd.to_datetime(df[col])
        except:
            pass

    if index in df.columns:
        df.set_index(index, inplace=True)
    elif type(index) is int:
        df.set_index(df.columns[index], inplace=True)

    return df

def dataframe_to_orgtable(dframe, name=None, caption=None, attr=None,
			  index=True, date_format=None, hlines=None,
			  encoding='ascii'):
    """
    Parameters
    ----------
    dframe : data frame
    name : defines org table's name (#+NAME:), optional
    caption defines org table's caption (#+CAPTION:): , optional
    attr : defines org table's LaTeX attributes (#+ATTR_LATEX:), optional
    index : write the row names, optional
    date_format : Format string for datetime objects, optional
    hlines : list  of numbers. Where to put horizontal lines, optional
    encoding : Encoding for the resulting string, optional

    Returns
    -------
    Returns a string containing the data frame formatted as an org table.
    """
    result=""
    if attr:
        result += "#+ATTR_LATEX: %s\n" % attr

    if caption:
        result += "#+CAPTION: %s\n" % caption

    if name:
        result += "#+NAME: %s\n" % name

    lines = '|' + dframe.to_csv(None, sep='|', line_terminator='|\n|',
                                encoding=encoding, index=index, date_format=date_format).rstrip("|").rstrip("\n")

    hlines_tmp=[]
    if hlines is None:
        hlines_tmp.append(1) # per default add a hl after the 1st line
    else:
        for hl in hlines:
            if hl < 0:
                hlines_tmp.append(len(lines.split('\n')) + hl)
            else:
                hlines_tmp.append(hl)

    for i,l in enumerate(lines.split('\n')):
        if i in hlines_tmp:
            result +=  "|-----\n"
        result += l
        result += "\n"
    return result
