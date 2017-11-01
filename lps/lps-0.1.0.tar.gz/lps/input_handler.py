from io import BytesIO

import cairosvg
from cairocffi import CairoError
from PIL import Image

MAX_PIXELS = 89478485

class InputImage(object):
    def __init__(self, image, scale):
        self.image = image
        self.scale = scale
        super(InputImage, self).__init__()
    
    def is_portrait(self):
        return self.image.height > self.image.width

    def print_width(self):
        return self.image.width / self.scale

    def print_height(self):
        return self.image.height / self.scale

    def fits_on_a_page(self, printable_dimensions):
        printable_dimensions.sort()
        print_dimensions = [self.print_width(), self.print_height()]
        print_dimensions.sort()

        return printable_dimensions[0] >= print_dimensions[0] and printable_dimensions[1] >= print_dimensions[1]

    def calculate_print_chunks(self, printable_dimensions, overlap):
        # returns a matrix of point tuples that define regions of the image to crop
        # and put onto each page

        # [ PAGE, PAGE, PAGE ]
        # [ [(x0, y0), (x1, y1)], [(x0, y0), (x1, y0)], [(x0, y0), (x1, y0)]]
        printable_x = printable_dimensions[0] # mm
        printable_x_scaled = printable_x * self.scale
        printable_y = printable_dimensions[1] # mm
        printable_y_scaled = printable_y * self.scale
        overlap_scaled = overlap * self.scale

        # calculate cols
        cur_x = 0
        x1 = 0
        cols = []

        while x1 < self.image.width:
            x0 = cur_x
            if x0 > 0:
                x0 = x0 - overlap_scaled

            x1 = (x0 + printable_x_scaled)
            if x1 > self.image.width:
                x1 = self.image.width

            cur_x = x1
            cols.append((x0, x1))
        # calculate rows
        cur_y = 0
        y1 = 0
        rows = []

        while y1 < self.image.height:
            y0 = cur_y
            if y0 > 0:
                y0 = y0 - overlap_scaled

            y1 = (y0 + printable_y_scaled)
            if y1 > self.image.width:
                y1 = self.image.width

            cur_y = y1
            rows.append((y0, y1))

        res = []
        for row in rows:
            res.extend([[(x0, row[0]),(x1, row[1])] for x0, x1 in cols])

        return res

    def chunk_and_annotate_image(self, crop_list):
        ''' Returns and array of cropped images '''
        images = []
        # # [
        #     {
        #         'first_row'
        #         'first_col'
        #         'image'
        #         'width' (mm)
        #         'hieght' (mm)
        #     }
        # ]
        for crop_spec in crop_list:
            image = self.image.crop((
                crop_spec[0][0],
                crop_spec[0][1],
                crop_spec[1][0],
                crop_spec[1][1],
            ))
            images.append(
                {
                    'image': image,
                    'first_col': crop_spec[0][0] == 0,
                    'first_row': crop_spec[0][1] == 0,
                    'height_mm': image.height / self.scale,
                    'width_mm': image.width / self.scale,
                }
            )
        return images


def handle_svg(image_file, desired_width, desired_height, start_scale=3):
    im = None
    # try and find a large scale factor for the vector image
    for i in range(start_scale, 0, -1):
        try:
            print(f'Trying to generate raster image of svg at {i}x scale')
            svg_bytes = cairosvg.svg2png(file_obj=image_file, scale=i)
        except CairoError as e:
            pass
        else:
            svg_stream = BytesIO(svg_bytes)
            im = Image.open(svg_stream)

            if im.width * im.height > MAX_PIXELS:
                print(f'Image width or height is greater then {MAX_PIXELS} pixels, trying a lower scale')
                continue

            break

    if im is None:
        raise 'Unable to find a scaling factor for the SVG!'

    # calculate the ACTUAL scale because scale above is not honoured
    if desired_width:
        scale = im.width / desired_width
    else:
        scale = im.height / desired_height

    return InputImage(im, scale)

def load_image(image_file, desired_width, desired_height, start_scale):
    if image_file.name.split('.')[-1] == 'svg':
        return handle_svg(image_file, desired_width, desired_height, start_scale)

    im = Image.open(image_file)

    if desired_width:
        scale = im.width / desired_width
    else:
        scale = im.height / desired_height
    return InputImage(image_file, scale)
