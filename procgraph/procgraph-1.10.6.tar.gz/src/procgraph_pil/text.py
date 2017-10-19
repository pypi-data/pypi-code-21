import os
import subprocess

import numpy

from procgraph import Block, BadConfig, ETERNITY
from procgraph.core.visualization import info as info_main, error as error_main

from .pil_conversions import Image_from_array
from contracts import contract
from procgraph_pil.pil_format_paragraph import format_paragraph


__all__ = ['Text']

class Text(Block):
    ''' This block provides text overlays over an image. 
    
    This block is very powerful, but the configuration is a bit complicated.
    
    You should provide a list of dictionary in the configuration variable 
    ``texts``. Each dictionary in the list describes how and where to write
    one piece of text.
     
    An example of valid configuration is the following: ::
    
        text.texts = [{string: "raw image", position: [10,30], halign: left, 
                      color: black, bg: white }]
    
    The meaning of the fields is as follow:
    
    ``string``
      Text to display. See the section below about keyword expansion.
      
    ``position``
      Array of two integers giving the position of the text in the image
      
    ``color``
      Text color. It can be a keyword color or an hexadecimal string 
      (``white`` or ``#ffffff``).
      
    ``bg``
      background color
    
    ``halign``
      Horizontal alignment. 
      Choose between ``left`` (default), ``center``, ``right``.
      
    ``valign``
      Vertical alignment. 
      Choose between ``top`` (default), ``middle``, ``center``.
    
    ``size``
      Font size in pixels
      
    ``font``
      Font family. Must be a ttf file (``Arial.ttf``)

    **Expansion**: Also we expand macros in the text using ``format()``. 
    The available keywords are:
    
    ``frame``
      number of frames since the beginning
       
    ``time``
      seconds since the beginning of the log

    ``timestamp``
      absolute timestamp
    
    '''

    Block.alias('text')

    Block.config('texts', 'Text specification (see block description).')

    Block.input('rgb', 'Input image.')
    Block.output('rgb', 'Output image with overlaid text.')

    def init(self):
        self.state.first_timestamp = None

    def update(self):

        # TODO: add check
        if self.state.first_timestamp is None:
            self.state.first_timestamp = self.get_input_timestamp(0)
            self.state.frame = 0
        else:
            self.state.frame += 1
        # Add stats
        macros = {}
        macros['timestamp'] = self.get_input_timestamp(0)
        if self.state.first_timestamp == ETERNITY:
            macros['time'] = -1
        else:
            macros['time'] = \
                self.get_input_timestamp(0) - self.state.first_timestamp
        macros['frame'] = self.state.frame

        rgb = self.input.rgb
        im = Image_from_array(rgb)
        from . import ImageDraw
        draw = ImageDraw.Draw(im)

        # {string: "raw image", position: [10,30], halign: left, 
        # color: black, bg: white  }
        if not isinstance(self.config.texts, list):
            raise BadConfig('Expected list', self, 'texts')

        for text in self.config.texts:
            text = text.copy()
            if not 'string' in text:
                raise BadConfig('Missing field "string" in text spec %s.' % 
                                text.__repr__(), self, 'texts')

            try:
                text['string'] = Text.replace(text['string'], macros)
            except KeyError as e:
                msg = str(e) + '\nAvailable: %s.' % macros.keys()
                raise BadConfig(msg, self, 'texts')

            p = text['position']
            
            try:
                p[0] = get_ver_pos_value(p[0], height=rgb.shape[0])
                p[1] = get_hor_pos_value(p[1], width=rgb.shape[1])
            except ValueError as e:
                raise BadConfig(str(e), text.__repr__(), self, 'texts')
            
            process_text(draw, text)

        out = im.convert("RGB")
        pixel_data = numpy.asarray(out)

        self.output.rgb = pixel_data

    @staticmethod
    def replace(s, macros):
        ''' Expand macros in the text. '''
        return s.format(**macros)
 

