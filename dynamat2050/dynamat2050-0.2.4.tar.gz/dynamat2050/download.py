import logging
import sys
import os
import json
from collections import deque
from datetime import datetime, timedelta

from .dynamat2050 import Client, DynamatError

log = logging.getLogger("dynamat2050")
logging.basicConfig(level=logging.INFO)

now = datetime.now()
one_year = timedelta(days=365)


class DynamatConfigError(DynamatError): pass

class ArgParser(object):
    """
    Check args for command line script
    First arg is the config file
    Second arg is the command
    """
    def __init__(self, *args):
        print("\n==========================")
        print(" downloading dynamat data ")
        print("==========================\n")
        self.args = deque(*args)
        self.script = self.args.popleft()
        try:
            self.config_uri = self.args.popleft()
        except IndexError:
            raise DynamatConfigError("Must provide a config file as first argument")
        if not os.path.exists(self.config_uri):
            raise DynamatConfigError("First argument must be a valid config file")
        try:
            self.command = self.args.popleft()
        except IndexError:
            raise DynamatConfigError("No command provided")
        if self.command not in allowed_commands:
            raise DynamatConfigError("Command '{}' not recognised, use one of [{}]".format(self.command, ','.join(allowed_commands)))
        try:
            self.outdir = self.args.popleft()
        except IndexError:
            raise DynamatConfigError("No output directory provided")
        self.args = list(self.args)

def client_from_config(config):
    try:
        url, username, password = config.pop('url'), config.pop('username'), config.pop('password')
    except KeyError as err:
        raise DynamatConfigError("Bad config file: {}".format(err))
    return Client(url=url, username=username, password=password)

def download(*args):
    """
    Deprecated in favour of command line scripts (see setup.py entry points)
    """
    try:
        args = ArgParser(args)
    except DynamatConfigError as err:
        log.error(err)

    with open(args.config_uri) as f:
        config = json.load(f)
    client = client_from_config(config)
    if args.command == "meters":
        log.info("attempting to get meters list")
        outfile = os.path.join(args.outdir, "meters.json")
        with open(outfile, 'w') as f:
            json.dump(client.meters(), f, indent=2, sort_keys=True)
    elif args.command == "meter_data":
        for meter in config['meters']:
            outfile = os.path.join(args.outdir, "meter_{}.json".format(meter))
            log.info("getting data for meter_{}".format(meter))
            data = client.meter_data(meter, now - one_year, now).decode('utf-8')
            with open(outfile, 'w') as f:
                log.info("created {}".format(outfile))
                json.dump(data, f, indent=2, sort_keys=True)


def pop_client(args):
    try:
        config_uri = args.popleft()
    except IndexError:
        raise DynamatConfigError("Must provide a config file as first argument")
    if not os.path.exists(config_uri):
        raise DynamatConfigError("First argument must be a valid config file")
    with open(config_uri) as f:
        config = json.load(f)
    return client_from_config(config)


def meters(argv=sys.argv):
    """
    Command line script for downloading meters
    """
    log.info("")
    log.info("|=========================|")
    log.info("| downloading meters list |")
    log.info("|=========================|")
    log.info("")
    args = deque(argv)
    script = args.popleft()
    try:
        client = pop_client(args)
    except DynamatConfigError as err:
        log.error(err)
        exit()

    log.info("attempting to get meters list")
    meters = client.meters()

    try:
        outdir = args.popleft()
    except IndexError:
        print(json.dumps(meters, indent=2, sort_keys=True))
    else:
        outfile = os.path.join(outdir, "meters.json")
        log.info("writing to '{}'".format(outfile))
        with open(outfile, 'w') as f:
            json.dump(meters, f, indent=2, sort_keys=True)


def data(argv=sys.argv):
    """
    Command line script for downloading meter data
    """
    log.info("")
    log.info("|=========================|")
    log.info("| downloading meter data  |")
    log.info("|=========================|")
    log.info("")
    args = deque(argv)
    script = args.popleft()
    try:
        client = pop_client(args)
    except DynamatConfigError as err:
        log.error(err)

    outdir = 'output'
    try:
        os.makedirs(outdir)
    except FileExistsError:
        pass
    for meter in args:
        log.info("attempting to get meter data for '{}'".format(meter))
        data = client.meter_data(meter, now - one_year, now).decode('utf-8')
        data = json.loads(data)
        outfile = os.path.join(outdir, "{}.json".format(meter))
        log.info("writing to '{}'".format(outfile))
        with open(outfile, 'w') as f:
            json.dump(data, f, indent=2, sort_keys=True)


if __name__ == "__main__":
    main(sys.argv)
