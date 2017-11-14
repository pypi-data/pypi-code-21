"""Pull centre specific data.
"""


# In the future this data can be pulled out of here into a configuration file
MACHINE_MAP = {
    '2619': 'rccc',
    '2694': 'rccc',
    '4299': 'nbccc'
}
TIMEZONE = {
    'nbccc': 'Australia/Sydney',
    'rccc': 'Australia/Sydney'
}

SQL_USERS = {
    'nbccc': 'physics',
    'nbccc-from-rccc': 'physics',
    'rccc': 'physics'
}
SQL_SERVERS = {
    'nbccc': 'nbccc-msq',
    'nbccc-from-rccc': 'physsvr',
    'rccc': 'msqsql'
}

