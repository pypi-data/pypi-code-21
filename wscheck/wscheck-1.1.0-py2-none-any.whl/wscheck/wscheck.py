import re

RULES = {
    'WSW001': 'Bad line ending',
    'WSW002': 'Tailing whitespace',
    'WSW003': 'Indentation is not multiple of 2',
    'WSW004': 'Indentation with non-space character',
    'WSW005': 'No newline at end of file',
    'WSW006': 'Too many newline at end of file',
}


class WhitespaceChecker(object):
    LINE_TEMPLATE = re.compile(r'([^\n\r]*)(\r\n|\r|\n|)', re.MULTILINE)
    TAILING_WHITESPACE_TEMPLATE = re.compile(r'\s+$')
    LINE_INDENT_TEMPLATE = re.compile(r'^\s+')
    NOT_SPACES_TEMPLATE = re.compile(r'[^ ]')

    def __init__(self, excluded_rules=None):
        excluded_rules = excluded_rules or []

        self._rules = {
            rule_id: rule_message
            for rule_id, rule_message in RULES.items()
            if rule_id not in excluded_rules
        }
        if not self._rules:
            raise RuntimeError('No rules to check')

        self._checkers = [
            self._check_by_lines,
            self._check_eof
        ]

        self._issues = []

    @property
    def issues(self):
        return self._issues

    def check_file(self, file_path):
        lines = self._read_file_lines_w_eol(file_path)
        for checker in self._checkers:
            checker(file_path, lines)

    def _read_file_lines_w_eol(self, file_path):
        with open(file_path) as fd:
            file_content = fd.read()
        lines = self.LINE_TEMPLATE.findall(file_content)

        # Workaround: can not match end of string in multi line regexp
        if len(lines) > 1 and lines[-2][1] == '':
            lines.pop()

        return lines

    def _check_by_lines(self, file_path, lines):
        for row, line_eol in enumerate(lines):
            line, eol = line_eol

            if 'WSW001' in self._rules:
                if not eol == '' and not eol == '\n':
                    self._add_issue(rule='WSW001', path=file_path, row=row, column=len(line), context=line,
                                    message_suffix='{!r}'.format(eol))

            if 'WSW002' in self._rules:
                tailing_whitespace_match = self.TAILING_WHITESPACE_TEMPLATE.search(line)
                if tailing_whitespace_match is not None:
                    self._add_issue(rule='WSW002', path=file_path, row=row, column=len(line) - 1, context=line)

            if line.strip() == '':
                continue

            indent_match = self.LINE_INDENT_TEMPLATE.match(line)
            if indent_match is not None:
                line_indent = indent_match.group()

                if 'WSW003' in self._rules:
                    if not len(line_indent) % 2 == 0:
                        self._add_issue(rule='WSW003', path=file_path, row=row, column=0, context=line)

                if 'WSW004' in self._rules:
                    character_match = self.NOT_SPACES_TEMPLATE.search(line_indent)
                    if character_match is not None:
                        self._add_issue(rule='WSW004', path=file_path, row=row, column=character_match.start(),
                                        context=line)

    def _add_issue(self, rule, path, row, column, context, message_suffix=None):
        self._issues.append({'rule': rule, 'path': path, 'row': row, 'column': column, 'context': context,
                            'message_suffix': message_suffix})

    def _check_eof(self, file_path, lines):
        if len(lines) == 0:
            return

        empty_lines = 0
        for row, line_eol in reversed(tuple(enumerate(lines))):
            line, eol = line_eol
            if not line == '':
                break
            empty_lines += 1

        if 'WSW005' in self._rules:
            if empty_lines == 0:
                line = lines[-1][0]
                self._add_issue(rule='WSW005', path=file_path, row=len(lines), column=0, context=line)
        if 'WSW006' in self._rules:
            if empty_lines > 1:
                shift = min(len(lines), empty_lines + 1)
                line = lines[-shift][0]
                self._add_issue(rule='WSW006', path=file_path, row=len(lines) - shift, column=len(line), context=line,
                                message_suffix='(+{})'.format(empty_lines - 1))
