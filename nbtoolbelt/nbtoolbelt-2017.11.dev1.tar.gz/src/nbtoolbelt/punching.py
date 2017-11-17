"""
Functions for punching

Copyright (c) 2017 - Eindhoven University of Technology, The Netherlands

This software is made available under the terms of the MIT License.
"""

from nbformat import NotebookNode
from typing import Any, Tuple, List, Dict, Set
from argparse import Namespace
from collections import defaultdict
import re
import copy
from .notebook_io import cell_lines

TEST = False


def punch_via_tags(nb: NotebookNode, args: NotebookNode) -> Tuple[Dict[str, int], NotebookNode, NotebookNode]:
    """Punch notebook via tags approach.

    .. note:: **Modifies**: nb

    :param nb: notebook to punch
    :param args: options
    :return: punch counts, punched notebook, chads notebook
    """
    # initialize punch counts
    freq = defaultdict(int)

    # create new notebook for the chads (content of cleared cells)
    nb_chads = copy.deepcopy(nb)
    nb_chads.cells = []

    # traverse all cells, and clear source if it has a tag in the trigger set
    # first, add to-be-cleared cell to chads notebook
    for cell in nb.cells:
        ct = cell.cell_type
        freq[ct] += 1
        if 'tags' in cell.metadata:
            if set(cell.metadata.tags).intersection(set(args.tags)):  # trigger tag present
                nb_chads.cells.append(copy.deepcopy(cell))
                cell.source = args.filling[ct] if args.fill else []
                if 'outputs' in cell:
                    cell.outputs = []
                if 'execution_count' in cell:
                    cell.execution_count = None
                freq[ct + ' holes'] += 1

    return dict(freq), nb, nb_chads


