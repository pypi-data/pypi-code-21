#!/usr/bin/env python

from argparse import ArgumentParser, FileType
from sqlalchemy import create_engine
from .params import parse_parameters, PARSERS
from .runner import run_query


def parse_args(argv):
    parser = ArgumentParser(description="""runs a query using sqlalchemy.
    The file specified in --query option is run using the parameters specified in --parameters option.
    You can put multiple statements, and they are run within a single transaction.
    """)
    parser.add_argument("-p", "--parameters", type=parse_parameters,
                        default={},
                        help="""specifies the parameters to be used in running queries.
                        the argument to this option is in the following form: name1:type1=value1[;name2;type2=value2;...].
                        the supported parameter types are: [{}]
                        """.format(', '.join(PARSERS.keys())))
    parser.add_argument("--url", required=True, help="""Python DBAPI url. This is used to connect the database.""")
    parser.add_argument("-q", "--query", type=FileType('r'),
                        required=True, help="the query to run. you may put multiple statement. we accept 'named' format as paramstyle")
    return vars(parser.parse_args(argv))


def main():
    import sys
    opts = parse_args(sys.argv[1:])
    url = opts.get('url')
    query_txt = opts.get('query').read()
    params = opts.get('parameters')
    engine = create_engine(url)
    queries = map(lambda x: x.strip(), query_txt.split(';'))
    queries = list(filter(lambda x: x, queries))
    run_query(engine, queries, params)
