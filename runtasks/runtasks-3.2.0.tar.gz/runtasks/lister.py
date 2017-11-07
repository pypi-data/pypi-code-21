
import re, inspect

INDENT = '  '


def print_doc(task):
    """
    Prints the documentation for a single task.
    """
    print(task.name)
    sig = inspect.signature(task.func)
    if sig.parameters:
        print(INDENT + ' '.join(str(p) for p in sig.parameters.values()))

    doc = getattr(task.func, '__doc__', None)
    if doc:
        if sig.parameters:
            print()

        doc = format_doc(task)
        print(doc)


def format_doc(task):
    """
    Formats documentation by removing leading spaces and trailing spaces.

    If there are multiple lines, such as a triple quoted string, leading spaces are removed
    from each until the line with the least spaces is right aligned.  We don't want to lose
    indentation *within* the documentation.
    """

    doc = getattr(task.func, '__doc__', None)
    if not doc:
        return None

    lines = [line.rstrip() for line in doc.rstrip().splitlines()]

    while lines and not lines[0]:
        lines.pop(0)

    if not lines:
        return None

    # We want the entire block indented by 1 space, so we need to see what the current minimum
    # indentation is.  However, the first line could be a blank line caused by a triple quoted
    # string using the format you see in this file, so remove it.

    re_space = re.compile('[ ]*')
    existing_indent = min(re_space.match(line).end() for line in lines if line)

    desired_indent = len(INDENT)

    if existing_indent < desired_indent:
        spaces = ' ' * (desired_indent - existing_indent)
        lines = [spaces + line for line in lines]
    elif existing_indent > desired_indent:
        remove = (existing_indent - desired_indent)
        lines = [line[remove:] for line in lines]

    return '\n'.join(lines)


def print_list(tasks):
    """
    Called when "--list" is passed on the command line.  Prints the list of available tasks.
    """
    names = sorted(list(tasks.keys()))
    print('Available tasks:')
    print()
    for name in names:
        task = tasks[name]
        print_doc(task)
        print()
