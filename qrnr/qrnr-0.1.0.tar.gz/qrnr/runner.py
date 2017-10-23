from sqlalchemy.sql.expression import text


def run_query(engine, queries, params):
    """
    Parameters
    ----------
    engine : sqlalchemy.Engine
    queries : a list of str
    params : a dict or a tuple of parameters

    Returns
    -------
    None

    >>> from sqlalchemy import create_engine
    >>> engine = create_engine('sqlite://')
    >>> queries = [
    ...   "CREATE TABLE foo(key int, val text)",
    ...   "INSERT INTO foo(key, val) VALUES(1, 'foo'), (2, :val)"
    ... ]
    >>> run_query(engine, queries, dict(val='par'))
    >>> engine.execute("SELECT COUNT(1) FROM foo").fetchall()[0][0] == 2
    True
    >>> engine.execute("SELECT val FROM foo WHERE key = 2").fetchall()[0][0] == 'par'
    True
    """
    with engine.begin() as conn:
        for query in queries:
            q = text(query)
            known_pars = {k: v for k, v in params.items() if k in q._bindparams}
            conn.execute(q.bindparams(**known_pars))



if __name__ == '__main__':
    import doctest
    doctest.testmod()
