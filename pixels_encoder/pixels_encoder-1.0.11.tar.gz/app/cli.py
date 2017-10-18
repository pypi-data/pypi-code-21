import argparse
import os.path
from .pixels_encoder import PixelsEncoder
from .helpers import *
import os


def cli():
    parser = argparse.ArgumentParser(description='Image pixels info extractor')
    parser.add_argument('-f', '--folder', type=str, help='input folder with images')
    parser.add_argument('-i', '--image', type=str, help='input image')
    parser.add_argument('-o', '--output', type=str, help='output file or folder', default=None)
    parser.add_argument('-p', '--pretty', type=bool, help='is pretty output json', default=False)
    args = parser.parse_args()

    if args.image and is_png_img(args.image):
        _encode(args.image, args.output, args.pretty)
    elif args.folder and os.path.isdir(args.folder):
        _encode_folder(args.folder, args.output, args.pretty)
    else:
        print("❌ image/folder argument wasn't found or doesn't exist!")
        exit(1)


def _encode(image, output, pretty):
    try:
        output_file = output if output else remove_path_ext(image) + '.json'
        encoder = PixelsEncoder(image)
        encoder.encode_pixels_info(output_file, pretty)
        print("%s image pixels info was successfully written to %s" % (image, output_file))
    except Exception as error:
        print("failed to write to file %s with error: %s" % (output, str(error)))


def _encode_folder(f, output, pretty):
    output_folder = output if output else os.path.join(f, 'output')
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)

    for img_path in gather_pngs_in(f):
        output_filename = remove_path_ext(filename_at(img_path)) + '.json'
        output_file = os.path.join(output_folder, output_filename)
        _encode(img_path, output_file, pretty)
