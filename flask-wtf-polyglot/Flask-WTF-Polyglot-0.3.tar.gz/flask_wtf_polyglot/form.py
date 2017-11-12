from flask_wtf.form import FlaskForm

from wtf_polyglot.meta import PolyglotMeta


class PolyglotForm(FlaskForm):
    Meta = PolyglotMeta
