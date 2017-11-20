import logging
from argparse import ArgumentParser

from .mac2vendors import write_mac_json, _assert_mapping_file_exists, get_mac_vendor

logger = logging.getLogger(__name__)

parser = ArgumentParser("mtv")

sub_parsers = parser.add_subparsers(help='[command] help', dest="command")

writeParser = sub_parsers.add_parser("write",
                                     help="Write the vendor mapping json destination to the file path given via --path."
                                          "Defaults to vendors.json")

writeParser.add_argument("-p", "--path", type=str, default="./vendors.json", )

macParser = sub_parsers.add_parser("mac", help="Translates the mac address to a vendor mapping.")

macParser.add_argument("mac_address", type=str, default="",
                       help="the mac to translate. A mac looks like this: xx:xx:xx:xx:xx:xx with x hexadecimal.")
macParser.add_argument("-s", "--strict", default=False, action="store_true",
                       help="Check if a valid mac_address was inserted")


def mtv():
    args = parser.parse_args()
    if args.command == "write":
        write_mac_json("vendors.txt", args.path)
    elif args.command == "mac":
        _assert_mapping_file_exists(force_refresh=True)
        mapping = get_mac_vendor("vendors.json", mac_address=args.mac_address, strict=args.strict)
        if mapping is not None:
            print(mapping)
    else:
        parser.print_help()


if __name__ == '__main__':
    mtv()