def get_hor_pos_value(spec, width):
    if isinstance(spec, str):
        if is_fraction(spec):
            return get_fraction(spec, width)
        else:
            valid = ['center', 'left', 'right']
            if not spec in valid:
                msg = 'Strange %r: not in %s' % (spec, valid)
                raise ValueError(msg)
    else:
        assert isinstance(spec, int)

    if spec == 'center':
        return width / 2
    elif spec == 'left': 
        return 0
    elif spec == 'right':
        return width
    else:
        if spec < 0:
            return width + spec
        else:
            return spec

def is_fraction(spec):
    return isinstance(spec, str) and spec[-1] == '%'

def get_fraction(spec, L):
    if not is_fraction(spec):
        raise ValueError(spec)
    f = float(spec[:-1])
    return int(f/100.0*L)
    
def get_ver_pos_value(spec, height):
    # Draws the string at the given position. The position gives the upper left corner of the text.
    if isinstance(spec, str):
        if is_fraction(spec):
            return get_fraction(spec, height)
        else:
            valid = ['middle', 'top', 'bottom']
            if not spec in valid:
                msg = 'Strange %r: not in %s' % (spec, valid)
                raise ValueError(msg)
    else:
        assert isinstance(spec, int)

    if spec == 'middle':
        return height / 2
    elif spec == 'top': 
        return 0
    elif spec == 'bottom':
        return height
    else:
        if spec < 0:
            return height + spec
        else:
            return spec
    


def info(s):
    info_main('procgraph_pil/text: %s' % s)


def error(s):
    error_main('procgraph_pil/text: %s' % s)


# cache of fonts
def find_file(font_name):
    try:
        # pattern = '*%s*.ttf' % font_name
        pattern = font_name
        a = subprocess.Popen(['locate', pattern], stdout=subprocess.PIPE)
        lines = a.stdout.read()
        options = lines.split('\n')
        options = [f for f in options if os.path.exists(f)]
        if len(options) == 0:
            error('Cannot find a file matching the pattern %r.' % pattern)
            return None
        guess = options[0]
        info('Found %d matches for %s, using  "%s".' % 
             (len(options), pattern, guess))
        return guess
    except Exception as e:
        error('Cannot run "locate": %s' % e)
        return None


fonts = {}


def get_font(name, size):
    
    key = (name, size)
    # cached 
    if key in fonts:
        return fonts[key]
    
    options = [name, 'FreeSans', 'Arial']
    
    errors = []
    for o in options:
        try:
            res = get_font_try(o, size)
            fonts[key] = res
            return res
        except KeyError as e:
            errors.append(e)
                    
    msg = 'Could not find any of the fonts %r' % options
    raise ValueError(msg)
    
def get_font_try(name, size):
    from . import ImageFont
    name = name.replace(' ', '')
    filename = name
    if not filename.endswith('.ttf'):
        filename += '.ttf'
    if os.path.exists(filename):
        return ImageFont.truetype(filename, size)
    else:
        found = find_file(filename)
        if found is None:
            msg =  'Could not find %r anywhere.' % filename
            raise KeyError(msg)
        info('Found %r using "locate".' % filename)
        return ImageFont.truetype(found, size)

def process_text(draw, t):
    position = t['position']
    string = t['string']
    color = t.get('color', '#aaaaaa')
    bg = t.get('bg', None)
    size = t.get('size', 15)
    fontname = t.get('font', 'Arial')
    font = get_font(fontname, size)

    tw, th = font.getsize(string)
    y, x = position[0], position[1]  # order is good

    halign = t.get('halign', 'left')
    valign = t.get('valign', 'top')

    if halign == 'left':
        pass
    elif halign == 'right':
        x -= tw
    elif halign == 'center':
        x -= tw / 2
    else:
        print('Unknown horizontal-align key %s' % halign)

    if valign == 'top':
        pass
    elif valign == 'bottom':
        y -= th
    elif valign == 'middle':
        y -= th / 2
    else:
        print('Unknown vertical-align key %s' % valign)

    if bg:
        for a in [[-1, 0], [1, 0], [0, 1], [0, -1], [-1, -1],
                   [-1, +1], [1, 1], [1, -1]]:
            draw.text([x + a[0], y + a[1]], string, fill=bg, font=font)

    draw.text([x, y], string, fill=color, font=font)

