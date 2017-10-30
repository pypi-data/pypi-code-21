"""Allows creation and manipulation of python objects representing html, css and javascript elements.

Available predefined objects for html elements:
    <html>, <head>, <body>, <title>, <meta>, <link>,
    <p>, <h1> to <h6>, <a>, <div>, <script>, <img>,
    <ul>, <ol>, <li>, <table>, <tr>, <th>, <td>, <hr>,
    <style>

Available predefined objects for css elements:
    element selector, id selector, class selector

Available predefined objects for javascript elements:


Todo:
    * Add js element support
    * Expand list of predefined html elements
    * Add a way to parse dicts
    * See A.__str__()  -  line 189
"""


import webgen.filegen as fg


class List:
    """Class that imitates some behaviours of python lists."""

    def __init__(self, *args):
        self.contents = list(args)

    def __getitem__(self, item):
        return self.contents[item]

    def __setitem__(self, key, value):
        self.contents[key] = value

    def __delitem__(self, key):
        del(self.contents[key])

    def __len__(self):
        return len(self.contents)

    def __call__(self, *args):
        for arg in args:
            self.contents.append(arg)


class Dict:
    """Class that imitates some behaviours of python dictionaries."""

    def __init__(self, **kwargs):
        self.contents = kwargs

    def __getitem__(self, item):
        return self.contents[item]

    def __setitem__(self, key, value):
        self.contents[key] = value

    def __delitem__(self, key):
        del (self.contents[key])

    def __len__(self):
        return len(self.contents)

    def __call__(self, **kwargs):
        self.contents = {**self.contents, **kwargs}


# HTML related code


class ElementHTML(List):
    """Class that handles html elements."""

    def __init__(self, tag, *args, end_tag=True, **kwargs):
        super().__init__(*args)
        self.tag = tag
        self.newlines = True
        self.end_tag = end_tag
        self._attributes = kwargs

    def attributes(self, **kwargs):
        self._attributes = kwargs

    def __str__(self, holder_filepath=''):
        """Return html valid representation of self.

        holder_filepath is propagated through the chain of elements
            and only those that need it use it
        """
        text_inline, text_attributes, nl = '', '', ''

        if self.newlines:
            nl = '\n'

        if len(self.contents) != 0:
            for element in self.contents:
                if isinstance(element, str):
                    text_inline += element
                else:
                    text_inline += nl + element.__str__(holder_filepath=holder_filepath) + nl

        text_inline.replace('\n\n', '\n')

        if len(self._attributes) != 0:
            text_attributes = ' '
            for key in self._attributes.keys():
                text_attributes += f'{key}=\"{self._attributes[key]}\"'

        if self.end_tag:
            return f'<{self.tag}{text_attributes}>{text_inline}</{self.tag}>'
        else:
            return f'<{self.tag}{text_attributes} />'


def custom_tag(tagtxt):
    """Allows to create a custom wrapper class of ElementHTML."""

    class CustomTag(ElementHTML):
        def __init__(self, *args, **kwargs):
            super().__init__(tagtxt, *args, **kwargs)
    return CustomTag


class HTML(ElementHTML):
    """Wrapper class of ElementHTML for creating html element."""

    def __init__(self, *args, **kwargs):
        super().__init__('html', *args, **kwargs)


class Head(ElementHTML):
    """Wrapper class of ElementHTML for creating head html element."""

    def __init__(self, *args, **kwargs):
        super().__init__('head', *args, **kwargs)


class Body(ElementHTML):
    """Wrapper class of ElementHTML for creating body html element."""

    def __init__(self, *args, **kwargs):
        super().__init__('body', *args, **kwargs)


class Title(ElementHTML):
    """Wrapper class of ElementHTML for creating title html element."""

    def __init__(self, *args, **kwargs):
        super().__init__('title', *args, **kwargs)


class Meta(ElementHTML):
    """Wrapper class of ElementHTML for creating meta html element."""

    def __init__(self, *args, **kwargs):
        super().__init__('meta', *args, **kwargs)


class Link(ElementHTML):
    """Wrapper class of ElementHTML for creating link html element."""

    def __init__(self, *args, **kwargs):
        super().__init__('link', *args, end_tag=False, **kwargs)


