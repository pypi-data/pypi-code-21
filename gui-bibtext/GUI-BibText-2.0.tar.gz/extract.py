#!/usr/bin/env python

"""
Code for generating the bibtex key from Google Scholar for the list of papers, whose names are stored
    in the excel sheet.


Author: Himanshu Mittal (himanshu.mittal224@gmail.com)
Referred: https://github.com/venthur/gscholar
"""

import optparse
import sys
import os
import pandas as pd
import gscholar as gs

def extractr(filePath):

    # Path to the excel sheet containing the list of paper title in the second colum, heading as 'Name'.
    pathToFile=filePath
    cwd = os.getcwd()
    sdir = cwd + '/bibtexFile.xlsx'
    xl = pd.ExcelFile(pathToFile)
    df = xl.parse("Sheet1")
    bt = []
    f=df['PaperName']
    for i in range(f.size):
        a1=f[i]
        x1 = a1.replace(u'\xa0', ' ')
        args1=x1.encode('ascii','ignore')
        biblist = gs.query(args1)
        print(biblist[0])
        k=biblist[0]
        k1 = k.replace(u'\n ', ' ')
        x2=k1.encode('ascii','ignore')
        x2=x2.decode('utf-8')
        bt.append(x2)
    df1 = pd.DataFrame({'bibtex': bt})
    f=pd.concat([df, df1], axis=1)

    # Create a Pandas Excel writer using XlsxWriter as the engine.
    writer = pd.ExcelWriter(sdir, engine='xlsxwriter')

    # Convert the dataframe to an XlsxWriter Excel object.
    f.to_excel(writer, sheet_name='Sheet1')

    writer.save()


if __name__ == "__main__":
    pathToFile="PaperList.xlsx"
    extractr(pathToFile)