"""
Send metric value to the graphite (carbon)

Usage:
    graphiti <host> <metric> <value> [<time>] [options]

Options:
  -h --help                 Show this screen.
  -p --port=PORT            Port for the backend [default: 2004]
  -v --verbose              Verbose output

PS time should be unix timestamp or in format "%Y-%m-%dT%H:%M:%S"

"""
import calendar
import datetime


def parse_number(value):
    try:
        return int(value)
    except ValueError:
        return float(value)


def parse_date(value):
    try:
        return int(value)
    except ValueError:
        pass

    dt = datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")
    return calendar.timegm(dt.utctimetuple())


def main():
    import docopt
    from graphiti.client import Client
    opt = docopt.docopt(__doc__)
    timestamp = opt["<time>"]
    if timestamp:
        timestamp = parse_date(timestamp)
    value = parse_number(opt["<value>"])
    if opt["--verbose"]:
        import logging
        logging.basicConfig(level=logging.DEBUG)

    client = Client(opt["<host>"], int(opt["--port"]), verbose=opt.get("--verbose"))
    client.send(opt["<metric>"], value, timestamp)
    client.flush(10)
    if client.messages:
        client.logger.warning("%d messages were not sent", len(client.messages))


if __name__ == '__main__':
    main()
