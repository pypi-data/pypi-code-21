import sys
from jinja2 import Template
from pprint import pprint
from .argsc import argsc
from .datafilesc import datafilesc


def output_text(data):
    # Print full json
    pprint(data)


def output_adif(data):
    # Jinja2 template for ADIF file header
    with open(datafilesc.get("templates/header_template.adif")) as file:
        adif_header = file.read()
    print(adif_header)

    # Jinja2 template for each ADIF QSO
    with open(datafilesc.get("templates/qso_row_template.adif")) as file:
        adif_row_template = file.read()
    adif_row = Template(adif_row_template)

    for q in data['qsos']:
        qso_data = {k: v for d in [data, q] for k, v in d.items()}
        print(adif_row.render(qso_data))


def main():
    args = argsc.get_args(sys.argv[1:])

    # Output
    if args.output == 'text':
        output_text(vars(args))

    elif args.output == 'adif':
        output_adif(vars(args))


if __name__ == "__main__":
    main()
