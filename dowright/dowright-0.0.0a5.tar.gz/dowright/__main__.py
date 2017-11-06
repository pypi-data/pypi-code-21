import argparse
import logging
from pathlib import Path

from .spec import parse_spec
from .build import Builder
from . import inventory

log = logging.getLogger('dowright')
log.addHandler(logging.NullHandler())


def setup_logging(level):
    level = logging.getLevelName(level.upper())
    log_format = '{asctime} {levelname}: {message}'
    datefmt = '%Y-%m-%d_%H:%M:%S'
    logging.basicConfig(
        level=level, format=log_format, datefmt=datefmt, style='{'
    )


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('spec', default='dowright.yml', nargs='?',
                        help='YAML specification for droplet management')
    parser.add_argument('-b','--build',action='store_true')
    parser.add_argument('-w','--wait',action='store_true')
    parser.add_argument('-i','--inventory',action='store_true')
    parser.add_argument('-I','--ips',action='store_true')
    parser.add_argument('-d','--domains',action='store_true')
    parser.add_argument('--destroy',action='store_true')
    parser.add_argument('--loglevel', default='info')

    args = parser.parse_args()

    return args


def main():
    args = get_args()

    setup_logging(args.loglevel)

    spec_path = Path(args.spec).expanduser().resolve()
    spec = parse_spec(spec_path)

    builder = Builder(spec)

    if args.build:
        builder.build_droplets()

    if args.wait:
        builder.wait_for_build()

    if args.ips:
        builder.configure_floating_ips()

    if args.domains:
        builder.configure_domains()
        
    if args.inventory:
        inventory.create_inventory(builder)

    if args.destroy:
        builder.destroy_droplets()


if __name__=='__main__':
    main()