class PunchBaseProcessor:
    """Base class for ``punch`` processors,
    using the Template Method pattern.

    Template methods:

    * ``punch_nb()``: main entry point; calls ``punch_line()`` and hook methods
      * ``pre_cell()``,
      * ``post_cell()``, and
      * ``post_nb()``

    * ``punch_line()``: calls hook methods
      * ``punch_begin_marker_line()``,
      * ``punch_end_marker_line()``,
      * ``punch_inside_line()``, and
      * ``punch_outside_line()``

    Concrete processors override the following hook methods:

    * ``__init__()`` to initialize; must call ``super()`` at begin
    * ``pre_cell()``
    * ``punch_begin_marker_line()``
    * ``punch_end_marker_line()``
    * ``punch_inside_line()``
    * ``punch_outside_line()``
    * ``post_cell()``
    * ``post_nb()``

    A concrete class is typically used to instantiate and process a notebook in one go:

    * ``ConcretePunchProcessor(args, nb).punch_nb()``
    """
    # TODO consider whether nb should be param of punch_nb(); this will require pre_nb() hook
    # TODO consider whether punch_nb() should be named __call__()

    def __init__(self, nb: NotebookNode, args: Namespace):
        """Initialize punch processor for given notebook and options.

        Some PunchProcessors may modify args, e.g. add ``punched_chads``.

        :param nb: notebook to punch
        :param args: options
        """
        self.args = args
        self.nb = nb

        # initialize punch counts
        self.freq = defaultdict(int)

        # initialize parsing state
        self.inside = False  # whether inside a hole
        self.label = None  # label of hole, when inside a hole
        self.labels = set()  # type: Set[str]  # labels encountered so far
        self.duplicate_labels = set()  # type: Set[str]

        # initialize marker line parsing results
        self.m_transition = None
        self.m_label = None
        self.m_description = None

    def pre_cell(self, cell: NotebookNode) -> None:
        pass

    def punch_begin_marker_line(self, cell: NotebookNode, line: str) -> None:
        """Process begin marker line."""
        pass

    def punch_end_marker_line(self, cell: NotebookNode, line: str) -> None:
        """Process end marker line."""
        pass

    def punch_inside_line(self, cell: NotebookNode, line: str) -> None:
        """Process line inside hole."""
        pass

    def punch_outside_line(self, cell: NotebookNode, line: str) -> None:
        """Process line outside hole."""
        pass

    def is_marker_line(self, line: str, cell_type: str) -> bool:
        """Determine whether given line is a marker line for given cell type.

        :param line: line to analyze
        :param cell_type: type of cell containing line
        :return: whether line is a marker line
        """
        return bool(re.search(self.args.marker_regex[cell_type], line))

    def parse_marker_line(self, line, cell_type) -> None:
        """Parse given marker line for given cell type.
        Set instance variables with m_transition, m_label, and m_description.
        Sets ``self.m_transition`` to ``None`` if parsing failed.

        .. note:: **Modifies**: ``self.m_transition, self.m_label, self.m_description``

        :param line: marker line
        :param cell_type: type of cell containing marker line
        """
        # TODO maybe have separate begin/end regex?
        m = re.search(self.args.marker_line_parsing_regex[cell_type], line)
        # the ``m`` stands for 'match object'
        if m:
            self.m_transition = m.group('transition')
            self.m_label = m.group('label')
            self.m_description = m.group('description')
        else:
            self.m_transition = None
            self.m_label = None
            self.m_description = None
        if TEST:
            print('transition: {}, label: {}, description: {}'
                  .format(self.m_transition, self.m_label, self.m_description))

    def punch_line(self, cell, cell_index, line, line_index) -> None:
        """Punch line.
        """
        # if line is a marker line, process it and update state
        # processing it, yields whether it is BEGIN or END, its label, and description
        # label is needed when filling from source
        if TEST:
            print(' {:>3}| {}'.format(line_index + 1, line))
        if self.is_marker_line(line, cell.cell_type):  # marker line
            # parse marker line
            self.parse_marker_line(line, cell.cell_type)

            # check marker line validity
            if not self.m_transition:  # parse failed
                raise AssertionError('Invalid marker line in cell {} on line {}.\n  {}'
                                     .format(cell_index, line_index + 1, line))
            expected_transitions = sorted(self.args.marker_transitions.values())
            if self.m_transition not in expected_transitions:
                raise AssertionError('Invalid transition in marker line of cell {} on line {}.\n'
                                     '  {}\n  Expected {}, but found {}.'
                                     .format(cell_index, line_index + 1, line, expected_transitions, self.m_transition))
            expected_transition = self.args.marker_transitions['end' if self.inside else 'begin']
            if self.m_transition != expected_transition:
                raise AssertionError('Unexpected transition in marker line of cell {} on line {}.\n'
                                     '  {}\n  Expected {}, but found {}.'
                                     .format(cell_index, line_index + 1, line, expected_transition, self.m_transition))

            # update state
            self.inside = not self.inside

            if self.inside:  # begin of hole
                self.freq['holes'] += 1
                self.label = self.m_label

                # check uniqueness of label
                if self.label in self.labels:
                    # label already appeared earlier
                    # TODO depending on purpose of hole collection: ignore, warn, error, or abort
                    # TODO maybe put this in a hook method?
                    # TODO maybe use warnings module?
                    if self.args.debug:
                        print('Duplicate label in cell {} on line {}:\n  {}'
                              .format(cell_index, line_index + 1, line))
                    self.duplicate_labels.add(self.label)

                self.labels.add(self.label)

                self.punch_begin_marker_line(cell, line)  # hook method

            else:  # end of hole
                if self.m_label != self.label:
                    raise AssertionError('Unexpected label in end marker line of cell {} on line {}:\n'
                                         '  Expected [{}], but found [{}]'
                                         .format(cell_index, line_index + 1, self.label, self.m_label))

                self.punch_end_marker_line(cell, line)  # hook method

            if not self.inside:
                self.label = None

        else:  # not marker line, then it depends on the side
            if self.inside:
                self.punch_inside_line(cell, line)  # hook method
            else:
                self.punch_outside_line(cell, line)  # hook method

    def post_cell(self, cell: NotebookNode) -> None:
        pass

    def post_nb(self) -> Any:
        pass

    def punch_nb(self) -> Any:
        """Template method; main entry point.
        """
        # __init__() took care of initialization

        # traverse cells of notebook
        for cell_index, cell in enumerate(self.nb.cells):
            if TEST:
                ct = cell.cell_type
                print('===== cell {}: {} ====='.format(cell_index, ct))
                print('marker regex: {}'.format(self.args.marker_regex[ct]))

            self.pre_cell(cell)  # hook method

            # process all lines in cell.source
            for line_index, line in enumerate(cell_lines(cell)):
                self.punch_line(cell, cell_index, line, line_index)

            self.post_cell(cell)  # hook method

        # check for missing end marker
        if self.inside:
            raise AssertionError('Last hole labeled [{}] has no end marker line.'
                                 .format(self.label))

        if self.duplicate_labels:
            if self.args.verbose:
                print('Labels with duplicates: {}'.format(sorted(self.duplicate_labels)))
            self.freq['labels with duplicates'] = len(self.duplicate_labels)

        return self.post_nb()  # hook method


