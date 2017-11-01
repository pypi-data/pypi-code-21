"""Utility file."""
import re
import six
import copy
import platform
import numpy as np
import pandas as pd
from six import iteritems
from lxml import objectify
from pptx.util import Inches
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from lxml.builder import ElementMaker


def is_slide_allowed(change, slide, number):
    '''
    Given a change like one of the below::

        slide-number: 1
        slide-number: [1, 2, 3]
        slide-title: 'company'
        slide-title: ['company', 'industry']

    ... return True if:

    1. ``number`` matches a slide-number
    2. ``slide`` title matches a slide-title regex (case-insensitive)

    If none of these are specified, return True.
    '''
    match = True
    # Restrict to specific slide titles, if specified
    if 'slide-number' in change:
        slide_number = change['slide-number']
        if isinstance(slide_number, (list, dict)):
            match = match and number in slide_number
        elif isinstance(slide_number, six.integer_types):
            match = match and number == slide_number

    # Restrict to specific slide titles, if specified
    if 'slide-title' in change:
        slide_title = change['slide-title']
        try:
            title = slide.shapes.title.text
        except AttributeError:
            title = ''
        if isinstance(slide_title, (list, dict)):
            match = match and any(
                re.search(expr, title, re.IGNORECASE) for expr in slide_title)
        elif isinstance(slide_title, six.string_types):
            match = match and re.search(slide_title, title, re.IGNORECASE)

    return match


def is_group(shape):
    # TODO: implement this
    return shape.element.tag.endswith('}grpSp')


def stack_elements(replica, shape, stack=False):
    '''
    Function to extend elements horizontally or vertically.
    '''
    config = {'vertical': {'axis': 'y', 'attr': 'height'},
              'horizontal': {'axis': 'x', 'attr': 'width'}}
    grp_sp = None
    if stack:
        grp_sp = shape.element
        # Adding a 15% margin between original and new object.
        met_margin = 0.15
        for index in range(replica - 1):
            # Adding a cloned object to shape
            extend_shape = copy.deepcopy(grp_sp)
            # Getting attributes and axis values from config based on stack.
            attr = config.get(stack, {}).get('attr', 0)
            axis = config.get(stack, {}).get('axis', 0)
            # Taking width or height based on stack value and setting a margin.
            metric_val = getattr(shape, attr)
            axis_val = getattr(extend_shape, axis)
            # Setting margin accordingly either vertically or horizontally.
            margin = round(metric_val * met_margin) + axis_val
            set_attr = (metric_val * (index + 1)) + margin
            # Setting graphic position of newly created object to slide.
            setattr(extend_shape, axis, int(set_attr))
            # Adding newly created object tomslide.
            grp_sp.addnext(extend_shape)

    return grp_sp


def pixel_to_inch(pixel):
    """Function to convert Pixel to Inches based on OS."""
    linux_width = 72.0
    windows_width = 96.0
    os_name = platform.system().lower().strip()
    if os_name == 'windows':
        return Inches(pixel / windows_width)
    return Inches(pixel / linux_width)


def scale(series, lo=None, hi=None):
    '''
    Returns the values linearly scaled from 0 - 1.

    The lowest value becomes 0, the highest value becomes 1, and all other
    values are proportionally multiplied and have a range between 0 and 1.

    Parameters
    ----------
    series : Pandas Series, numpy array, list or iterable
        Data to scale
    lo : float
        Value that becomes 0. Values lower than ``lo`` in ``series``
        will be mapped to negative numbers.
    hi : float
        Value that becomes 1. Values higher than ``hi`` in ``series``
        will be mapped to numbers greater than 1.

    Examples
    --------
    Typical usage::

        stats.scale([1, 2, 3, 4, 5])
        # array([ 0.  ,  0.25,  0.5 ,  0.75,  1.  ])

        stats.scale([1, 2, 3, 4, 5], lo=2, hi=4)
        # array([-0.5,  0. ,  0.5,  1. ,  1.5])
    '''
    series = np.array(series, dtype=float)
    lo = np.nanmin(series) if lo is None or np.isnan(lo) else lo
    hi = np.nanmax(series) if hi is None or np.isnan(hi) else hi
    return (series - lo) / ((hi - lo) or np.nan)


