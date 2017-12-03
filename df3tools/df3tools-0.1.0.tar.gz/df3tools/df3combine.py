"""
A command-line tool for combining multiple image files into
POV-Ray density file (DF3).

"""

from __future__ import print_function
import sys
import argparse
import struct
import glob

from PIL import Image

from df3tools.exceptions import Df3Exception


def to_big_endian(value):
    """ Convert integer to big-endian byte string """
    return struct.pack(">L", value)


def detect_size(prefix, silent):
    """
    Detect image size and number of layers.

    :param prefix: input files prefix
    :param silent: suppress output (info messages, progress etc.)

    :returns: Tuple with sizes.

    """
    files = sorted(glob.glob(prefix + "*"))
    num_layers = len(files)
    if num_layers == 0:
        raise Df3Exception("No files found with prefix '%s'" % prefix)

    width, height = Image.open(files[0]).size
    if not silent:
        print("Size: %dx%d, %d layers" % (width, height, num_layers))

    return (files, width, height, num_layers)


def df3combine(filename, prefix="layer", silent=True):
    """
    Combine a series of separate images into POV-Ray density file (DF3).

    :param filename: path to resulting DF3 file
    :param prefix: input files prefix
    :param silent: suppress output (info messages, progress etc.)

    """
    files, width, height, num_layers = detect_size(prefix, silent)

    with open(filename, "wb") as df3_file:
        # write header
        df3_file.write(to_big_endian(width)[-2:])
        df3_file.write(to_big_endian(height)[-2:])
        df3_file.write(to_big_endian(num_layers)[-2:])

        # write layers data
        for img_num, img_name in enumerate(files):
            img = Image.open(img_name)
            img_data = img.convert("L").tobytes("raw", "L")
            df3_file.write(img_data)
            percentage = float(img_num + 1) / num_layers * 100
            if not silent:
                sys.stdout.write("Processing data [%.2f%%]\r" % percentage)
                sys.stdout.flush()

        if not silent:
            print("\nDone.")


def main():
    """ Main script execution """
    parser = argparse.ArgumentParser(description="""
    Combine a series of separate images into POV-Ray density file (DF3)
    """)
    parser.add_argument("df3file", help="Resulting DF3 filename")
    parser.add_argument("-p", "--prefix", type=str,
                        default="layer",
                        help="Input files prefix")
    parser.add_argument("-s", "--silent", help="Suppress output",
                        default=False, action="store_true")

    args = parser.parse_args()

    df3combine(args.df3file, args.prefix, args.silent)
