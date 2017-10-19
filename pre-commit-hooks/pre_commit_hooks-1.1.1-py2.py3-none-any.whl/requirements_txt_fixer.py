from __future__ import print_function

import argparse


PASS = 0
FAIL = 1


class Requirement(object):

    def __init__(self):
        super(Requirement, self).__init__()
        self.value = None
        self.comments = []

    @property
    def name(self):
        if self.value.startswith(b'-e '):
            return self.value.lower().partition(b'=')[-1]

        return self.value.lower().partition(b'==')[0]

    def __lt__(self, requirement):
        # \n means top of file comment, so always return True,
        # otherwise just do a string comparison with value.
        if self.value == b'\n':
            return True
        elif requirement.value == b'\n':
            return False
        else:
            return self.name < requirement.name


def fix_requirements(f):
    requirements = []
    before = tuple(f)
    after = []

    before_string = b''.join(before)

    # If the file is empty (i.e. only whitespace/newlines) exit early
    if before_string.strip() == b'':
        return PASS

    for line in before:
        # If the most recent requirement object has a value, then it's
        # time to start building the next requirement object.
        if not len(requirements) or requirements[-1].value is not None:
            requirements.append(Requirement())

        requirement = requirements[-1]

        # If we see a newline before any requirements, then this is a
        # top of file comment.
        if len(requirements) == 1 and line.strip() == b'':
            if len(requirement.comments) and requirement.comments[0].startswith(b'#'):
                requirement.value = b'\n'
            else:
                requirement.comments.append(line)
        elif line.startswith(b'#') or line.strip() == b'':
            requirement.comments.append(line)
        else:
            requirement.value = line

    # if a file ends in a comment, preserve it at the end
    if requirements[-1].value is None:
        rest = requirements.pop().comments
    else:
        rest = []

    for requirement in sorted(requirements):
        after.extend(requirement.comments)
        after.append(requirement.value)
    after.extend(rest)

    after_string = b''.join(after)

    if before_string == after_string:
        return PASS
    else:
        f.seek(0)
        f.write(after_string)
        f.truncate()
        return FAIL


def fix_requirements_txt(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('filenames', nargs='*', help='Filenames to fix')
    args = parser.parse_args(argv)

    retv = PASS

    for arg in args.filenames:
        with open(arg, 'rb+') as file_obj:
            ret_for_file = fix_requirements(file_obj)

            if ret_for_file:
                print('Sorting {}'.format(arg))

            retv |= ret_for_file

    return retv
