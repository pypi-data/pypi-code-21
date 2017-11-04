import argparse
import re
import textwrap

import tcm


CONTROL_HELP = 'Path to control file.'
DESCRIPTION = '''\
    Merges multiple lists of TACL works together in a specified order,
    and outputs one or more catalogue files using supplied labels.'''
EPILOG = '''\
FILES

This program makes use of several types of file:

* Group files: These list TACL works that belong to a group, where the
  group name is the filename (basename only, not the full path). The
  content is one or more work names, one per line.

* Groups files: These specify the individual group files to be merged
  together and the order in which this merge occurs. The content is
  one or more paths to group files, one per line.

* Mapping files: These specify a many to one mapping between group
  names and labels. The order determines the order the labels appear
  in the output catalogue. The content is a group name followed by
  whitespace followed by the label. If only a group name is given on a
  line, then the label is taken as blank: any works in that group
  will appear in the generated catalogue but without a label.

* Control files: These specify a single groups file to handle the
  merge, and one or more mapping files to handle the output of
  catalogues. The content is per the following example:

    [MERGING]
    # The "groups" key specifies the path to the groups file giving
    # the ordered list of group files to use in a merge.
    groups = attribution-groups.txt

    [MAPPING]
    # Each catalogue output is specified here as a mapping file path
    # key and an output file path value.
    attribution-mapping.txt = attribution.txt
    chronology-mapping.txt = chronology.txt
'''
OUTPUT_HELP = 'Path to directory to save catalogues to.'


class ParagraphFormatter (argparse.ArgumentDefaultsHelpFormatter):

    """argparse formatter to maintain paragraph breaks in text, while
    wrapping those blocks.

    Code minimally adapted from the patch at
    http://bugs.python.org/file28091, authored by rurpy2.

    """

    def _split_lines(self, text, width):
        return self._para_reformat(text, width, multiline=True)

    def _fill_text(self, text, width, indent):
        lines = self._para_reformat(text, width, indent, True)
        return '\n'.join(lines)

    def _para_reformat(self, text, width, indent='', multiline=False):
        new_lines = list()
        main_indent = len(re.match(r'( *)', text).group(1))

        def blocker(text):
            """On each call yields 2-tuple consisting of a boolean and
            the next block of text from 'text'.  A block is either a
            single line, or a group of contiguous lines.  The former
            is returned when not in multiline mode, the text in the
            line was indented beyond the indentation of the first
            line, or it was a blank line (the latter two jointly
            referred to as "no-wrap" lines).  A block of concatenated
            text lines up to the next no-wrap line is returned when
            in multiline mode.  The boolean value indicates whether
            text wrapping should be done on the returned text."""
            block = list()
            for line in text.splitlines():
                line_indent = len(re.match(r'( *)', line).group(1))
                isindented = line_indent - main_indent > 0
                isblank = re.match(r'\s*$', line)
                if isblank or isindented:
                    # A no-wrap line.
                    if block:
                        # Yield previously accumulated block of text
                        # if any, for wrapping.
                        yield True, ''.join(block)
                        block = list()
                    # And now yield our no-wrap line.
                    yield False, line
                else:
                    # We have a regular text line.
                    if multiline:
                        # In multiline mode accumulate it.
                        block.append(line)
                    else:
                        # Not in multiline mode, yield it for
                        # wrapping.
                        yield True, line
            if block:
                # Yield any text block left over.
                yield (True, ''.join(block))

        for wrap, line in blocker(text):
            if wrap:
                # We have either a single line or a group of
                # concatented lines.  Either way, we treat them as a
                # block of text and wrap them (after reducing multiple
                # whitespace to just single space characters).
                line = self._whitespace_matcher.sub(' ', line).strip()
                # Textwrap will do all the hard work for us.
                new_lines.extend(textwrap.wrap(text=line, width=width,
                                               initial_indent=indent,
                                               subsequent_indent=indent))
            else:
                # The line was a no-wrap one so leave the formatting
                # alone.
                new_lines.append(line[main_indent:])
        return new_lines


def main():
    parser = argparse.ArgumentParser(description=DESCRIPTION, epilog=EPILOG,
                                     formatter_class=ParagraphFormatter)
    parser.add_argument('control', help=CONTROL_HELP, metavar='CONTROL')
    parser.add_argument('output', help=OUTPUT_HELP, metavar='OUTPUT')
    args = parser.parse_args()
    controller = tcm.Controller()
    controller.load_control(args.control)
    report = controller.generate_catalogues(args.output)
    print('\n'.join(report))
