"""
UI related capabilities for the text editor widget embedded in each tab in Mu.

Copyright (c) 2015-2017 Nicholas H.Tollervey and others (see the AUTHORS file).

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import keyword
import os
import re
import logging
import os.path
from collections import defaultdict
from PyQt5.Qsci import QsciScintilla, QsciLexerPython, QsciAPIs
from mu.interface.themes import Font, DayTheme


# Regular Expression for valid individual code 'words'
RE_VALID_WORD = re.compile('^[A-Za-z0-9_-]*$')


logger = logging.getLogger(__name__)


class PythonLexer(QsciLexerPython):
    """
    A Python specific "lexer" that's used to identify keywords of the Python
    language so the editor can do syntax highlighting.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setHighlightSubidentifiers(False)

    def keywords(self, flag):
        """
        Returns a list of Python keywords.
        """
        if flag == 1:
            kws = keyword.kwlist + ['self', 'cls']
        elif flag == 2:
            kws = __builtins__.keys()
        else:
            return None
        return ' '.join(kws)


class EditorPane(QsciScintilla):
    """
    Represents the text editor.
    """

    def __init__(self, path, text):
        super().__init__()
        self.path = path
        self.setText(text)
        self.check_indicators = {  # IDs are arbitrary
            'error': {'id': 19, 'markers': {}},
            'style': {'id': 20, 'markers': {}}
        }
        self.BREAKPOINT_MARKER = 23  # Arbitrary
        self.search_indicators = {
            'selection': {'id': 21, 'positions': []}
        }
        self.previous_selection = {
            'line_start': 0, 'col_start': 0, 'line_end': 0, 'col_end': 0
        }
        self.lexer = PythonLexer()
        self.api = None
        self.has_annotations = False
        self.setModified(False)
        self.breakpoint_lines = set()
        self.configure()

    def configure(self):
        """
        Set up the editor component.
        """
        # Font information
        font = Font().load()
        self.setFont(font)
        # Generic editor settings
        self.setUtf8(True)
        self.setAutoIndent(True)
        self.setIndentationsUseTabs(False)
        self.setIndentationWidth(4)
        self.setIndentationGuides(True)
        self.setBackspaceUnindents(True)
        self.setTabWidth(4)
        self.setEdgeColumn(79)
        self.setMarginLineNumbers(0, True)
        self.setMarginWidth(0, 50)
        self.setBraceMatching(QsciScintilla.SloppyBraceMatch)
        self.SendScintilla(QsciScintilla.SCI_SETHSCROLLBAR, 0)
        self.set_theme()
        # Markers and indicators
        self.setMarginSensitivity(0, True)
        self.markerDefine(self.Circle, self.BREAKPOINT_MARKER)
        self.setMarginSensitivity(1, True)
        self.setIndicatorDrawUnder(True)
        for type_ in self.check_indicators:
            self.indicatorDefine(
                self.SquiggleIndicator, self.check_indicators[type_]['id'])
        for type_ in self.search_indicators:
            self.indicatorDefine(
                self.StraightBoxIndicator, self.search_indicators[type_]['id'])
        self.setAnnotationDisplay(self.AnnotationBoxed)
        self.selectionChanged.connect(self.selection_change_listener)

    def connect_margin(self, func):
        """
        Connect clicking the margin to the passed in handler function.
        """
        self.marginClicked.connect(func)

    def set_theme(self, theme=DayTheme):
        """
        Connect the theme to a lexer and return the lexer for the editor to
        apply to the script text.
        """
        theme.apply_to(self.lexer)
        self.lexer.setDefaultPaper(theme.Paper)
        self.setCaretForegroundColor(theme.Caret)
        self.setMarginsBackgroundColor(theme.Margin)
        self.setMarginsForegroundColor(theme.Caret)
        self.setIndicatorForegroundColor(theme.IndicatorError,
                                         self.check_indicators['error']['id'])
        self.setIndicatorForegroundColor(theme.IndicatorStyle,
                                         self.check_indicators['style']['id'])
        for type_ in self.search_indicators:
            self.setIndicatorForegroundColor(
                theme.IndicatorWordMatch, self.search_indicators[type_]['id'])
        self.setMarkerBackgroundColor(theme.BreakpointMarker,
                                      self.BREAKPOINT_MARKER)
        self.setAutoCompletionThreshold(2)
        self.setAutoCompletionSource(QsciScintilla.AcsAll)
        self.setLexer(self.lexer)
        self.setMatchedBraceBackgroundColor(theme.BraceBackground)
        self.setMatchedBraceForegroundColor(theme.BraceForeground)
        self.setUnmatchedBraceBackgroundColor(theme.UnmatchedBraceBackground)
        self.setUnmatchedBraceForegroundColor(theme.UnmatchedBraceForeground)

    def set_api(self, api_definitions):
        """
        Sets the API entries for tooltips, calltips and the like.
        """
        self.api = QsciAPIs(self.lexer)
        for entry in api_definitions:
            self.api.add(entry)
        self.api.prepare()

    @property
    def label(self):
        """
        The label associated with this editor widget (usually the filename of
        the script we're editing).

        If the script has been modified since it was last saved, the label will
        end with an asterisk.
        """
        if self.path:
            label = os.path.basename(self.path)
        else:
            label = 'untitled'
        # Add an asterisk to indicate that the file remains unsaved.
        if self.isModified():
            return label + ' *'
        else:
            return label

    def reset_annotations(self):
        """
        Clears all the assets (indicators, annotations and markers).
        """
        self.clearAnnotations()
        self.markerDeleteAll()
        self.reset_search_indicators()
        self.reset_check_indicators()

    def reset_check_indicators(self):
        """
        Clears all the text indicators related to the check code functionality.
        """
        for indicator in self.check_indicators:
            for _, markers in \
                    self.check_indicators[indicator]['markers'].items():
                line_no = markers[0]['line_no']  # All markers on same line.
                self.clearIndicatorRange(
                    line_no, 0, line_no, 999999,
                    self.check_indicators[indicator]['id'])
            self.check_indicators[indicator]['markers'] = {}

    def reset_search_indicators(self):
        """
        Clears all the text indicators from the search functionality.
        """
        for indicator in self.search_indicators:
            for position in self.search_indicators[indicator]['positions']:
                self.clearIndicatorRange(
                    position['line_start'], position['col_start'],
                    position['line_end'], position['col_end'],
                    self.search_indicators[indicator]['id'])
            self.search_indicators[indicator]['positions'] = []

    def annotate_code(self, feedback, annotation_type='error'):
        """
        Given a list of annotations add them to the editor pane so the user can
        act upon them.
        """
        indicator = self.check_indicators[annotation_type]
        for line_no, messages in feedback.items():
            indicator['markers'][line_no] = messages
            for message in messages:
                col = message.get('column', 0)
                if col:
                    col_start = col - 1
                    col_end = col + 1
                    self.fillIndicatorRange(line_no, col_start, line_no,
                                            col_end, indicator['id'])

    def show_annotations(self):
        """
        Display all the messages to be annotated to the code.
        """
        lines = defaultdict(list)
        for indicator in self.check_indicators:
            markers = self.check_indicators[indicator]['markers']
            for k, marker_list in markers.items():
                for m in marker_list:
                    lines[m['line_no']].append(m['message'])
        for line, messages in lines.items():
            text = '\n'.join(messages).strip()
            if text:
                self.annotate(line, text, self.annotationDisplay())

    def find_next_match(self, text, from_line=-1, from_col=-1,
                        case_sensitive=True, wrap_around=True):
        """
        Finds the next text match from the current cursor, or the given
        position, and selects it (the automatic selection is the only available
        QsciScintilla behaviour).
        Returns True if match found, False otherwise.
        """
        return self.findFirst(
            text,            # Text to find,
            False,           # Treat as regular expression
            case_sensitive,  # Case sensitive search
            True,            # Whole word matches only
            wrap_around,     # Wrap search
            forward=True,    # Forward search
            line=from_line,  # -1 starts at current position
            index=from_col,  # -1 starts at current position
            show=False,      # Unfolds found text
            posix=False)     # More POSIX compatible RegEx

    def range_from_positions(self, start_position, end_position):
        """Given a start-end pair, such as are provided by a regex match,
        return the corresponding Scintilla line-offset pairs which are
        used for searches, indicators etc.

        FIXME: Not clear whether the Scintilla conversions are expecting
        bytes or characters (ie codepoints)
        """
        start_line, start_offset = self.lineIndexFromPosition(start_position)
        end_line, end_offset = self.lineIndexFromPosition(end_position)
        return start_line, start_offset, end_line, end_offset

    def highlight_selected_matches(self):
        """
        Checks the current selection, if it is a single word it then searches
        and highlights all matches.

        Since we're interested in exactly one word:
        * Ignore an empty selection
        * Ignore anything which spans more than one line
        * Ignore more than one word
        * Ignore anything less than one word
        """
        selected_range = line0, col0, line1, col1 = self.getSelection()
        #
        # If there's no selection, do nothing
        #
        if selected_range == (-1, -1, -1, -1):
            return

        #
        # Ignore anything which spans two or more lines
        #
        if line0 != line1:
            return

        #
        # Ignore if no text is selected or the selected text is not at most one
        # valid identifier-type word.
        #
        selected_text = self.selectedText()
        if not RE_VALID_WORD.match(selected_text):
            return

        #
        # Ignore anything which is not a whole word.
        # NB Although Scintilla defines a SCI_ISRANGEWORD message,
        # it's not exposed by QSciScintilla. Instead, we
        # ask Scintilla for the start end end position of
        # the word we're in and test whether our range end points match
        # those or not.
        #
        pos0 = self.positionFromLineIndex(line0, col0)
        word_start_pos = self.SendScintilla(
            QsciScintilla.SCI_WORDSTARTPOSITION, pos0, 1)
        _, start_offset = self.lineIndexFromPosition(word_start_pos)
        if col0 != start_offset:
            return

        pos1 = self.positionFromLineIndex(line1, col1)
        word_end_pos = self.SendScintilla(
            QsciScintilla.SCI_WORDENDPOSITION, pos1, 1)
        _, end_offset = self.lineIndexFromPosition(word_end_pos)
        if col1 != end_offset:
            return

        #
        # For each matching word within the editor text, add it to
        # the list of highlighted indicators and fill it according
        # to the current theme.
        #
        indicators = self.search_indicators['selection']
        text = self.text()
        for match in re.finditer(selected_text, text):
            range = self.range_from_positions(*match.span())
            #
            # Don't highlight the text we've selected
            #
            if range == selected_range:
                continue

            line_start, col_start, line_end, col_end = range
            indicators['positions'].append({
                'line_start': line_start, 'col_start': col_start,
                'line_end': line_end, 'col_end': col_end
            })
            self.fillIndicatorRange(line_start, col_start, line_end,
                                    col_end, indicators['id'])

    def selection_change_listener(self):
        """
        Runs every time the text selection changes. This could get triggered
        multiple times while the mouse click is down, even if selection has not
        changed in itself.
        If there is a new selection is passes control to
        highlight_selected_matches.
        """
        # Get the current selection, exit if it has not changed
        line_from, index_from, line_to, index_to = self.getSelection()
        if self.previous_selection['col_end'] != index_to or \
                self.previous_selection['col_start'] != index_from or \
                self.previous_selection['line_start'] != line_from or \
                self.previous_selection['line_end'] != line_to:
            self.previous_selection['line_start'] = line_from
            self.previous_selection['col_start'] = index_from
            self.previous_selection['line_end'] = line_to
            self.previous_selection['col_end'] = index_to
            # Highlight matches
            self.reset_search_indicators()
            self.highlight_selected_matches()
