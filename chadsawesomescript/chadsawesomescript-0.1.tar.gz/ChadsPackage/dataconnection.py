import pyodbc 

def IQuery(n):
    cnxn = pyodbc.connect("Driver={SQL Server Native Client 11.0};"
                      "Server=CHADSSURFACE_01\SQLEXPRESS;"
                      "Database=PowerDominator;"
                      "Trusted_Connection=yes;")
    cursor = cnxn.cursor()
    cursor.execute('SELECT * FROM Area')

    for row in cursor:
        print('row = %r' % (row,))