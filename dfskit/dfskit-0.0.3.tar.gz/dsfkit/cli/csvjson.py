import argparse
import sys
from argparse import ArgumentParser

from dsfkit.utilities import csvjson


def main():
    parser = ArgumentParser()
    parser.add_argument('csv_file', metavar='CSV_FILE', nargs='?', type=argparse.FileType('r'),
                        default=sys.stdin, help='CSV file (if empty stdin is used)')
    parser.add_argument('json_file', metavar='JSON_FILE', nargs='?', type=argparse.FileType('w'),
                        default=sys.stdout, help='JSON file (if empty, stdout is used)')
    parser.add_argument('--sort', help = "Sort JSON output", action="store_true")
    parser.add_argument('--pretty', help="Pretty print JSON output", action="store_true")
    args = parser.parse_args()

    csv_json = csvjson.CsvJson(sort_columns=args.sort, pretty_print=args.pretty)
    args.json_file.write(csv_json.convert(args.csv_file))
    args.json_file.write('\n')
    args.json_file.flush()
    args.json_file.close()


if __name__ == '__main__':
    main()
