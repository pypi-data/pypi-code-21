import logging
import sys
import time

from light import LightProcessor
from watcher import Watcher


def parse_args():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--input', help='Path to input directory', required=True)
    parser.add_argument('--output', help='Path to output directory', required=True)
    parser.add_argument('--unpacker', help='Path to unpacker', required=True)
    parser.add_argument('--aux', help='Path to auxiliary script', required=False)
    parser.add_argument('--timeout', help='Time file much to untouched to be considered complete', required=True, type=int)
    parser.add_argument('--log', help='Path to log file')
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
        file_log = logging.FileHandler(args.log)
        file_log.setLevel(logging.INFO)
        file_log.setFormatter(formatter)
        root.addHandler(file_log)

    root.info("Started RUP light")

    processor = LightProcessor(unpacker=args.unpacker,
                               output_dir=args.output,
                               aux=args.aux)

    w = Watcher(args.input, args.timeout)
    processor.attach(w)
    w.run()

    while True:
        time.sleep(1000)


if __name__ == '__main__':

    main()


