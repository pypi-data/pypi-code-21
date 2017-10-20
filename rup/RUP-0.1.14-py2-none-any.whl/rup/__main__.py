import logging
from logging.handlers import WatchedFileHandler
import signal
import threading
import time
import sys
import yaml

from collector import Collector
from processor import Processor
from rules import parse_rules_from_file
from watcher import Watcher, DirectoryIterator
from rundb.client import RunDbc


def parse_config(path):
    with open(path, 'r') as f:
        return yaml.safe_load(f)


def parse_args():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--rules', help='Path to rules file', required=True)
    parser.add_argument('--config', help='Path to rules file', required=True)
    parser.add_argument('--log', help='Path to log file')
    parser.add_argument('--iterate', help='Iterates a directory and exits')
    return parser.parse_args()


def main():
    args = parse_args()

    root = logging.getLogger()
    root.setLevel(logging.INFO)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(filename)s:%(lineno)d - %(name)s:%(funcName)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    root.addHandler(ch)
    if args.log:
        file_log = WatchedFileHandler(args.log)
        file_log.setLevel(logging.INFO)
        file_log.setFormatter(formatter)
        root.addHandler(file_log)

    root.info("Started RUP")

    settings_file = args.config
    rules_file = args.rules

    settings = parse_config(settings_file)

    rules = parse_rules_from_file(rules_file)

    search = RunDbc(settings['runDB']['API_key'], settings['runDB']['host'])

    col = Collector()

    processor = Processor(search, rules, settings['hostname'])

    processor.set_rules(parse_rules_from_file(rules_file))
    processor.attach_collector(col)

    if args.iterate:
        w = DirectoryIterator(str(args.iterate))
        col.attach(w)
        w.run()

    else:
        watchers = []
        timeout = int(settings['watch']['timeout'])
        for d in settings['watch']['directories']:

            w = Watcher(d, timeout)
            col.attach(w)
            w.run()
            watchers.append(w)

            w = DirectoryIterator(d)
            col.attach(w)
            t = threading.Thread(target=w.run)
            t.daemon = True
            t.start()


        def sighup_handler(_, __):
            log = logging.getLogger("SIGHUP")
            log.info("Received SIGHUP. Reloading {} and {}".format(rules_file, settings_file))
            try:
                processor.set_rules(parse_rules_from_file(rules_file))
            except Exception as e:
                log.error("Failed reloading rules due to: {}".format(e.message))

        signal.signal(signal.SIGHUP, sighup_handler)

        while True:
            time.sleep(1000)


if __name__ == '__main__':

    main()