class PunchedNotebookProcessor(PunchBaseProcessor):
    """Create punched notebook."""

    def __init__(self, nb: NotebookNode, args: Namespace):
        super().__init__(nb, args)
        # initialize result notebook
        self.nb_punched = copy.deepcopy(nb)
        self.nb_punched.cells = []  # to be appended to

        self.source_chad = []  # type: List[NotebookNode]  # chad being inserted to fill current hole
        self.cell_punched = None  # type: NotebookNode  # next punched cell being collected

    def pre_cell(self, cell: NotebookNode):
        # create corresponding cell for punched notebook
        # we preserve everything, except possibly the source lines (this could result in empty cells)
        self.cell_punched = copy.deepcopy(cell)
        self.cell_punched.source = []  # type: List[str]  # to be converted to single string in post_cell()

    def punch_begin_marker_line(self, cell: NotebookNode, line: str):
        # copy marker line to result notebook, if desired
        if self.args.keep_marker_lines:
            self.cell_punched.source.append(line)

        # take care of filling, if desired
        if self.args.fill:
            # inject filling
            if self.args.punch_source:
                # use chads from source notebook, available in self.args.source_chads
                if self.label in self.args.source_chads:  # corresponding source chad is present
                    # copy the source chad,
                    self.source_chad = self.args.source_chads[self.label][:]  # copy  TODO deep?
                    # it will be injected possibly in multiple (up to three) steps
                    # (1) here, (2) in post_cell(), (3) in punch_end_marker_line()
                    if self.source_chad[0].cell_type == cell.cell_type:
                        # if equal begin cell types, then insert source from first cell here
                        # handle first cell of source chad here (N.B. source chad has first cell)
                        if TEST:
                            print('Copying from begin chad cell to begin hole cell: {}'
                                  .format(repr(self.source_chad[0].source)))
                        self.cell_punched.source.append(self.source_chad[0].source)
                        del self.source_chad[0]  # remove parts of source chad that have been handled
                    else:  # begin cell types differ
                        # insert below this cell (handled in post_cell() and/or punch_end_marker_line())
                        pass
                else:  # corresponding source chad is not present
                    # warn that replacement is not present
                    # TODO find better way of warning
                    if self.args.debug:
                        print('No source chad for label "{}" (not filling this hole).'
                              .format(self.label))
                    self.source_chad = []
                    self.freq['unfilled holes'] += 1

            else:
                # use fixed content, substituting label and description (only useful with source option)
                kwargs = {'label': self.m_label, 'description': self.m_description}
                self.cell_punched.source.append(self.args.filling[cell.cell_type].format(**kwargs))

    def punch_end_marker_line(self, cell: NotebookNode, line: str):
        # check if source chad still has material; if so, handle it; could concern multiple cells
        if self.source_chad:
            # need to split if still in same cell as begin marker line
            if self.cell_punched.source:  # already collected some material preceding this hole
                # append that as cell
                self.cell_punched.source = '\n'.join(self.cell_punched.source)
                self.nb_punched.cells.append(self.cell_punched)
                # reset
                self.cell_punched = copy.deepcopy(cell)
                self.cell_punched.source = []  # to be converted to single string in post_cell()

            # prepend material in source chad, except last if last has same cell type as this cell
            if TEST:
                print('Copying all-but-last cell from chad cell into hole: {} cells'
                      .format(len(self.source_chad[:-1])))
            self.nb_punched.cells.extend(self.source_chad[:-1])
            del self.source_chad[:-1]

            # check if receiver and source end cell have same type
            if self.args.source_chads[self.label][-1].cell_type == cell.cell_type:
                # copy any remaining content
                if TEST:
                    print('Copying from end chad cell to end hole cell: {}'
                          .format(repr(self.source_chad[-1].source)))
                self.cell_punched.source.append(self.source_chad[-1].source)
            else:  # receiving and source end cell types differ; put in a separate cell preceding this one
                if TEST:
                    print('Copying last cell from chad cell into hole: {} cells'
                          .format(len(self.source_chad[:-1])))
                self.nb_punched.cells.append(self.source_chad[-1])
            del self.source_chad[-1]  # now it is empty

        # copy marker line to result notebook, if desired
        if self.args.keep_marker_lines:
            self.cell_punched.source.append(line)

    def punch_outside_line(self, cell: NotebookNode, line: str):
        # copy line to result notebook
        self.cell_punched.source.append(line)

    def post_cell(self, cell: NotebookNode):
        # join source list into single string
        self.cell_punched.source = '\n'.join(self.cell_punched.source)

        if self.cell_punched.source or not self.inside or not self.args.punch_source:
            # transfer non-empty collected cell to result notebook
            self.nb_punched.cells.append(self.cell_punched)
            self.cell_punched = None
        # TODO not satisfactory when not copying marker lines; empty begin cell is suppressed, empty end cell not

    def post_nb(self):
        unused_chads = sorted(set(self.args.source_chads.keys()).difference(self.labels))
        if unused_chads:
            self.freq['unused source chads'] = len(unused_chads)
            if self.args.verbose:
                print('Labels of unused source chads: {}'.format(unused_chads))
        unfilled_labels = sorted(self.labels.difference(self.args.source_chads.keys()))
        if self.args.punch_source and unfilled_labels:
            if self.args.verbose:
                print('Labels of unfilled holes: {}'.format(unfilled_labels))

        return self.freq, self.nb_punched


