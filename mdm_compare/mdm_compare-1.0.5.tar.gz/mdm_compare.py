import numpy as np


__version__ = '1.0.5'
DEFAULT_PRECISION = 7


def mdm_compare(mdm_file1, mdm_file2, decimal_precision=DEFAULT_PRECISION):
    with open(mdm_file1, 'r') as f1:
        lines1 = f1.readlines()
        with open(mdm_file2, 'r') as f2:
            lines2 = f2.readlines()

            if len(lines1) != len(lines2):
                raise ValueError('Files do not have the same number of lines')

            for idx, (line1, line2) in enumerate(zip(lines1, lines2)):
                if line1 != line2:
                    array1 = np.fromstring(line1, dtype=float, sep=' ')
                    array2 = np.fromstring(line2, dtype=float, sep=' ')
                    try:
                        np.testing.assert_almost_equal(
                            array1,
                            array2,
                            decimal=decimal_precision,
                        )
                    except AssertionError:
                        raise ValueError("Files are different on line %d" % (idx+1))
    return True

def main(): #pragma: no cover
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        description='Compare 2 experiment results stored in the MDM file format'
    )
    parser.add_argument(
        'file',
        nargs=2,
        help='Experiment result stored in the MDM file format'
    )
    parser.add_argument(
        '-p',
        '--precision',
        default=DEFAULT_PRECISION,
        type=int,
        help="Decimal precision (at %d decimals by default) required to " \
             "consider MDM files the same" % DEFAULT_PRECISION
    )
    parser.add_argument(
        '--version',
        action='version',
        version="%(prog)s " + __version__
    )
    args = parser.parse_args()


    try:
        mdm_compare(*args.file, decimal_precision=args.precision)
        print 'Files can be considered the same'
    except Exception, e:
        print >> sys.stderr, "ERROR:", e
        sys.exit(1)

if __name__ == '__main__':
    main()
