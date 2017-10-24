"""
analyze.py

This is the database layout. See the documentation for details on each field.

model table: 
0 - title = CHAR(250)
1 - description = TEXT
2 - copyright = CHAR(250)
3 - author = CHAR(250)
4 - definition_url = CHAR(500)
5 - dmid = CHAR(40)
6 - entryid = CHAR(40)
7 - dataid = CHAR(40)

record table:
 0 - header = char(100)
 1 - label = char(250)
 2 - datatype = char(10)
 3 - min_len = char(100)
 4 - max_len = char(100)
 5 - choices = TEXT
 6 - regex = CHAR(250)
 7 - min_inc_val = char(100)
 8 - max_inc_val = char(100)
 9 - description = TEXT
10 - definition_url = CHAR(500)
11 - pred_obj_list = TEXT
12 - def_txt_value = TEXT
13 - def_num_value = char(100)
14 - units = CHAR(50)
15 - mcid = CHAR(40)
16 - adid = CHAR(40)
17 - min_exc_val = char(100)
18 - max_exc_val = char(100)

"""
import sys
import os
import time
import csv
import sqlite3

from uuid import uuid4
from collections import OrderedDict
import iso8601
import configparser
import argparse
from subprocess import run
import click

def checkType(h, dataDict):
    """ test each data item from a column. if one is not a type, turn off that type. If the type is an int or a float then the min/max is set as inclusive. Exclusive is never set."""
    dlist = dataDict[h]
    is_int = False
    is_float = False
    is_date = False
    is_str = False
    maxincval = None
    minincval = None
    
    for x in dlist:
        try:
            int(x)
            is_int = True
        except:
            is_int = False
            break
    
    for x in dlist:
        try:
            if not is_int:
                float(x)
                is_float = True
        except:
            is_float = False
            break
    
    for x in dlist:
        try:
            if not is_int and not is_float:
                iso8601.parse_date(x)
                is_date = True
        except:
            is_date = False
            break
    
    for x in dlist:
        try:
            if not is_int and not is_float and not is_date:
                str(x)
                is_str = True
        except:
            is_str = False
            break
    
    if is_int:
        intlist = [int(x) for x in dlist]
        maxincval = max(intlist)
        minincval = min(intlist)
    if is_float:
        flist = [float(x) for x in dlist]
        maxincval = max(flist)
        minincval = min(flist)
    
    if is_int:
        dt = "Integer"
    elif is_float:
        dt = "Decimal"  # most of the time it really is a decimal.
    elif is_date:
        dt = "Date"
    else:
        dt = "String"

    return(dt, maxincval, minincval, h)

def analyze(csvInput, delim, level, out_dir):
    """
    Load and analyze the CSV file.
    Create a database used to describe the data.
    """

    dname, fname = os.path.split(csvInput)
    prjname = fname[:fname.index('.')]
    os.makedirs(out_dir, exist_ok=True)    
    dbName =  prjname + '.db'
    db_file = out_dir + os.path.sep + dbName
    
    # if this database already exists then delete it
    try:
        os.remove(db_file)
    except OSError:
        pass

    # create the database with the two tables.
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute("""CREATE TABLE "model" ("title" CHAR(250), "description" TEXT, "copyright" CHAR(250), "author" CHAR(250), "definition_url" CHAR(500), "dmid" CHAR(40), "entryid" CHAR(40), "dataid" CHAR(40))""")
    c.execute("""CREATE TABLE "record"  (header  char(100), label char(250), datatype char(10), min_len char(100), max_len char(100), "choices" TEXT, "regex" CHAR(250), "min_inc_val" char(100), "max_inc_val" char(100), "description" TEXT, "definition_url" CHAR(500), "pred_obj_list" TEXT, "def_txt_value" TEXT, "def_num_value" char(100), "units" CHAR(50), "mcid" CHAR(40), "adid" CHAR(40), "min_exc_val" char(100), "max_exc_val" char(100))""")
    c.execute("""CREATE INDEX header_idx on record (header)""")
    
    # create the initial data for the record table.
    data = []
    with open(csvInput) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=delim)
        for h in reader.fieldnames:
            mcID = str(uuid4())  # model component
            adID = str(uuid4())   # adapter
            label = 'The ' + h.replace('_', ' ')
            data.append((h, label, 'String', '', '', '', '', '', '', '', '', '', '', '', '', mcID, adID,'',''))

    c = conn.cursor()
    c.executemany(
        "INSERT INTO record VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", data)
    conn.commit()

    # create the initial data for the model table
    dmID = str(uuid4())   # data model
    entryID = str(uuid4())   # entry
    dataID = str(uuid4())   # data cluster

    data = [('S3M Data Model', 'S3M Data Model for ' + csvInput, 'Copyright 2017, Data Insights, Inc.',
             'Data Insights, Inc.', 'http://www.some_url.com', dmID, entryID, dataID)]
    c.executemany("insert into model values (?,?,?,?,?,?,?,?)", data)
    conn.commit()
    conn.close()

    if level == 'Full':
        conn = sqlite3.connect(db_file)
        # indepth analysis of columns for datatypes and ranges.
        with open(csvInput) as csvfile:
            reader = csv.DictReader(csvfile, delimiter=delim)
            hdrs = reader.fieldnames
            dataDict = OrderedDict()
            for h in reader.fieldnames:
                dataDict[h] = []

            for row in reader:
                for h in reader.fieldnames:
                    dataDict[h].append(row[h])

        hdrs = dataDict.keys()

         # check for the column types and min/max values, show progress bar
        with click.progressbar(hdrs, label="Checking types and min/max values: ") as bar:
            for h in bar:
                vals = checkType(h, dataDict)
                    
                # edit the database record for the correct type
                c = conn.cursor()
                c.execute("""UPDATE record SET datatype = ?, max_inc_val = ?, min_inc_val = ? WHERE header = ? """, vals)
                conn.commit()
    
            conn.close()

    return(db_file)