class ChadsNotebookProcessor(PunchBaseProcessor):
    """Create chads notebook."""

    def __init__(self, nb: NotebookNode, args: Namespace):
        super().__init__(nb, args)
        # initialize result notebook
        self.nb_chads = copy.deepcopy(self.nb)
        self.nb_chads.cells = []  # it needs its own list object (avoid aliasing)

    def pre_cell(self, cell: NotebookNode):
        # create corresponding cell for chads notebook
        # we preserve everything, except possibly the source lines (this could result in empty cells)
        self.cell_chads = copy.deepcopy(cell)
        self.cell_chads.source = []  # to be converted to single string in post_cell()

    def punch_begin_marker_line(self, cell: NotebookNode, line: str):
        # copy marker line to result notebook, if desired
        if self.args.keep_marker_lines:
            self.cell_chads.source.append(line)

    def punch_end_marker_line(self, cell: NotebookNode, line: str):
        # copy marker line to result notebook, if desired
        if self.args.keep_marker_lines:
            self.cell_chads.source.append(line)

    def punch_inside_line(self, cell: NotebookNode, line: str):
        # copy line to result notebook
        self.cell_chads.source.append(line)

    def post_cell(self, cell: NotebookNode):
        # join source list into single string
        self.cell_chads.source = '\n'.join(self.cell_chads.source)

        # transfer collected cell to result notebook
        self.nb_chads.cells.append(self.cell_chads)

    def post_nb(self):
        return self.freq, self.nb_chads


class SourceChadsProcessor(PunchBaseProcessor):
    """Create chads for later use as source.
    Result is delivered in ``args.source_chads``,
    which is a dictionary that maps hole labels to hole content as list of cells.
    """

    def __init__(self, nb: NotebookNode, args: Namespace):
        super().__init__(nb, args)
        # initialize punched chads (which could serve as source chads in another punch)
        self.args.source_chads = {}  # dictionary of label-chad pairs

    def pre_cell(self, cell: NotebookNode):
        # start collecting hole content for args.source_chads
        if self.inside:
            self.cell_source_chads = copy.deepcopy(cell)
            self.cell_source_chads.source = []  # list of strings, to be consolidated into single string

    def punch_begin_marker_line(self, cell: NotebookNode, line: str):
        # start collecting hole content for args.source_chads
        self.cell_source_chads = copy.deepcopy(cell)
        self.cell_source_chads.source = []  # list of strings, to be consolidated into single string
        # we don't copy marker lines into args.punched_chads
        self.args.source_chads[self.label] = []  # overwrites previous chad, if label not unique

    def punch_end_marker_line(self, cell: NotebookNode, line: str):
        # finish collecting hole content for args.source_chads
        # join source list into single string
        self.cell_source_chads.source = '\n'.join(self.cell_source_chads.source)

        # transfer collected cell to result notebooks
        self.args.source_chads[self.label].append(self.cell_source_chads)

    def punch_inside_line(self, cell: NotebookNode, line: str):
        # copy line to result
        self.cell_source_chads.source.append(line)

    def post_cell(self, cell: NotebookNode):
        if self.inside:
            # finish collecting hole content for args.source_chads
            # join source list into single string
            self.cell_source_chads.source = '\n'.join(self.cell_source_chads.source)

            # transfer collected cell to result notebooks
            self.args.source_chads[self.label].append(self.cell_source_chads)

    def post_nb(self):
        return self.freq

