import re

import flask
from mongoframes import And, Q
import wtforms.validators
from wtforms.validators import *
from wtforms.validators import ValidationError

# WTForm validators are passed through to provide a single access point
__all__ = set(wtforms.validators.__all__)
__all__.add('ErrorMessage')
__all__.add('RequiredIf')
__all__.add('ValidationError')
__all__.add('UniqueDocument')
__all__ = tuple(__all__)


class ErrorMessage(str):
    """
    The `ErrorMessage` class allows additional error information to be included
    with an error message. This can be useful when validators have additional
    information to relay to the user such as a suggested alternative to an
    invalid value.
    """

    def __new__(cls, content, raised_by, **kwargs):

        # The object that raised the error
        cls.raised_by = raised_by

        # Additional error information is add based on the kwargs
        for k, v in kwargs.items():
            setattr(cls, k, v)

        return str.__new__(cls, content)


class RequiredIf:
    """
    The `RequiredIf` validator allows the parent field to be flagged as required
    only if certain conditions are met.

    The set of conditions are specified using keywords when initializing the
    validator, for example:

        send_by = SelectField(
            'Send by',
            choices=[('sms', 'SMS'), ('email', 'Email')]
            )
        email = StringField('Email', [RequiredIf(send_by='email')])
        mobile_no = StringField('Mobile no.', [RequiredIf(send_by='sms')])
    """

    def __init__(self, **conditions):
        self.conditions = conditions

    def __call__(self, form, field):
        for name, value in self.conditions.items():

            assert name in form._fields, \
                'Condition field does not present in form.'

            # Check if the condition is met
            if form._fields.get(name).data == value:
                return InputRequired()(form, field)

        Optional()(form, field)


class UniqueDocument:
    """
    Validate that a field value is unique within a set of documents (optionally
    the set can be filtered).

    If a field value is found not to be unique and endpoint/args arguments are
    provided then the error raised will include a link to the view the other
    document with the same value.
    """

    def __init__(self, frame_cls, case_sensitive=True, endpoint=None,
                endpoint_args=None, alternative=None, message=None, **kwargs):

        # The frame class representing the document set
        self.frame_cls = frame_cls

        # A filter (either a query or function that returns a query) used to
        # filter the set of documents that must be unique.
        if 'filter' in kwargs:
            self.filter = kwargs['filter']
        else:
            self.filter = self.__class__.default_filter

        # A flag indicating if the unqiue nature of the field's value is case
        # sensitive.
        self.case_sensitive = case_sensitive

        # An endpoint and arguments that can be used to build a link to another
        # document with the same value. The end point arguments can either be a
        # dictionary or a function.
        self.endpoint = endpoint
        self.endpoint_args = endpoint_args

        # If alternative is specified it must be callable object that accepts
        # a value and an attempt index and returns an alternative value that
        # may be unique, e.g:
        #
        #     lambda v, i: '{v}-{i}'.format(v, i + 1)
        #
        # Would return the following for the string `my-example`:
        #
        #     > 'my-example-1'
        #     > 'my-example-2'
        #     > 'my-example-3'
        #
        # And so on. The field will try at most 100 times to generate a valid
        # unique alternative value before giving up.
        self.alternative = alternative

        # The error message to display if the asset isn't the required type
        self.message = message

    def __call__(self, form, field):
        if not field.data:
            return

        # Build the filter for the set of documents that must be unique
        base_filter = None
        if callable(self.filter):
            base_filter = self.filter(form, field)
        elif self.filter:
            base_filter = self.filter

        # Check the document is unique
        value = field.data
        other = self.find_matching(field.name, value, base_filter)
        if other:

            # If an endpoint is defined build a link to the other document
            url = None
            if self.endpoint:
                kwargs = self.endpoint_args
                if callable(self.endpoint_args):
                    kwargs = self.endpoint_args(other)
                url = flask.url_for(self.endpoint, **kwargs)

            # If an alternative callable is defined attempt to find a valid
            # alternative.
            alternative = None
            if self.alternative:
                for i in range(0, 100):
                    new_value = self.alternative(value, i)
                    if self.is_unique(field.name, new_value, base_filter):
                        alternative = new_value
                        break

            # Compile the message for the error
            message = self.message
            mark_safe = True
            if message is None:
                message = field.gettext(
                    'Another document exists with the same value')

            message = ErrorMessage(
                message,
                self,
                alternative=alternative,
                matching_url=url
                )

            # Raise a validation error
            raise ValidationError(message)

    def find_matching(self, name, value, base_filter):
        """Return any document that matches the given value"""

        if not self.case_sensitive:
            value = re.compile(value, re.I)
        filter = Q[name] == value

        if base_filter:
            filter = And(filter, base_filter)
        return self.frame_cls.one(filter)

    def is_unique(self, name, value, base_filter):
        """Return True if the given value is unique"""

        if not self.case_sensitive:
            value = re.compile(value, re.I)
        filter = Q[name] == value

        if base_filter:
            filter = And(filter, base_filter)
        return self.frame_cls.count(filter) == 0

    @staticmethod
    def default_filter(form, field):
        """
        The default filter applied when checking if a field is unique, by
        default we return a filter that checks if a document is being updated
        and if so excludes itself from the unique test.
        """
        if form.obj:
            return Q._id != form.obj._id