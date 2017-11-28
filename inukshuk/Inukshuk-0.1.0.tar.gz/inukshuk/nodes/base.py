
class ParserNode:
    own_close = False

    def __init__(self):
        pass

    def iterChildren(self):
        raise NotImplementedError()

    def add(self, node):
        raise NotImplementedError()

    def parse(self, parser):
        raise NotImplementedError()

    def recurseInto(self, parser, node):
        self.add(node)
        node.parse(parser)

    def render(self, ctx, data, out):
        raise NotImplementedError(
            "%s doesn't implement direct rendering." % type(self))

    def compile(self, ctx, out):
        raise NotImplementedError(
            "%s doesn't implement compilation." % type(self))


class LeafParserNode(ParserNode):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def iterChildren(self):
        return iter(())

    def parse(self, parser):
        pass

    def render(self, ctx, data, out):
        return self.value

    def compile(self, ctx, out):
        ctx.pushvar(repr(self.value))


class SingleChildParserNode(ParserNode):
    def __init__(self):
        self.child = None

    def iterChildren(self):
        yield self.child

    def add(self, node):
        if self.child is None:
            self.child = node
        else:
            raise Exception("This node already has a child: %s" % self.child)

    def render(self, ctx, data, out):
        return self.child.render(ctx, data, out)

    def compile(self, ctx, out):
        self.child.compile(ctx, out)


class MultiChildrenParserNode(ParserNode):
    def __init__(self):
        self.children = []

    def iterChildren(self):
        return iter(self.children)

    def add(self, node):
        if node in self.children:
            raise Exception("The given node is already a child of "
                            "the current node.")
        self.children.append(node)

    def render(self, ctx, data, out):
        for c in self.children:
            c.render(ctx, data, out)

    def compile(self, ctx, out):
        for c in self.children:
            c.compile(ctx, out)


class ParserError(Exception):
    def __init__(self, line_num, message):
        super().__init__("Error line %d: %s" % (line_num, message))
        self.line_num = line_num
        self.message = message
