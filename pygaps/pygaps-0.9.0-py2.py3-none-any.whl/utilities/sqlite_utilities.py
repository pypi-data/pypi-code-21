"""
This module contains general functions for SQL query building
"""


def build_update(table, to_set, where, prefix=None):
    """
    Builds an update request

    Parameters
    ----------
    table : str
        table where query will be directed
    to_set: iterable
        the list of columns to update
    where: iterable
        the list of conditions to constrain the query
    prefix: str, optional
        the prefix to introduce to the second part of the constraint

    Returns
    -------
    str
        built query
    """

    sql_q = 'UPDATE \"' + table + '\"'
    sql_q += " SET "
    sql_q += ', '.join('{0} = :{0}'.format(w) for w in to_set)
    sql_q += ' WHERE '
    if prefix is not None:
        sql_q += ' AND '.join('{0} = :{1}{0}'.format(w, prefix) for w in where)
    else:
        sql_q += ' AND '.join('{0} = :{0}'.format(w) for w in where)

    return sql_q


def build_insert(table, to_insert):
    """
    Builds an insert request

    Parameters
    ----------
    table : str
        table where query will be directed
    to_insert: iterable
        the list of columns where the values will be inserted

    Returns
    -------
    str
        built query
    """

    sql_q = 'INSERT INTO \"' + table + '\" ('
    sql_q += ', '.join('{0}'.format(w) for w in to_insert)
    sql_q += ') VALUES ('
    sql_q += ', '.join(':{0}'.format(w) for w in to_insert)
    sql_q += ')'

    return sql_q


def build_select(table, to_select, where):
    """
    Builds an select request

    Parameters
    ----------
    table : str
        table where query will be directed
    to_set: iterable
        the list of columns to select
    where: iterable
        the list of conditions to constrain the query

    Returns
    -------
    str
        built query
    """

    sql_q = "SELECT "
    sql_q += ', '.join('{0}'.format(w) for w in to_select)
    sql_q += ' FROM \"' + table + '\"'
    if len(where) > 0:
        sql_q += ' WHERE '
        sql_q += ' AND '.join('{0} = :{0}'.format(w) for w in where)

    return sql_q


def build_delete(table, where):
    """
    Builds a delete request

    Parameters
    ----------
    table : str
        table where query will be directed
    where: iterable
        the list of conditions to constrain the query

    Returns
    -------
    str
        built query
    """

    sql_q = "DELETE "
    sql_q += 'FROM \"' + table + '\"'
    sql_q += ' WHERE '
    sql_q += ' AND '.join('{0} = :{0}'.format(w) for w in where)

    return sql_q
