from .base import LeafParserNode


class TextNode(LeafParserNode):
    def render(self, ctx, data, out):
        out(self.value)

    def compile(self, ctx, out):
        out.indent().write('out_write(%s)\n' % repr(self.value))


class CommentNode(TextNode):
    def render(self, ctx, data, out):
        if ctx.engine.strip_comments:
            return
        out(ctx.render_comment(self.text))

    def compile(self, ctx, out):
        pass