def decimals(series):
    '''
    Given a ``series`` of numbers, returns the number of decimals
    *just enough* to differentiate between most numbers.

    Parameters
    ----------
    series : Pandas Series, numpy array, list or iterable
        Data to find the required decimal precision for

    Returns
    -------
    decimals : int
        The minimum number of decimals required to differentiate
        between most numbers

    Examples
    --------
    Typical usage::

        stats.decimals([1, 2, 3])       # 0: All integers. No decimals needed
        stats.decimals([.1, .2, .3])    # 1: 1 decimal is required
        stats.decimals([.01, .02, .3])  # 2: 2 decimals are required
        stats.decimals(.01)             # 2: Only 1 no. of 2 decimal precision

    Notes
    -----
    This function first calculates the smallest difference between any pair of
    numbers (ignoring floating-point errors). It then finds the log10 of that
    difference, which represents the minimum decimals required to
    differentiate between these numbers.
    '''
    series = np.ma.masked_array(series, mask=np.isnan(series)).astype(float)
    series = series.reshape((series.size,))
    diffs = np.diff(series[series.argsort()])
    inf_diff = 1e-10
    min_float = .999999
    diffs = diffs[diffs > inf_diff]
    if len(diffs) > 0:
        smallest = np.nanmin(diffs.filled(np.Inf))
    else:
        nonnan = series.compressed()
        smallest = (abs(nonnan[0]) or 1) if len(nonnan) > 0 else 1
    return int(max(0, np.floor(min_float - np.log10(smallest))))


def conver_color_code(colorcode):
    """Convert color code to valid PPTX color code."""
    colorcode = colorcode.rsplit('#')[-1].lower()
    return colorcode + ('0' * (6 - len(colorcode)))

# Custom Charts Functions below(Sankey, Treemap, Calendarmap).


def apply_text_css(run, paragraph, **kwargs):
    """Apply css."""
    pixcel_to_inch = 10000
    if kwargs.get('color'):
        rows_text = run.font.fill
        rows_text.solid()
        run.font.color.rgb = RGBColor.from_string(conver_color_code(kwargs['color']))
    if kwargs.get('font-family'):
        run.font.name = kwargs['font-family']
    if kwargs.get('font-size'):
        run.font.size = pixcel_to_inch * kwargs['font-size']
    if kwargs.get('text-align'):
        paragraph.alignment = getattr(PP_ALIGN, kwargs['text-align'].upper())
    for prop in {'bold', 'italic', 'underline'}:
        setattr(run.font, prop, kwargs.get(prop))


def make_element():
    """Function to create element structure."""
    nsmap = {
        'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
        'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
        'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
    }
    a = ElementMaker(namespace=nsmap['a'], nsmap=nsmap)
    p = ElementMaker(namespace=nsmap['p'], nsmap=nsmap)
    r = ElementMaker(namespace=nsmap['r'], nsmap=nsmap)
    return {'nsmap': nsmap, 'a': a, 'p': p, 'r': r}