@contract(rgb='array[HxWx4]')
def draw_text_on_img(rgb, string, position,
                     color='#aaaaaaff',
                     bg=None,
                     fontsize=None,
                     height=None,
                     width=None,
                     fontname='Arial',
                     line_width='100%',
                     line_scale=1.5,
                     halign='left', 
                     valign='top'):
                     
    im = Image_from_array(rgb)
    from . import ImageDraw
    draw = ImageDraw.Draw(im)

    position[0] = get_ver_pos_value(position[0], height=rgb.shape[0])
    position[1] = get_hor_pos_value(position[1], width=rgb.shape[1])

    print('Using line width %r (shape %r) ' % (line_width ,rgb.shape))
        
    if is_fraction(line_width):
        line_width = get_fraction(line_width, rgb.shape[1])
            
        
    n = sum([fontsize is not None, 
             height is not None, 
             width is not None])
    if n != 1:
        msg = 'Need exactly one of fontsize, height, width (got %d)' % n
        raise ValueError(msg)
        
    if fontsize is not None:
        if is_fraction(fontsize):
            fontsize = get_fraction(fontsize, rgb.shape[0])
        font = get_font(fontname, fontsize)
    else:
        test_scale = 100
        font0 = get_font(fontname, test_scale)
        _, (th0, tw0) = format_paragraph(text=string, font=font0, 
                                            line_width=100000, 
                                            line_scale=line_scale)

        print('size using test_scale =%s -> h %s w %s' % (test_scale, th0, tw0))
            
        if height is not None:
            if is_fraction(height):
                height = get_fraction(height, rgb.shape[0])
            #print('height: %s' % height)
            scale = height * 1.0 / th0

        if width is not None:
            if is_fraction(width):
                width = get_fraction(width, rgb.shape[1])

            #print('width: %s' % width)
            scale = width * 1.0 / tw0
        
        use_size = int(test_scale * scale)
        print('scale: %s' % scale)
        print('use_size: %s' % use_size)
        font = get_font(fontname, use_size)
         
        _, (th1, tw1) = format_paragraph(text=string, font=font, 
                                            line_width=100000, 
                                            line_scale=line_scale)
        print('now: h %s w %s ' % (th1,tw1))
         
    
    #print('font: %s' % str(font))
    tokens, (th, tw) = format_paragraph(text=string, font=font, 
                                        line_width=line_width, 
                                        line_scale=line_scale)
    print('th, tw: %s' % str((th,tw)))
    base = get_basepoint(p0=position, tw=tw, th=th, 
                         halign=halign, valign=valign)
    print('basepoint: %s' % str(base))
    for t in tokens:
        #print(t)
        draw_token(draw=draw, t=t, base=base, bg=bg, font=font, color=color) 

    out = im.convert("RGBA")
    pixel_data = numpy.asarray(out)
    return pixel_data

def draw_token(draw, t, base, bg, font, color):
    
    x = t.position[1] + base[1]
    y = t.position[0] + base[0]
    
    #print('drawing at y=%.2f x=%.2f token %r' % (y,x,t.text))
    string = t.text
    if bg:
        for a in [[-1, 0], [1, 0], [0, 1], [0, -1], [-1, -1],
                   [-1, +1], [1, 1], [1, -1]]:
            draw.text([x + a[0], y + a[1]], string, fill=bg, font=font)

    # w, h = font.getsize(string)
#     draw.rectangle(((0,0),(w,h)), fill="white", outline = "blue")
    #print('token %r -> size h %s w %s ' % (t, h ,w ))
    #draw.text([0, 0], string, fill="#000000", font=font)
    
    draw.text([x, y], string, fill=color, font=font)

def get_basepoint(p0, tw, th, halign, valign):
    y, x = p0
    if halign == 'left':
        pass
    elif halign == 'right':
        x -= tw
    elif halign == 'center':
        x -= tw / 2
    else:
        print('Unknown horizontal-align key %s' % halign)

    if valign == 'top':
        pass
    elif valign == 'bottom':
        y -= th
    elif valign == 'middle':
        y -= th / 2
    else:
        print('Unknown vertical-align key %s' % valign)
    return y, x