class P(ElementHTML):
    """Wrapper class of ElementHTML for creating paragraph html element."""

    def __init__(self, *args, **kwargs):
        super().__init__('p', *args, **kwargs)


class H(ElementHTML):
    """Wrapper class of ElementHTML for creating header html element."""

    def __init__(self, *args, size=1, **kwargs):
        super().__init__(f'h{size}', *args, **kwargs)


class A(ElementHTML):
    """Wrapper class of ElementHTML for creating anchor html element."""

    def __init__(self, *args, **kwargs):
        super().__init__('a', *args, **kwargs)
        self.oldstr = ElementHTML.__str__

    def __str__(self, holder_filepath=''):  # holder_filepath is passed in `filegen.py`
        if 'href' in self._attributes.keys() and \
            isinstance(self._attributes['href'], fg.HTML):
                if holder_filepath == '':
                    raise ValueError('')  # Add description to ValueError
                new_href = self._compare_relative_path(holder_filepath, self._attributes['href'].filepath())
                self._attributes['href'] = new_href

        return self.oldstr(self)

    @staticmethod
    def _compare_relative_path(path_main, path_other):
        """Returns path from path_main to path_other.

        Example:
            path_main = 'some_folder\\file1.html'
            path_other = 'some_folder\\sub_folder\\file2.html'

            returns 'sub_folder\\file2.html'
        """
        if '\\' in path_main:
            main_p = path_main.split('\\')
        else:
            main_p = [path_main]

        if '\\' in path_other:
            other_p = path_other.split('\\')
        else:
            other_p = [path_other]

        min_path_len = min([len(main_p), len(other_p)])

        path_overlap = 0
        for i in range(min_path_len):
            if main_p[i] == other_p[i] and path_overlap == i:
                path_overlap += 1

        return '..\\' * (len(main_p)-1 - path_overlap) \
               + '\\'.join(other_p[path_overlap:])


class Div(ElementHTML):
    """Wrapper class of ElementHTML for creating division html element."""

    def __init__(self, *args, **kwargs):
        super().__init__('div', *args, **kwargs)


class Script(ElementHTML):
    """Wrapper class of ElementHTML for creating script html element."""

    def __init__(self, *args, **kwargs):
        super().__init__('script', *args, **kwargs)


class Img(ElementHTML):
    """Wrapper class of ElementHTML for creating image html element."""

    def __init__(self, *args, **kwargs):
        super().__init__('img', *args, **kwargs)


class Ul(ElementHTML):
    """Wrapper class of ElementHTML for creating unordered list html element."""

    def __init__(self, *args, **kwargs):
        super().__init__('ul', *args, **kwargs)

    @classmethod
    def from_list(cls, list_, _no_ul_tag=False):
        """Converts a python list into `Ul` object."""

        if _no_ul_tag:
            # Returns a python list containing `Li` class objects
            items = []

            for item in list_:
                if isinstance(item, list):
                    items.append(cls.from_list(item))
                elif isinstance(item, dict):
                    items.append(*cls.from_dict(item, _part_of_list=True))
                else:
                    items.append(Li(item))
            return items
        else:
            # Returns a `Ul` class object
            temp_ul = cls()

            for item in list_:
                if isinstance(item, list):
                    temp_ul(cls.from_list(item))
                elif isinstance(item, dict):
                    temp_ul(*cls.from_dict(item, _part_of_list=True))
                else:
                    temp_ul(Li(item))
            return temp_ul

    @classmethod
    def from_dict(cls, dict_, _part_of_list=False):
        keys = list(dict_.keys())
        keys.sort()

        items = []
        for key in keys:
            items.append(key)
            if isinstance(dict_[key], list):
                items.append(dict_[key])
            else:
                items.append([dict_[key]])

        return cls.from_list(items, _no_ul_tag=_part_of_list)


