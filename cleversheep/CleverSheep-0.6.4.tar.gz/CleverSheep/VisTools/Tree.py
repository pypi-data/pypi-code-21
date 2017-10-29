#! /usr/bin/env python
"""A tree drawing module.

This module provides support for drawing trees using ASCII characters.

"""


import CleverSheep.Extras.ultraTB
import itertools
import sys


# TODO: This should get moved to Prog.Iter
def lookAhead(iterable):
    """Yields (el, isLast) for the iterable.

    This generator effectively does a single look-ahead in order to be able to
    indicate when the last element has been reached.

    :Param iterable:
        The sequence or iterable to be processed.
    """
    sentinel = []
    iterable = itertools.chain(iterable, [sentinel])
    prev = iterable.next()
    while not prev is sentinel:
        next = iterable.next()
        yield (prev, next is sentinel)
        prev = next


def walkTree(node, visit, getChildren, arg=None):
    """Walks any tree, regardless of its construction.

    The getChildren function must return an iterable of all the children
    in the node.

    :Paramaters:
      node
        The root node.
      visit
        The function to invoke for each node visited. This is invoked as
        ``visit(node, arg, isLast, hasChildren)``.
      getChildren
        The function that is ised to get the children of a node. This is
        invoked as ``getChildren(node)`` and must return an iterable.
      arg
        The ``arg`` passed to the `visit` function.

    """
    def _walk(node, arg=None, isLast=True):
        hasChildren = 0
        for child, _ignore in lookAhead(getChildren (node)):
            hasChildren = 1
            break
        arg, stop = visit (node, arg, isLast, hasChildren)
        if not stop:
            for child, isLast in lookAhead(getChildren (node)):
                _walk(child, arg, isLast)

    _walk(node, arg, isLast=True)


def drawTree (node, getChildren=lambda n:n.children,
        strFunc=lambda n:n.getText(), prefixFunc=lambda n:"",
        ind=4, tall=False, stream=None, chars='`o-|>', closure=None,
        width=140):
    """Draws a tree, starting at node.

    <+ Todo +>

    :Param node:
        The root node of the tree.
    :Param getChildren:
        The function that is ised to get the children of a node. This is
        invoked as ``getChildren(node)`` and must return an iterable.
    :Param strFunc:
        A function to call to get a node's text. This is invoked as
        ``strFunc(node)`` and should return a string, which may contain
        more than one line.
    :Param prefxiFunc:
        A function to call to get a node's prefix text. This is invoked as
        ``prefixFunc(node)`` and should return a string, which may contain
        more than one line.
    :Param ind:
        The indent to add for each level of the tree.
    :Param tall:
        If true then the tree will be drawn with extra vertical spacing.
    :Param stream:
        The file stream to write the tree to.
    :Param chars:
        The characters to use for different parts of the tree lines.
        The default value is ```o-|>``, which correspond to (in order):

            - The lower left corner.
            - The joint between a branch and its children.
            - The horizontal line.
            - The vertical line.
            - The arrow just before the node's text.

    :Param closure:
        This is currently unused.
    """
    stream = stream or sys.stdout
    elbowChar, jointChar, horChar, downChar, termChar = list(chars)
    l = ind - 2
    space = " " * l
    line = horChar * l

    def _draw (obj, arg, amLast, hasChildren):
        if arg:
            downPipe, tee, elbow = arg

        if tall: #pragma: debug
            stream.write(downPipe)
            stream.write("\n")

        midJoint = downPipe[:-1] + tee
        endJoint = downPipe[:-1] + elbow

        p = tee.index(jointChar)
        q = midJoint.index(jointChar)
        if amLast:
            downPipe = midJoint[:q-p] + " " * (p) + downChar
            leader = midJoint[:q-p] + " " * p + " "
        else:
            downPipe = midJoint[:q-p+1] + " " * (p-1) + downChar
            leader = midJoint[:q-p+1] + " " * p

        if not hasChildren:
            midJoint = midJoint.replace(jointChar, horChar)
            endJoint = endJoint.replace(jointChar, horChar)


        textWidth = width - len(midJoint) - 1
        text = strFunc(obj)
        prefix = prefixFunc(obj)
        pad = " " * len(prefix)

        try:
            lines = text.splitlines()
        except AttributeError: #pragma: debug
            lines = [text]
        for i, l in enumerate(lines):
            try: #pragma: debug
                if len(l) > textWidth:
                    l = l[:textWidth-3] + "..."
            except TypeError: #pragma: debug
                pass
            if prefix:
                if i == 0:
                    stream.write(prefix)
                else:
                    stream.write(pad)
            if i:
                if hasChildren:
                    stream.write(downPipe)
                    stream.write("  " + l)
                else:
                    stream.write(leader)
                    stream.write("  " + l)
            else:
                if amLast:
                    stream.write(endJoint)
                    stream.write(l)
                else:
                    stream.write(midJoint)
                    stream.write(l)
            stream.write("\n")

        return (downPipe, tee, elbow), False


    downPipe = ""
    tee = downChar + line + jointChar + horChar + termChar
    elbow = elbowChar + line + jointChar + horChar + termChar

    walkTree(node, _draw, getChildren, (downPipe, tee, elbow))


if __name__ == "__main__": #pragma: no cover

    def main(args):
        """The main for this module.

        <+Details+>
        """
        class N:
            def __init__(self, name):
                self.name = name
                self.children = []

        a = N("A")
        b = N("B")
        c = N("C")

        a.children = [b, c]
        drawTree(a, getChildren=lambda n: n.children, strFunc=lambda n:n.name)


    import argparse
    parser = argparse.ArgumentParser()

    global options
    args = parser.parse_args()

    main(args)
