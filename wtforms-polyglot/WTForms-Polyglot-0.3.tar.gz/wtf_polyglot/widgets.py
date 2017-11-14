from wtforms.widgets.core import html_params, HTMLString


__all__ = ('SubmitButton',)


class Button(object):
    """
    Render a basic ``<button>``.

    The field's label is used as the text of the button instead of the data on
    the field.
    """
    html_params = staticmethod(html_params)

    def __init__(self, button_type=None):
        if button_type is not None:
            self.button_type = button_type

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        kwargs.setdefault('type', self.button_type)
        kwargs.setdefault('value', field.label.text)
        return HTMLString('<button {}>{}</button>'
                          .format(self.html_params(name=field.name, **kwargs),
                                  kwargs['value']))


class SubmitButton(Button):
    """
    Render a submit button.
    """
    button_type = 'submit'