class Ol(ElementHTML):
    """Wrapper class of ElementHTML for creating ordered list html element."""

    def __init__(self, *args, **kwargs):
        super().__init__('ol', *args, **kwargs)

    @classmethod
    def from_list(cls, list_, _no_ul_tag=False):
        """Converts a python list into `Ul` object."""

        if _no_ul_tag:
            # Returns a python list containing `Li` class objects
            items = []

            for item in list_:
                if isinstance(item, list):
                    items.append(cls.from_list(item))
                elif isinstance(item, dict):
                    items.append(*cls.from_dict(item, _part_of_list=True))
                else:
                    items.append(Li(item))
            return items
        else:
            # Returns a `Ul` class object
            temp_ul = cls()

            for item in list_:
                if isinstance(item, list):
                    temp_ul(cls.from_list(item))
                elif isinstance(item, dict):
                    temp_ul(*cls.from_dict(item, _part_of_list=True))
                else:
                    temp_ul(Li(item))
            return temp_ul

    @classmethod
    def from_dict(cls, dict_, _part_of_list=False):
        keys = list(dict_.keys())
        keys.sort()

        items = []
        for key in keys:
            items.append(key)
            if isinstance(dict_[key], list):
                items.append(dict_[key])
            else:
                items.append([dict_[key]])

        return cls.from_list(items, _no_ul_tag=_part_of_list)


class Li(ElementHTML):
    """Wrapper class of ElementHTML for creating list item html element."""

    def __init__(self, *args, **kwargs):
        super().__init__('li', *args, **kwargs)
        self.newlines = False


class Table(ElementHTML):
    """Wrapper class of ElementHTML for creating table html element."""

    def __init__(self, *args, **kwargs):
        super().__init__('table', *args, **kwargs)

    @classmethod
    def from_list(cls, list_):
        """Converts a python list into `Table` object."""
        if isinstance(list_[0], list):
            cols = len(list_[0])
        else:
            raise ValueError('Insert only nested lists.')

        for row in list_:
            if isinstance(row, list):
                if not len(row) == cols:
                    raise ValueError('All rows in the table must be of same length.')
            else:
                row = [row]
                row.extend([''] * (cols - 1))

        temp_table = cls()

        header_row = Tr()
        temp_table(header_row)
        for header in list_[0]:
            header_row(Th(header))

        for row in list_[1:]:
            temp_row = Tr()
            temp_table(temp_row)
            for cell in row:
                temp_row(Td(cell))

        return temp_table


class Tr(ElementHTML):
    """Wrapper class of ElementHTML for creating table row html element."""

    def __init__(self, *args, **kwargs):
        super().__init__('tr', *args, **kwargs)
        self.newlines = False


class Th(ElementHTML):
    """Wrapper class of ElementHTML for creating table header html element."""

    def __init__(self, *args, **kwargs):
        super().__init__('th', *args, **kwargs)
        self.newlines = False


class Td(ElementHTML):
    """Wrapper class of ElementHTML for creating table cell html element."""

    def __init__(self, *args, **kwargs):
        super().__init__('td', *args, **kwargs)
        self.newlines = False


class Hr(ElementHTML):
    """Wrapper class of ElementHTML for creating thematic break html element."""

    def __init__(self, *args, **kwargs):
        super().__init__('hr', *args, **kwargs)


class Style(ElementHTML):
    """Wrapper class of ElementHTML for creating style html element."""

    def __init__(self, *args, **kwargs):
        super().__init__('style', *args, **kwargs)


# - - - - -


# CSS related code


def custom_attr_setter(attr_text):
    """Return a wrapper function that sets self[attr_text] to passed value.

    This function is used to create custom wrapper methods in Declarations class.
    """

    def attr_setter(self, value: str):
        self[attr_text] = value
    return attr_setter


