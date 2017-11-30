from __future__ import print_function
from pandas import read_csv
import threading

data = read_csv("tmp/data_10m.csv",
                error_bad_lines=False,
                chunksize=10000
                )

data.columns  # all column labels
data.index    # number of records

data.iloc[0][0]

count = list()
src = "/Users/scott.pierce/code/golumn/tmp/data_100k.csv"
# raw count
sum((1 for line in open(src, 'rb')))


def line_index(src):
    counts = list()
    offset = 0
    with open(src, "r") as f:
        for line in f:
            size = len(line)
            offset += size
            counts.append((size, offset))
    return counts


def blocks(files, size=65536):
    while True:
        b = files.read(size)
        if not b: break
        yield b

with open("file", "r") as f:
    print(sum(bl.count("\n") for bl in blocks(f)))

test_csv()
# => count:  5240867 , time:  43.838359117507935 , resource:  6,650,626,048
# htop: 9606M 31904
def test_csv(src="/Users/scott.pierce/code/golumn/tmp/contract_items_10m.csv"):
    import csv, resource
    from time import time
    a = time() 
    rows = list()
    for row in csv.reader(open(src, 'r')):
        rows.append(row)
    print('count: ', len(rows), ', time: ', time() - a, ', resource: ', resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)

test_csv2()
# => count:  5240867 , time:  28.120308876037598 , resource:  7208960
def test_csv2(src="/Users/scott.pierce/code/golumn/tmp/contract_items_10m.csv"):
    import csv, resource
    from time import time
    a = time() 
    count = 0
    for row in csv.reader(open(src, 'r')):
        count += 1
    print('count: ', count, ', time: ', time() - a, ', resource: ', resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)

test_pandas(memory_map=True, engine='python', chunksize=10000)
# => count:  5240866 , time:  73.83057379722595 , resource:  4143607808

test_pandas(memory_map=True, chunksize=1000)
# => count:  5240866 , time:  36.177579164505005 , resource:  2,486,493,184
# htop: 16.3G 7224M

test_pandas(memory_map=True, chunksize=10000)
# => count:  5240866 , time:  27.79412603378296 , resource:  3967664128

def test_pandas(src="/Users/scott.pierce/code/golumn/tmp/contract_items_10m.csv", **kw):
    import csv
    import resource
    from time import time
    from pandas import read_csv
    start = time() 
    sep = ','
    with open(src, 'r') as f:
        dialect = csv.Sniffer().sniff(f.read(64 * 1024))
        sep = dialect.delimiter
    print('time sniff:', time() - start); start = time()
    chunks = read_csv(src, error_bad_lines=False, sep=sep, **kw)
    print('time read_csv:', time() - start)
    count = 0
    frames = list()
    for chunk in chunks:
        frames.append(chunk)
        count += len(chunk)
    print('count: ', count, ', time: ', time() - start, ', resource: ', resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)

test_pandas_to_sql()
# => count:  5240866 , time:  162.62307929992676 , resource:  79,282,176
# => count:  5240866 , time:  69.78917694091797 , resource:  951,816,192
def test_pandas_to_sql(src="/Users/scott.pierce/code/golumn/tmp/contract_items_10m.csv"):
    import resource, os, sqlite3
    from time import time
    from pandas import read_csv
    from hashlib import md5
    start = time() 
    table = '_' + md5(src.encode('utf-8')).hexdigest()
    dst = 'tmp/grid.db'
    os.path.isfile(dst) and os.remove(dst)
    conn = sqlite3.connect(dst)
    for chunk in read_csv(src, chunksize=10000):
        chunk.to_sql(table, conn, if_exists='append', index=False)
    c = conn.cursor()
    c.execute('SELECT COUNT(1) FROM {0}'.format(table))
    count = c.fetchone()[0]
    print('count: ', count, ', time: ', time() - start, ', resource: ', resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)

import sqlite3
dst = 'tmp/golumn.db'
conn = sqlite3.connect(dst)
data = [row for row in conn.execute("select * from _d6e870f764cf31b0e74593493f6f03b1 limit 1 offset 100")]



# time > 1 minute
def test_agate(src="/Users/scott.pierce/code/golumn/tmp/contract_items_10m.csv"):
    import agate
    import agatesql
    table = agate.Table.from_csv(src, sniff_limit=1000)  
    table.to_sql('sqlite3://./foo.sqlite', 'data')

