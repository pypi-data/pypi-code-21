import argparse

from lps.input_handler import load_image
from lps.page_geometries import PageGeometry

def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'image_file',
        type=argparse.FileType('rb'),
        help='Image to parse'
    )
    image_dimension_group = parser.add_mutually_exclusive_group(required=True)
    image_dimension_group.add_argument(
        '--width', type=int,
        help='Width of image in millimeters'
    )
    image_dimension_group.add_argument(
        '--height', type=int,
        help='Height of image in millimeters'
    )
    parser.add_argument(
        '--page_size',
        default='a3',
        help='Page size, e.g. a3, a4'
    )
    parser.add_argument(
        '--overlap',
        default=20,
        type=int,
        help='Print overlap in mm'
    )
    parser.add_argument(
        '--margins',
        default=10,
        type=int,
        help='Print margins in mm'
    )
    parser.add_argument(
        '--outfile',
        default='out.pdf',
        help='Filename to save pdf to'
    )
    parser.add_argument(
        '--svg_start_scale',
        default=3,
        type=int,
        help='When using SVG, this is the largest scale factor to attempt to generate an image'
    )
    return parser

def run_cli():
    parser = create_parser()
    args = parser.parse_args()
    print("Loading Image")
    input_image = load_image(args.image_file, args.width, args.height, args.svg_start_scale)
    page_geo = PageGeometry(args.page_size, margins=args.margins, portait=input_image.is_portrait())

    if input_image.fits_on_a_page(page_geo.max_printable_dimensions()):
        print('The image will fit on a single page')
    else:
        print('The image will not fit on a single page')
    print("Calculating crop list")
    crop_list = input_image.calculate_print_chunks(page_geo.max_printable_dimensions(), args.overlap)
    print(f'This will require {len(crop_list)} pages')
    print("Chunking image")
    chunked_images = input_image.chunk_and_annotate_image(crop_list)
    print("Generating PDF")
    page_geo.generate_pdf(chunked_images, args.overlap, f_name=args.outfile)

if __name__ == '__main__':
    run_cli()
