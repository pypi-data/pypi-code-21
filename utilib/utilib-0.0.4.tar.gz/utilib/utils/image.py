from PIL import Image, ImageOps
from io import BytesIO
from utilib.core.http import async_fetch_url
import qrcode
import six

NUL = b'\x00'
EOT = b'\x04'
ENQ = b'\x05'
DLE = b'\x10'
DC4 = b'\x14'
CAN = b'\x18'
ESC = b'\x1b'
FS = b'\x1c'
GS = b'\x1d'
NEWLINE = b'\x1b\x4a\x30'


def _generate_qrcode_image(text, **kwargs):
    _image = qrcode.make(
        text,
        error_correction=qrcode.ERROR_CORRECT_H,
        **kwargs)
    return _image


def generate_qrcode_image(text, **kwargs):

    _image = qrcode.make(
        text,
        error_correction=qrcode.ERROR_CORRECT_H,
        **kwargs)
    size = 384, int(_image.size[1] * 384 / _image.size[0] + .5)
    return _image.resize(size).convert('1')


def get_image_content(_image):
    if isinstance(_image, bytes):
        _c = BytesIO()
        _c.write(_image)
        _image = Image.open(_c).convert('RGBA')
    elif isinstance(_image, BytesIO):
        _image = Image.open(_image).convert('RGBA')
    _bg = Image.new("RGB", _image.size, (255, 255, 255))
    _bg.paste(_image, (0, 0), _image)
    _content = BytesIO()
    _bg.save(_content, format='JPEG')
    return _content.getvalue()


class ImageHelper:

    @staticmethod
    def _int_low_high(inp_number, out_bytes):
        """ Generate multiple bytes for a number: In lower and higher parts,
        or more parts as needed.

        :param inp_number: Input number
        :param out_bytes: The number of bytes to output (1 - 4).
        """
        max_input = (256 << (out_bytes * 8) - 1)
        if not 1 <= out_bytes <= 4:
            raise ValueError('Can only output 1-4 bytes')
        if not 0 <= inp_number <= max_input:
            raise ValueError(
                'Number too large. Can only output up to '
                '{0} in {1} bytes'.format(max_input, out_bytes))
        outp = b''
        for _ in range(0, out_bytes):
            outp += six.int2byte(inp_number % 256)
            inp_number //= 256
        return outp

    @staticmethod
    def image2bin_v2(_image, position=0):
        header = b'\x1b' + b'\x09' + b'\x1b' + b'\xfe' + bytes.fromhex(
            '%02d' % position) + ImageHelper._int_low_high(
            int(_image.width / 8),
            2) + ImageHelper._int_low_high(
            _image.height, 2)
        return header + _image.tobytes() + b'\x1b' + b'\x15'

    @staticmethod
    def image2bin(_image):
        density_byte = 0
        header = GS + b"v0" + six.int2byte(
            density_byte) + ImageHelper._int_low_high(
            int(_image.width / 8),
            2) + ImageHelper._int_low_high(
            _image.height, 2)
        return header + _image.tobytes() + b'\n' * 3

    @staticmethod
    def get_hex_from_bin(bin_content):
        content = bin_content
        result = ''
        count = 0
        while 1:
            if count > len(content) - 1:
                break
            c = content[count]
            count += 1
            result += hex(ord(c)).upper()[2:] + ' ' if not len(
                hex(ord(c)).upper()[2:]) == 1 else '0' + hex(
                ord(c)).upper()[2:] + ' '
        return result

    @staticmethod
    def get_receipt_image(image):
        image = ImageOps.invert(image.convert('L'))
        size = 384, int(image.size[1] * 384 / image.size[0] + .5)
        return image.resize(size).convert('1')

    @staticmethod
    async def get_template_demo(content):
        image = Image.open(content)
        image = ImageHelper.get_receipt_image(image)
        template_content = await async_fetch_url(
            'https://s3.cn-north-1.amazonaws.com.cn'
            '/ad-dist/template.png')
        template_content = template_content.body
        _template = BytesIO()
        _template.write(template_content)
        template_image = Image.open(_template)
        template_image = ImageHelper.get_receipt_image(template_image)
        blank_image = Image.new('1',
                                (384, template_image.size[1] + image.size[1]))
        blank_image.paste(template_image, (0, 0))
        blank_image.paste(image, (0, template_image.size[1]))
        return blank_image