def fill_color(**kwargs):
    """
    Return a new color object.

    You may use any one of the following ways of specifying colour:

        color(schemeClr='accent2')             # = second theme color
        color(prstClr='black')                 # = #000000
        color(hslClr=[14400000, 100.0, 50.0])  # = #000080
        color(sysClr='windowText')             # = window text color
        color(scrgbClr=(50000, 50000, 50000))  # = #808080
        color(srgbClr='aaccff')                # = #aaccff

    One or more of these modifiers may be specified:

    - alpha    : '10%' indicates 10% opacity
    - alphaMod : '10%' increased alpha by 10% (50% becomes 55%)
    - alphaOff : '10%' increases alpha by 10 points (50% becomes 60%)
    - blue     : '10%' sets the blue component to 10%
    - blueMod  : '10%' increases blue by 10% (50% becomes 55%)
    - blueOff  : '10%' increases blue by 10 points (50% becomes 60%)
    - comp     : True for opposite hue on the color wheel (e.g. red -> cyan)
    - gamma    : True for the sRGB gamma shift of the input color
    - gray     : True for the grayscale version of the color
    - green    : '10%' sets the green component to 10%
    - greenMod : '10%' increases green by 10% (50% becomes 55%)
    - greenOff : '10%' increases green by 10 points (50% becomes 60%)
    - hue      : '14400000' sets the hue component to 14400000
    - hueMod   : '600000' increases hue by 600000 (14400000 becomes 20000000)
    - hueOff   : '10%' increases hue by 10 points (50% becomes 60%)
    - inv      : True for the inverse color. R, G, B are all inverted
    - invGamma : True for the inverse sRGB gamma shift of the input color
    - lum      : '10%' sets the luminance component to 10%
    - lumMod   : '10%' increases luminance by 10% (50% becomes 55%)
    - lumOff   : '10%' increases luminance by 10 points (50% becomes 60%)
    - red      : '10%' sets the red component to 10%
    - redMod   : '10%' increases red by 10% (50% becomes 55%)
    - redOff   : '10%' increases red by 10 points (50% becomes 60%)
    - sat      : '100000' sets the saturation component to 100%
    - satMod   : '10%' increases saturation by 10% (50% becomes 55%)
    - satOff   : '10%' increases saturation by 10 points (50% becomes 60%)
    - shade    : '10%' is 10% of input color, 90% black
    - tint     : '10%' is 10% of input color, 90% white

    Refer
    <http://msdn.microsoft.com/en-in/library/documentformat.openxml.drawing(v=office.14).aspx>
    """
    hslclr = kwargs.get('hslclr')
    sysclr = kwargs.get('sysclr')
    srgbclr = kwargs.get('srgbclr')
    prstclr = kwargs.get('prstclr')
    scrgbclr = kwargs.get('scrgbclr')
    schemeclr = kwargs.get('schemeclr')

    ns = xmlns('a')
    srgbclr = srgbclr.rsplit('#')[-1].lower()
    srgbclr = srgbclr + ('0' * (6 - len(srgbclr)))
    if schemeclr:
        s = '<a:schemeClr %s val="%s"/>' % (ns, schemeclr)
    elif srgbclr:
        s = '<a:srgbClr %s val="%s"/>' % (ns, srgbclr)
    elif prstclr:
        s = '<a:prstClr %s val="%s"/>' % (ns, prstclr)
    elif hslclr:
        s = '<a:hslClr %s hue="%.0f" sat="%.2f%%" lum="%.2f%%"/>' % (
            (ns,) + tuple(hslclr))
    elif sysclr:
        s = '<a:sysClr %s val="%s"/>' % (ns, sysclr)
    elif scrgbclr:
        s = '<a:scrgbClr %s r="%.0f" g="%.0f" b="%.0f"/>' % ((ns,) + tuple(
            scrgbclr))
    color = objectify.fromstring(s)
    return color


def xmlns(*prefixes):
    """XML ns."""
    elem_schema = make_element()
    return ' '.join('xmlns:%s="%s"' % (pre, elem_schema['nsmap'][pre]) for pre in prefixes)


def call(val, g, group, default):
    """Callback."""
    if callable(val):
        return val(g)
    return default


def cust_shape(x, y, w, h, _id):
    """Custom shapes."""
    _cstmshape = '<p:sp ' + xmlns('p', 'a') + '>'
    _cstmshape = _cstmshape + """<p:nvSpPr>
            <p:cNvPr id='%s' name='%s'/>
            <p:cNvSpPr/>
            <p:nvPr/>
          </p:nvSpPr>
          <p:spPr>
            <a:xfrm>
              <a:off x='%s' y='%s'/>
              <a:ext cx='%s' cy='%s'/>
            </a:xfrm>
            <a:custGeom>
              <a:avLst/>
              <a:gdLst/>
              <a:ahLst/>
              <a:cxnLst/>
              <a:rect l='0' t='0' r='0' b='0'/>
            </a:custGeom>
          </p:spPr>
        </p:sp>"""
    shp = _cstmshape % (_id, 'Freeform %d' % _id, x, y, w, h)
    return objectify.fromstring(shp)


def draw_sankey(data, spec):
    """Create sankey data logic."""
    x0 = spec['x0']
    size = spec['size']
    group = spec['group']
    width = spec['width']
    default_color = '#ccfccf'
    default_stroke = '#ffffff'
    attrs = spec.get('attrs', {})
    sort = spec.get('sort', False)

    text = spec.get('text')
    order = spec.get('order')
    fill_color = spec.get('color')

    g = data.groupby(group)
    frame = pd.DataFrame({
        'size': g[group[0]].count() if size is None else g[size].sum(),
        'seq': 0 if order is None else order(g),
    })
    frame['width'] = frame['size'] / float(frame['size'].sum()) * width
    frame['fill'] = call(fill_color, g, group, default_color)
    frame['text'] = call(text, g, group, '')
    # Add all attrs to the frame as well
    for key, val in iteritems(attrs):
        frame[key] = call(val, g, group, None)
    if 'stroke' not in attrs:
        frame['stroke'] = default_stroke
    # Compute frame['x'] only after sorting
    if order and sort:
        frame.sort_values('seq', inplace=True)
    frame['x'] = x0 + frame['width'].cumsum() - frame['width']
    return frame


