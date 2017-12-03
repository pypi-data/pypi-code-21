#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
from .visvalingamwyatt import simplify_geometry
try:
    import fiona
except ImportError:
    raise ImportError('command line tool requires Fiona')

def main():
    parser = argparse.ArgumentParser('vwsimplify')
    parser.add_argument('input', default='/dev/stdin')
    parser.add_argument('output', default='/dev/stdout')
    parser.add_argument('-p', '--precision', type=int, metavar='int', default=5)

    group = parser.add_mutually_exclusive_group()
    group.add_argument('-t', '--threshold', type=float, metavar='float')
    group.add_argument('-n', '--number', type=int, metavar='int')
    group.add_argument('-r', '--ratio', type=float, metavar='float', help='fraction of points to keep')

    args = parser.parse_args()

    if args.input == '-':
        args.input = '/dev/stdin'

    if args.output == '-':
        args.output = '/dev/stdout'

    if args.number:
        kwargs = {
            'method': 'number',
            'factor': args.number
        }

    elif args.threshold:
        kwargs = {
            'method': 'threshold',
            'factor': args.threshold
        }

    else:
        kwargs = {
            'method': 'ratio',
            'factor': args.ratio or 0.90
        }

    with fiona.drivers():
        with fiona.open(args.input, 'r') as src:
            with fiona.open(args.output, 'w', schema=src.schema, driver=src.driver, crs=src.crs) as sink:
                for feature in src:
                    geom = simplify_geometry(feature['geometry'], **kwargs)
                    feature['geometry']['coordinates'] = geom['coordinates']
                    sink.write(feature)


if __name__ == '__main__':
    main()
