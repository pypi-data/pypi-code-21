"""
A command-line tool for spliting POV-Ray density file (DF3)
to a series of separate images.

"""

from __future__ import print_function
import sys
import os
import argparse
import struct

from PIL import Image

from df3tools.exceptions import Df3Exception


def from_big_endian(bytestring):
    """ Convert big-endian bytestring to int """
    bytestring = bytestring.rjust(4, b'\x00')
    return struct.unpack(">L", bytestring)[0]


def split_by_n(seq, chunk_size):
    """ Generator splitting a sequence into chunks """
    while seq:
        yield seq[:chunk_size]
        seq = seq[chunk_size:]


def detect_size(df3_file, silent):
    """
    Detect image size and number of layers.

    :param df3_file: DF3 file descriptor.
    :param silent: suppress output (info messages, progress etc.)

    :returns: Tuple with sizes.

    """
    header = df3_file.read(6)
    sizes = [from_big_endian(v) for v in split_by_n(header, 2)]
    width, height, num_layers = sizes
    if not silent:
        print("Size: %dx%d, %d layers" % (width, height, num_layers))

    return (width, height, num_layers)


def detect_byte_width(data, num_voxels, silent):
    """
    Detect byte width.

    :param data: Byte string with DF3 body.
    :param num_voxels: Number of voxels in file.
    :param silent: suppress output (info messages, progress etc.)

    """
    byte_width = int(float(len(data)) / num_voxels)
    if not silent:
        plural = ' s'[byte_width > 1]
        print("Voxel resolution: %d byte%s" % (byte_width, plural))

    return byte_width


def df3split(filename, prefix="layer", img_format='tga', silent=True):
    """
    Split POV-Ray density file (DF3) to a series of separate images.

    :param filename: path to DF3 file to process
    :param prefix: output files prefix
    :param img_format: output files format (tga, png, etc.)
    :param silent: suppress output (info messages, progress etc.)

    """
    if not os.path.isfile(filename):
        raise Df3Exception("File not found: " + filename)

    with open(filename, "rb") as df3_file:
        width, height, num_layers = detect_size(df3_file, silent)

        data = df3_file.read()
        detect_byte_width(data, width * height * num_layers, silent)

        # parse data and save images
        for img_num, img_data in enumerate(split_by_n(data, width * height)):
            layer_num = str(img_num).zfill(len(str(num_layers)))
            img = Image.new("L", (width, height))
            img.putdata(img_data)
            img.save("%s%s.%s" % (prefix, layer_num, img_format.lower()))
            percentage = float(img_num + 1) / num_layers * 100
            if not silent:
                sys.stdout.write("Processing data [%.2f%%]\r" % percentage)
                sys.stdout.flush()

        if not silent:
            print("\nDone.")


def main():
    """ Main script execution """
    parser = argparse.ArgumentParser(description="""
    Split POV-Ray density file (DF3) to a series of separate images
    """)
    parser.add_argument("df3file", help="DF3 filename, including path")
    parser.add_argument("-t", "--format", type=str,
                        choices=["tga", "png"],
                        default="tga",
                        help="Output files format")
    parser.add_argument("-p", "--prefix", type=str,
                        default="layer",
                        help="Output files prefix")
    parser.add_argument("-s", "--silent", help="Suppress output",
                        default=False, action="store_true")

    args = parser.parse_args()

    df3split(args.df3file, args.prefix, args.format, args.silent)