def squarified(x, y, w, h, data):
    """

    Draw a squarified treemap.

    See <http://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.36.6685>
    Returns a numpy array with (x, y, w, h) for each item in data.

    Examples
    --------
    The result is a 2x2 numpy array::

        >>> squarified(x=0, y=0, w=6, h=4, data=[6, 6, 4, 3, 2, 2, 1])
        array([[ 0.        ,  0.        ,  3.        ,  2.        ],
               [ 0.        ,  2.        ,  3.        ,  2.        ],
               [ 3.        ,  0.        ,  1.71428571,  2.33333333],
               [ 4.71428571,  0.        ,  1.28571429,  2.33333333],
               [ 3.        ,  2.33333333,  1.2       ,  1.66666667],
               [ 4.2       ,  2.33333333,  1.2       ,  1.66666667],
               [ 5.4       ,  2.33333333,  0.6       ,  1.66666667]])

        >>> squarified(x=0, y=0, w=1, h=1, data=[np.nan, 0, 1, 2])
        array([[ 0.        ,  0.        ,  0.        ,  0.        ],
               [ 0.        ,  0.        ,  0.        ,  0.        ],
               [ 0.        ,  0.        ,  0.33333333,  1.        ],
               [ 0.33333333,  0.        ,  0.66666667,  1.        ]])
    """
    w, h = float(w), float(h)
    size = np.nan_to_num(np.array(data).astype(float))
    start, end = 0, len(size)
    result = np.zeros([end, 4])
    if w <= 0 or h <= 0:
        return result

    cumsize = np.insert(size.cumsum(), 0, 0)
    while start < end:
        # We lay out out blocks of rects on either the left or the top edge of
        # the remaining rectangle. But how many rects in the block? We take as
        # many as we can as long as the worst aspect ratio of the block's
        # rectangles keeps improving.

        # This section is (and should be) be heavily optimised. Each operation
        # is run on every element in data.
        last_aspect, newstart = np.Inf, start + 1
        startsize = cumsize[start]
        blockmin = blockmax = size[newstart - 1]
        blocksum = cumsize[newstart] - startsize
        datasum = cumsize[end] - startsize
        ratio = datasum * (h / w if w > h else w / h)
        while True:
            f = blocksum * blocksum / ratio
            aspect = blockmax / f if blockmax > f else f / blockmax
            aspect2 = blockmin / f if blockmin > f else f / blockmin
            if aspect2 > aspect:
                aspect = aspect2
            if aspect <= last_aspect:
                if newstart < end:
                    last_aspect = aspect
                    newstart += 1
                    val = size[newstart - 1]
                    if val < blockmin:
                        blockmin = val
                    if val > blockmax:
                        blockmax = val
                    blocksum += val
                else:
                    break
            else:
                if newstart > start + 1:
                    newstart = newstart - 1
                break

        # Now, lay out the block = start:newstart on the left or top edge.
        block = slice(start, newstart)
        blocksum = cumsize[newstart] - startsize
        scale = blocksum / datasum
        blockcumsize = cumsize[block] - startsize

        if w > h:
            # Layout left-edge, downwards
            r = h / blocksum
            result[block, 0] = x
            result[block, 1] = y + r * blockcumsize
            result[block, 2] = dx = w * scale
            result[block, 3] = r * size[block]
            x, w = x + dx, w - dx
        else:
            # Layout top-edge, rightwards
            r = w / blocksum
            result[block, 0] = x + r * blockcumsize
            result[block, 1] = y
            result[block, 2] = r * size[block]
            result[block, 3] = dy = h * scale
            y, h = y + dy, h - dy

        start = newstart

    return np.nan_to_num(result)


