
import os
import json

import jinja2 as jj

from IPython.display import display, Javascript, Markdown

from .util import is_digit


class Autorun:
    """
    """

    here = os.path.dirname(os.path.abspath(__file__))
    dir_template = os.path.join(here, 'templates')
    loader = jj.FileSystemLoader(dir_template)
    env = jj.Environment(loader=loader,
                         variable_start_string='__$',
                         variable_end_string='$__',
                         block_start_string='{%',
                         block_end_string='%}'
                         )

    def __init__(self,
                 cells=None,
                 metadata=False,
                 comment=False,
                 comment_flag='# AUTORUN',
                 verbose=True):
        """
        """
        inputs = [cells, metadata, comment]
        msg = 'Exactly one of cells/metadata/comment must be set'
        assert sum([bool(e) for e in inputs]) == 1, msg

        str_cells = self._cells_to_str(cells)
        self.data = {'str_cells': str_cells,
                     'metadata': metadata,
                     'comment': comment,
                     'comment_flag': comment_flag,
                     }
        self.verbose = verbose

    def add_js(self):
        """
        """
        template = Autorun.env.get_template('main.template.js')
        js = template.render(data=self.data)

        if self.verbose:
            template = Autorun.env.get_template('notice_safe.txt')
            txt = template.render()
            print(txt)

        display(Javascript(js))

        if self.verbose:
            template = Autorun.env.get_template('notice_short.md')
            str_data = json.dumps(self.data)
            md = template.render(str_data=str_data)
            display(Markdown(md))

    @classmethod
    def info(cls):
        """
        """
        template = Autorun.env.get_template('notice_long.md')
        md = template.render()
        display(Markdown(md))

    @staticmethod
    def _cells_to_str(cells):
        """
        """
        if cells is None:
            return None

        if isinstance(cells, list):
            str_cells = ','.join([str(e) for e in cells])
        else:
            str_cells = cells

        s = str_cells
        if ':' in str_cells:
            s = str_cells.split(':', 2)
            assert all([is_digit(e)
                        for e in s]), 'All slice elements must be integers'
            if len(s) == 3:
                assert s[2] != '0', 'Slice step cannot be zero'

        return str_cells
