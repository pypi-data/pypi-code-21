from wtforms.form import Form

from wtf_polyglot.meta import PolyglotMeta


class PolyglotForm(Form):
    """
    Base form class which renders its fields using polyglot HTML5 output.
    """

    Meta = PolyglotMeta
