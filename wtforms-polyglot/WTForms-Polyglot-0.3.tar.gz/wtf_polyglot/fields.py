from wtforms.fields.core import BooleanField

from .widgets import SubmitButton


__all__ = ('SubmitField',)


class SubmitField(BooleanField):
    """
    Represents an ``<button type='submit'>...</button>``.

    This allows checking if a given submit button has been pressed.
    """
    widget = SubmitButton()
