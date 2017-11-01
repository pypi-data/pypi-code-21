from sys import exit

from reportlab.pdfgen import canvas
from reportlab.lib import pagesizes
from reportlab.lib.utils import ImageReader

class PageGeometry(object):
    def __init__(self, page_size, margins=10, portait=True):
        page_size = page_size.upper()

        try:
            page_size_imperial = getattr(pagesizes, page_size)
        except AttributeError as e:
            print(f'Unknown page size "{page_size}"!')
            exit(1)

        self._page_size_imperial = page_size_imperial
        self._page_size = (
            self.convert_fractional_inch_to_mm(page_size_imperial[0]),
            self.convert_fractional_inch_to_mm(page_size_imperial[1]),
        )
        self._margins = margins
        self.portait = portait
        super(PageGeometry, self).__init__()


    @staticmethod
    def convert_fractional_inch_to_mm(value):
        return (value / 72) * 25.4

    @staticmethod
    def convert_mm_to_fractional_inch(value):
        return (value / 25.4) * 72

    def max_printable_dimensions(self):
        return [
            (min(self._page_size) if self.portait else max(self._page_size)) - (2 * self._margins),
            (max(self._page_size) if self.portait else min(self._page_size)) - (2 * self._margins)
        ]

    def generate_pdf(self, images, overlap, f_name = 'out.pdf'):
        _pagesize = (pagesizes.portrait(self._page_size_imperial) if self.portait else pagesizes.landscape(self._page_size_imperial))
        _canvas = canvas.Canvas(f_name, pagesize=_pagesize)
        margin = self.convert_mm_to_fractional_inch(self._margins)
        overlap = self.convert_mm_to_fractional_inch(overlap)

        for image in images:
            img_height = self.convert_mm_to_fractional_inch(image['height_mm'])
            img_width = self.convert_mm_to_fractional_inch(image['width_mm'])
            img_x = margin
            img_y = _pagesize[1] - img_height - margin

            _canvas.drawImage(
                ImageReader(image['image']),
                img_x,
                img_y,
                width=img_width,
                height=img_height,
                preserveAspectRatio=True,
                anchor='sw',
                mask=[0, 0, 0, 0, 0, 0]
            )

            _canvas.setStrokeColorRGB(1, 0, 0)

            if not image['first_col']:
                # draw a line, overlap in, from the leftmost margin
                _canvas.line(
                    margin + overlap,
                    0,
                    margin + overlap,
                    _pagesize[1]
                )

            if not image['first_row']:
                # draw a line, overlap + magin from the top of the page
                _canvas.line(
                    0,
                    _pagesize[1] - margin - overlap,
                    _pagesize[0],
                    _pagesize[1] - margin - overlap
                )

            _canvas.showPage()

        _canvas.save()