# CSV test
py3 -m golumn tmp/contract_items_10m.csv
# => total time:  45.297314167022705

def panda_test():
    import sqlite3, pandas
    conn = sqlite3.connect('example.db')
    src = "/Users/scott.pierce/code/golumn/tmp/contract_items_100k.csv"
    df = pandas.read_csv(src)
    df.to_sql('bom_utf16', conn, if_exists='append', index=False)

from time import time
a = time(); panda_test(); print('time: %f' % (time() - a))
# => time: 1.608533

def csv_test():
    import sqlite3, pandas
    conn = sqlite3.connect('example.db')
    src = '/Users/scott.pierce/code/golumn/tmp/bom_utf16.csv'
    df = pandas.read_csv(src)
    df.to_sql('bom_utf16', conn, if_exists='append', index=False)


from odo import odo, resource, discover

src = 'tmp/contract_items_10m.csv'
csv = resource(src)
ds = discover(csv)
a = time(); odo(src, 'sqlite:///tmp/output.db::foo', dshape=ds); print('time: %f' % (time() - a))


test_csv_to_sqlite(src='tmp/contract_items_100k.csv')
# => count:  100000 , time:  1.6078600883483887 , resource:  58535936
test_csv_to_sqlite(src='tmp/contract_items_10m.csv')
# => count:  5240866 , time:  54.33652997016907 , resource:  58646528

    
def test_csv_to_sqlite(src="/Users/scott.pierce/code/golumn/tmp/contract_items_10m.csv"):
    import csv, resource, sqlite3
    from time import time
    a = time() 
    rows = list()
    conn = sqlite3.connect('example.db')
    csvreader = csv.reader(open(src, 'r'))
    headers = next(csvreader)
    len_headers = len(headers)
    conn.execute('DROP TABLE IF EXISTS items')
    conn.execute('CREATE TABLE items ({0})'.format(', '.join(headers)))
    insert_stmt = 'INSERT INTO items VALUES ({0})'.format(', '.join(['?' for h in headers]))
    rows = list()
    count = 0
    for row in csvreader:
        rows.append(row[:len_headers])
        count += 1
        if len(rows) > 9980:
            conn.executemany(insert_stmt, rows)
            rows.clear()
    if len(rows) > 0:
        conn.executemany(insert_stmt, rows)
    conn.close()
    print('count: ', count, ', time: ', time() - a, ', resource: ', resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)

test_import_to_sqlite(src="tmp/contract_items_10m.csv")
# => count:  5240866 , time:  53.65821599960327 , resource:  25759744

def test_import_to_sqlite(src="/Users/scott.pierce/code/golumn/tmp/contract_items_10m.csv"):
    import csv, resource
    from golumn.SQLiteImporter import SQLiteImporter
    from time import time
    a = time() 
    rows = list()
    csvreader = csv.reader(open(src, 'r'))
    headers = next(csvreader)
    importer = SQLiteImporter(headers, db='example.db', table='items')
    count = 0
    for row in csvreader:
        rows.append(row[:len(headers)])
        count += 1
        if len(rows) > 9980:
            print('inserting')
            importer.insert(rows)
            rows.clear()
    if len(rows) > 0:
        importer.insert(rows)
    importer.close()
    print('count: ', count, ', time: ', time() - a, ', resource: ', resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)

def print_standard_paths():
    sp = wx.StandardPaths.Get()
    for x in ['GetConfigDir',
            'GetUserConfigDir',
            'GetDataDir',
            'GetLocalDataDir',
            'GetUserDataDir',
            'GetUserLocalDataDir',
            'GetDocumentsDir',
            'GetAppDocumentsDir',
            'GetPluginsDir',
            'GetInstallPrefix',
            'GetResourcesDir',
            'GetTempDir',
            'GetExecutablePath',
            ]:
        print("%s: %s" % (x, getattr(sp, x)()))

def center_on_active_display(frm, size=(1000, 600)):
    active_display = wx.Display.GetFromPoint(wx.GetMousePosition())
    active_area = wx.Display(active_display).ClientArea
    w1,h1 = size
    x2,y2,w2,h2 = active_area
    x1 = int((w2-w1)/2)
    y1 = int((h2-h1)/2)

    # a.ClientArea =>
    #   Value: (4, 23, 1436, 877)
    #   Value: (4, 23, 1436, 877)

    # b.ClientArea => 
    #   Value: (-1028, -1440, 3440, 1440)
    #   Value: (-1028, -1440, 3440, 1440)

