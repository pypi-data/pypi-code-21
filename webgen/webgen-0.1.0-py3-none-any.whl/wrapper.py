import webgen.dom as dom
import webgen.filegen as fg


def empty_html():
    pass


def head(stylesheet, title_text, charset='utf-8'):
    if isinstance(stylesheet, str):
        stylesheet_path = stylesheet
    else:
        stylesheet_path = stylesheet.filepath()

    return dom.Head(dom.Title(title_text),
                    dom.Meta(charset=charset),
                    dom.Link(rel='stylesheet', href=stylesheet_path))


def list_ordered(element_number, *args):
    elements = []
    for i in range(element_number):
        if i < len(args):
            elements.append(dom.Li(args[i]))
        else:
            elements.append(dom.Li())

    return dom.Ol(*elements)


def list_unordered(element_number, *args):
    elements = []
    for i in range(element_number):
        if i < len(args):
            elements.append(dom.Li(args[i]))
        else:
            elements.append(dom.Li())

    return dom.Ul(*elements)


def navbar():
    pass