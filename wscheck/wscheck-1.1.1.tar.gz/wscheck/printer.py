from collections import OrderedDict
from lxml import builder, etree

from checker import RULES

BUILD = builder.ElementMaker()


class ErrorPrinter(object):
    def __init__(self, files, issues):
        """
        :type files: list
        :type issues: list
        """
        self._files = sorted(files)
        self._issues = sorted(issues, key=lambda issue: (issue['path'], issue['line'], issue['col']))

    def print_to_tty(self):
        glue_text = ''

        for issue in self._issues:
            context = issue['context']
            message_indent = issue['col'] - 1
            message = self._get_message(issue)

            index = 0
            while index >= 0:
                index = context.find('\t', index)
                if index == -1:
                    break

                context = '{}--->{}'.format(context[:index], context[index + 1:])
                if index < message_indent:
                    message_indent += 3

                index += 4

            print('{glue}In {path} line {row}:\n{context}\n{message_indent}^-- {message}'.format(
                glue=glue_text,
                path=issue['path'],
                row=issue['line'],
                context=context,
                message_indent=' ' * message_indent,
                message='{}: {}'.format(issue['rule'], message)
            ))

            glue_text = '\n'

    def _get_message(self, issue):
        """
        :type issue: dict
        :rtype: str
        """
        message = RULES[issue['rule']]
        if issue['message_suffix']:
            message = '{} {}'.format(message, issue['message_suffix'])
        return message

    def write_checkstyle(self, file_path):
        """
        :type file_path: str
        """
        file_elements = OrderedDict(
            (path, BUILD.file(name=path))
            for path in sorted(self._files, key=lambda path: path.lower())
        )

        for issue in self._issues:
            file_elements[issue['path']].append(
                BUILD.error(
                    line='{}'.format(issue['line']),
                    column='{}'.format(issue['col']),
                    severity='warning',
                    message=self._get_message(issue),
                    source='WhitespaceCheck.{}'.format(issue['rule'])
                )
            )

        checkstyle_element = BUILD.checkstyle(version='4.3')
        for file_element in file_elements.values():
            checkstyle_element.append(file_element)
        tree = etree.ElementTree(checkstyle_element)

        tree.write(file_path, encoding='utf-8', xml_declaration=True, pretty_print=True)
