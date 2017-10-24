from __future__ import print_function
import argparse
import datetime
import json
import os
from .datafilesc import datafilesc


class argsc(object):
    @staticmethod
    def get_defaults():
        # JSON - personal defaults (callsign, mygrid, rig, power)
        defaults = {"operator": "N0CALL", "mygrid": "JA00",
                    "myrig": "Kenwood TH-D72A", "txpwr": "5"}

        defaults_dir = os.getenv('HOME') + '/.pysatadif'
        defaults_file = defaults_dir + '/defaults.json'

        if not os.path.isdir(defaults_dir):
            os.mkdir(defaults_dir)

        if not os.path.isfile(defaults_file):
            with open(defaults_file, 'x') as file:
                json.dump(defaults, file)

        if os.path.isdir(defaults_dir) and os.path.isfile(defaults_file):
            with open(defaults_file) as file:
                defaults = json.loads(file.read())
        return defaults

    @staticmethod
    def get_args(arguments):

        # Get json default values from file
        jd = argsc.get_defaults()

        # Get date values from today
        ymd = datetime.datetime.utcnow().strftime('%Y%m%d')

        p = argparse.ArgumentParser(
                description=__doc__,
                formatter_class=argparse.RawDescriptionHelpFormatter)

        p.add_argument('-s', '--satname', required=True,
                       help="Satellites to track", default=None)

        p.add_argument('-n', '--timeon', required=True,
                       help="Start time of QSO (HHMMSS)", default=None)

        p.add_argument('-f', '--timeoff',
                       help="End time of QSO (HHMMSS)", default=None)

        p.add_argument('-d', '--qsodate',
                       help="QSO Date (" + ymd + ")", default=ymd)

        p.add_argument('-g', '--mygrid', help="My grid square",
                       default=jd['mygrid'] if 'mygrid' in jd else None)

        p.add_argument('-r', '--myrig', help="My rig",
                       default=jd['myrig'] if 'myrig' in jd else None)

        p.add_argument('-c', '--operator', help="My callsign",
                       default=jd['operator'] if 'operator' in jd else None)

        p.add_argument('-t', '--txpwr', help="TX Power",
                       default=jd['txpwr'] if 'txpwr' in jd else None)

        p.add_argument('-q', '--qso', required=True, action='append',
                       help="QSO callsign and optionally grid (eg N0CALL,DN70)")

        p.add_argument('-p', '--propmode',
                       help=argparse.SUPPRESS, default='SAT')

        p.add_argument('-o', '--output',
                       help="Output Format (text, adif)", default='text')

        p.add_argument('-v', '--verbose', action='count',
                       help="Print verbose debugging messages", default=None)

        args = p.parse_args(arguments)
        dargs = vars(args)

        # ------------------------------------------------------------ #
        # Data validation

        # If we get HHMM, then add on 00 for seconds
        if len(args.timeon) == 4:
            args.timeon = args.timeon + '00'

        # If we get a timeon but no timeoff, just assume it's the same
        if not args.timeoff:
            args.timeoff = args.timeon

        # ------------------------------------------------------------ #

        # Load satellite specific defaults (band, frequencies, mode)
        with open(datafilesc.get("sats/" + args.satname + ".json")) as file:
            satinfo = json.loads(file.read())

        for key, value in satinfo[args.satname].items():
            try:
                # Python 2
                key = key.encode('utf-8') if isinstance(key, unicode) else key
                value = value.encode('utf-8') if isinstance(value, unicode) else value
            except NameError:
                # Python 3 (nothing)
                pass

            dargs[key] = value

        # ------------------------------------------------------------ #

        # Reformat the qso stuff
        args.qsos = []
        for q in args.qso:
            if ',' in q:
                args.qsos.append({'call': q.split(',')[0], 'grid': q.split(',')[1]})
            else:
                args.qsos.append({'call': q})

        return args


if __name__ == "__main__":
    import sys
    args = argsc.get_args(sys.argv[1:])
    print(args)