class _CSSDeclarations:
    """Class that contains custom wrapper methods for adding pre-defined declarations to ElementCSS instances."""

    color = custom_attr_setter('color')
    direction = custom_attr_setter('direction')
    spacing_letter = custom_attr_setter('letter-spacing')
    spacing_word = custom_attr_setter('word-spacing')
    line_height = custom_attr_setter('line-height')
    align_txt = custom_attr_setter('text-align')
    align_vertical = custom_attr_setter('vertical-align')
    txt_deco = custom_attr_setter('text-decoration')
    txt_indent = custom_attr_setter('text-indent')
    txt_shadow = custom_attr_setter('text-shadow')
    txt_transform = custom_attr_setter('text-transform')
    txt_overflow = custom_attr_setter('text-overflow')
    unicode = custom_attr_setter('unicode-bidi')
    white_space = custom_attr_setter('white-space')
    font = custom_attr_setter('font')
    font_family = custom_attr_setter('font-family')
    font_size = custom_attr_setter('font-size')
    font_style = custom_attr_setter('font-style')
    font_variant = custom_attr_setter('font-variant')
    font_weight = custom_attr_setter('font-weight')
    bg = custom_attr_setter('background')
    bg_color = custom_attr_setter('background-color')
    bg_img = custom_attr_setter('background-image')
    bg_repeat = custom_attr_setter('background-repeat')
    bg_attachment = custom_attr_setter('background-attachment')
    bg_pos = custom_attr_setter('background-position')
    border = custom_attr_setter('border')
    border_b = custom_attr_setter('border-bottom')
    border_l = custom_attr_setter('border-left')
    border_r = custom_attr_setter('border-right')
    border_t = custom_attr_setter('border-top')
    border_color = custom_attr_setter('border-color')
    border_radius = custom_attr_setter('border-radius')
    border_style = custom_attr_setter('border-style')
    border_width = custom_attr_setter('border-width')
    border_collapse = custom_attr_setter('border-collapse')
    border_spacing = custom_attr_setter('border-spacing')
    caption_side = custom_attr_setter('caption-side')
    empty_cells = custom_attr_setter('empty-cells')
    table_layout = custom_attr_setter('table-layout')
    margin = custom_attr_setter('margin')
    margin_b = custom_attr_setter('margin-bottom')
    margin_l = custom_attr_setter('margin-left')
    margin_t = custom_attr_setter('margin-top')
    margin_r = custom_attr_setter('margin-right')
    padding = custom_attr_setter('padding')
    padding_b = custom_attr_setter('padding-bottom')
    padding_l = custom_attr_setter('padding-left')
    padding_t = custom_attr_setter('padding-top')
    padding_r = custom_attr_setter('padding-right')
    height = custom_attr_setter('height')
    height_max = custom_attr_setter('max-height')
    height_min = custom_attr_setter('min-height')
    width = custom_attr_setter('width')
    width_max = custom_attr_setter('max-width')
    width_min = custom_attr_setter('min-width')
    outline = custom_attr_setter('outline')
    outline_color = custom_attr_setter('outline-outline_color')
    outline_off = custom_attr_setter('outline-offset')
    outline_style = custom_attr_setter('outline-style')
    outline_width = custom_attr_setter('outline-width')
    list = custom_attr_setter('list-style')
    list_img = custom_attr_setter('list-style-image')
    list_pos = custom_attr_setter('list-style-position')
    list_type = custom_attr_setter('list-style-type')
    display = custom_attr_setter('display')
    visible = custom_attr_setter('visibility')
    pos = custom_attr_setter('position')
    bottom = custom_attr_setter('bottom')
    left = custom_attr_setter('left')
    top = custom_attr_setter('top')
    right = custom_attr_setter('right')
    clip = custom_attr_setter('clip')
    z_ind = custom_attr_setter('z-index')
    overflow = custom_attr_setter('overflow')
    overflowX = custom_attr_setter('overflow-x')
    overflowY = custom_attr_setter('overflow-y')
    clear = custom_attr_setter('clear')
    float = custom_attr_setter('float')


class ElementCSS(Dict, _CSSDeclarations):
    """Class that handles css elements."""

    def __init__(self, selector, **kwargs):
        Dict.__init__(self, **kwargs)
        _CSSDeclarations.__init__(self)
        self.selector = selector

    def __str__(self):
        declarations_text = ''

        if len(self.contents) != 0:
            for key in self.contents.keys():
                declarations_text += f'\t{key}: {self.contents[key]};\n'

        return f'{self.selector} {"{"}\n' \
               f'{declarations_text}' \
               f'{"}"}'


class SelectorElement(ElementCSS):
    """Wrapper class of ElementCSS for creating css element selectors."""

    def __init__(self, selector, **kwargs):
        super().__init__(selector, **kwargs)


class SelectorId(ElementCSS):
    """Wrapper class of ElementCSS for creating css id selectors."""

    def __init__(self, selector, **kwargs):
        super().__init__(f'#{selector}', **kwargs)


class SelectorClass(ElementCSS):
    """Wrapper class of ElementCSS for creating css class selectors."""

    def __init__(self, selector, **kwargs):
        super().__init__(f'.{selector}', **kwargs)


# - - - - -


# Javascript related code


class ElementJS(List):
    """Class that handles javascript elements."""

    def __init__(self, *args):
        super().__init__(*args)


# - - - - -