class SubTreemap(object):
    """
    Yield a hierarchical treemap at multiple levels.

    Usage:
        SubTreemap(
            data=data,
            keys=['Parent', 'Child'],
            values={'Value':sum},
            size=lambda x: x['Value'],
            sort=None,
            padding=0,
            aspect=1)

    yields:
        x, y, w, h, (level, data)
    """

    def __init__(self, **args):
        """Default Constructor."""
        self.args = args

    def draw(self, width, height, x=0, y=0, filter={}, level=0):
        """Function to draw rectanfles."""
        # We recursively into each column in `keys` and stop there
        if level >= len(self.args['keys']):
            return

        # Start with the base dataset. Filter by each key applied so far
        summary = self.args['data']
        for key in filter:
            summary = summary[summary[key] == filter[key]]

        # Aggregate by the key up to the current level
        summary = summary.groupby(
            self.args['keys'][:level + 1]
        ).agg(self.args.get('values', {}))
        for key in self.args['keys'][:level + 1]:
            if hasattr(summary, 'reset_index'):
                # Just pop the key out. .reset_index(key) should do this.
                # But on Pandas 0.20.1, this fails
                summary = summary.reset_index([summary.index.names.index(key)])
            else:
                summary[key] = summary.index

        # If specified, sort the aggregated data
        if 'sort' in self.args and callable(self.args['sort']):
            summary = self.args['sort'](summary)

        pad = self.args.get('padding', 0)
        aspect = self.args.get('aspect', 1)

        # Find the positions of each box at this level
        key = self.args['keys'][level]
        rows = (summary.to_records() if hasattr(summary, 'to_records') else
                summary)

        rects = squarified(x, y * aspect, width, height * aspect, self.args['size'](rows))
        for i2, (x2, y2, w2, h2) in enumerate(rects):
            v2 = rows[i2]
            y2, h2 = y2 / aspect, h2 / aspect
            # Ignore invalid boxes generated by Squarified
            if (
                np.isnan([x2, y2, w2, h2]).any() or
                np.isinf([x2, y2, w2, h2]).any() or
                w2 < 0 or h2 < 0
            ):
                continue

            # For each box, dive into the next level
            filter2 = dict(filter)
            filter2.update({key: v2[key]})
            for output in self.draw(w2 - 2 * pad, h2 - 2 * pad, x=x2 + pad, y=y2 + pad,
                                    filter=filter2, level=level + 1):
                yield output

            # Once we've finished yielding smaller boxes, yield the parent box
            yield x2, y2, w2, h2, (level, v2)


class TableProperties():
    """Get/Set Table's properties."""

    def extend_table(self, shape, data, total_rows, total_columns):
        """Function to extend table rows and columns if required."""
        avail_rows = len(shape.table.rows)
        avail_cols = len(shape.table.columns)

        col_width = shape.table.columns[0].width
        row_height = shape.table.rows[0].height
        # Extending Table Rows if required based on the data
        while avail_rows < total_rows:
            shape.table.rows._tbl.add_tr(row_height)
            avail_rows += 1
        # Extending Table Columns if required based on the data
        while avail_cols < total_columns:
            shape.table._tbl.tblGrid.add_gridCol(col_width)
            avail_cols += 1

    def get_default_css(self, shape):
        """Function to get Table style for rows and columns."""
        pixel_inch = 10000
        tbl_style = {}
        mapping = {0: 'header', 1: 'row'}
        for row_num in range(len(list(shape.table.rows)[:2])):
            style = {}
            txt = shape.table.rows[row_num].cells[0].text_frame.paragraphs[0]

            if txt.alignment:
                style['text-align'] = '{}'.format(txt.alignment).split()[0]

            if not hasattr(txt, 'runs'):
                txt.add_run()
            if txt.runs:
                txt = txt.runs[0].font
                style['bold'] = txt.bold
                style['italic'] = txt.italic
                style['font-size'] = (txt.size / pixel_inch) if txt.size else txt.size
                style['font-family'] = txt.name
                style['underline'] = txt.underline
            tbl_style[mapping[row_num]] = style

        if 'row' not in tbl_style or not len(tbl_style['row']):
            tbl_style['row'] = copy.deepcopy(tbl_style['header'])

        if 'font-size' not in tbl_style['row']:
            tbl_style['row']['font-size'] = tbl_style['header'].get('font-size', None)

        return tbl_style

    def get_css(self, info, column_list, data):
        """Get Table CSS from config."""
        columns = info.get('columns', {})
        table_css = {}
        for col in column_list:
            common_css = copy.deepcopy(info.get('style', {}))
            common_css.update(columns.get(col, {}))
            if 'gradient' in common_css:
                common_css['min'] = common_css.get('min', data[col].min())
                common_css['max'] = common_css.get('min', data[col].max())
            table_css[col] = common_css
        return table_css

    def apply_table_css(self, cell, paragraph, run, info):
        """Apply Table style."""
        if info.get('fill'):
            cell_fill = cell.fill
            cell_fill.solid()
            cell_fill.fore_color.rgb = RGBColor.from_string(conver_color_code(info['fill']))
        apply_text_css(run, paragraph, **info)
