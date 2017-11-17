"""
Tool nbview

Copyright (c) 2017 - Eindhoven University of Technology, The Netherlands

This software is made available under the terms of the MIT License.
"""

from nbtoolbelt.toolbaseapp import Tool
from nbformat import NotebookNode
from pathlib import Path
from argparse import _ArgumentGroup
from typing import List
from nbtoolbelt.arguments import NegatableAction
from nbtoolbelt.processing import ProcessingResultType
from nbtoolbelt.rendering import render_nb
import webbrowser
import os

TOOL = 'view'


class ViewTool(Tool):
    """Show notebooks in the browser, with embedded MathJax and attachments rendered.
    """

    def __init__(self) -> None:
        super().__init__(
            name='nb' + TOOL,
            description='View Jupyter notebooks your browser.',
            action=TOOL
        )
        self._aggregate['written_html'] = []  # list of opened html files

    def process_nb(self, nb: NotebookNode, nb_path: Path) -> ProcessingResultType:
        """View notebook.
        That is, convert it to html, and open it in the default browswer.

        .. note:: **Side-effect**: Creates html file

        :param nb: notebook to show head of
        :param nb_path: notebook's path
        :return: empty
        """
        # determine destination path of html file
        name_insert = '' if self._args.inplace else self._args.view_result_name
        html_path = nb_path.with_name(nb_path.stem + name_insert + '.html')

        # convert to html
        html = render_nb(nb)

        if self._args.write_files:
            # write html to file
            try:
                with html_path.open('w', encoding='utf-8') as fp:
                    fp.write(html)
            except Exception as e:
                ename = type(e).__name__
                print('Writing of "{}" failed ({}): {}.'.format(html_path.name, ename, e), file=sys.stderr)
                if self._args.debug:
                    print('  Tried to write html file:', html_path.resolve(), file=sys.stderr)
                raise

            # register in self._aggregate, for deletion (if so desired)
            if self._args.wait_delete:
                self._aggregate['written_html'].append(html_path)
        else:
            print('No file written')  # TODO is this really necessary?

        # open in browser
        if self._args.browser:
            webbrowser.open('file://' + Path(html_path).resolve().as_posix(), new=2)

        return []  # no notebooks produced

    def process_collected_data(self):
        if self._aggregate['written_html']:
            answer = input('Delete created html files ([y]/n)? ')
            deleting = not answer or answer.lower()[0] == 'y'
            for file in self._aggregate['written_html']:
                if deleting:
                    if not self._args.quiet:
                        print('Deleting:', file)
                    os.remove(file)
                else:
                    if not self._args.quiet:
                        print('Keeping:', file)

    def config_tool_args_parsing(self, group: _ArgumentGroup) -> None:
        group.add_argument('-b', '--browser', action=NegatableAction,
                           help='open html in browser' +
                                ' (default: {})'.format(self._args.browser))
        group.add_argument('-w', '--wait_delete', action=NegatableAction,
                           help='interactively wait for user confirmation to delete html files' +
                                ' (default: {})'.format(self._args.wait_delete))

    def print_tool_args(self) -> None:
        print('  Wait for user to confirm deletion of html: {!r}'.format(self._args.wait_delete))
        print('  Open in web browser: {!r}'.format(self._args.browser))

    def check_and_adjust_arguments(self):
        args = self._args
        if not args.write_files:
            args.browser = False
            args.wait_delete = False


def main(cli_args: List[str]=None):
    return ViewTool().main(cli_args)


if __name__ == "__main__":
    import sys
    sys.exit(main())
