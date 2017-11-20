import os
from datetime import timedelta
from hashlib import sha1

import flask
from wtforms.csrf.session import SessionCSRF
from wtforms.fields import FormField, FieldList
from wtforms.form import Form

__all__ = [
    'BaseForm',
    'CSRF'
    ]


class BaseForm(Form):
    """
    Base form class for manhattan applications. The base form adds the following
    behaviours to the standard `wtforms.Form` class:

    - By default whitespace is stripped from submitted values, this is achieved
      by assigning a filter to each applicable field that calls strip against
      the fields value. To disable this behaviour you cant set the meta class
      attribute `strip_input` to `False`.
    - CSRF protection is implement by forms but by default is disabled as the
      recommended approach to implementing CSRF protection to an application is
      through the use of the `CSRF` class. To enable CSRF protection `csrf`
      needs to be set to True and a `CSRF_SECRET_KEY` must be set against the
      application config.
    """

    class Meta:

        csrf = False
        csrf_class = SessionCSRF
        csrf_time_limit = timedelta(minutes=30)

        strip_input = True

        @property
        def csrf_context(self):
            return flask.session

        @property
        def csrf_secret(self):
            return flask.current_app.config.get('CSRF_SECRET_KEY')\
                    .encode('utf8')

        def bind_field(self, form, unbound_field, options):
            # Apply the a filter to strip whitespace
            field_cls = unbound_field.field_class

            # Define the field classes that are unapplicable
            unapplicable = (FormField, FieldList)

            # If input stripping is enabled and applicable to this field then
            # add the `strip_filter` as the first filter for the field.
            if self.strip_input and not issubclass(field_cls, unapplicable):
                options['filters'] = [self.strip_filter] + \
                        options.get('filters', [])

            return unbound_field.bind(form=form, **options)

        @staticmethod
        def strip_filter(v):
            """A filter that strips from a value"""
            if hasattr(v, 'strip'):
                return v.strip()
            return v

    def __init__(self, formdata=None, obj=None, prefix='', data=None, meta=None,
            **kwargs):

        # Retain a reference to the `obj` passed on init
        self._obj = obj

        super().__init__(formdata, obj, prefix, data, meta, **kwargs)

    # Read-only properties

    @property
    def obj(self):
        """Return the `obj` passed to the form when initialized"""
        return self._obj


class CSRF:
    """
    Support for CSRF protection for Flask applications.
    """

    _app = None

    _exempt_blueprints = set()
    _exempt_views = set()

    # This private form class is used to implement CSRF protection, a separate
    # form class is used to prevent changes to BaseForm affecting CSRF
    # protection.
    class _CSRFForm(BaseForm):
        class Meta:
            csrf = True

    @classmethod
    def init_app(cls, app):
        """
        The `init_app` methods adds CSRF protection to a Flask application, for
        example:

            import flask
            from manhattan.forms import CSRF

            app = flask.Flask(__name__)

            # The `SECRET_KEY` must be configured for Flask sessions
            app.config['SECRET_KEY'] = '...'

            # We also need to configure a secret key for CSRF
            app.config['CSRF_SECRET_KEY'] = '...'

            # Add CSRF protection to the app
            CSRF.init_app(app)

        By default `POST`, `PUT` and `PATCH` methods are protected by this can
        be configured by setting `CSRF_METHODS` against the application config.
        """

        cls._app = app

        assert app.config.get('CSRF_SECRET_KEY'), \
                '`CSRF_SECRET_KEY` must be set in the `app.config`'

        # Set app config defaults
        app.config.setdefault('CSRF_METHODS', ['POST', 'PUT', 'PATCH'])

        # Set the time limit for the CSRF token in specified in settings
        if app.config.get('CSRF_TIME_LIMIT'):
            cls._CSRFForm.Meta.csrf_time_limit = app.config.get(
                'CSRF_TIME_LIMIT'
            )

        # Add crsf_token to jinja
        @app.context_processor
        def csrf_token():
            return dict(csrf_token=cls.generate_token)

        # Add CRSF protection to the app
        @app.before_request
        def _csrf_protect():
            # If the request method is not protected bail
            if flask.request.method not in app.config['CSRF_METHODS']:
                return

            # Check the endpoint is set (it wont be if there's an exception)
            if not flask.request.endpoint:
                return

            # Check we can find the view the endpoint relates to
            view = app.view_functions.get(flask.request.endpoint)
            if not view:
                return

            # Check if the blueprint is exempt
            if flask.request.blueprint in cls._exempt_blueprints:
                return

            # Check if the view is exempt
            view_path = '{v.__module__}.{v.__name__}'.format(v=view)
            if view_path in cls._exempt_views:
                return

            if not cls.validate_token():
                flask.abort(400, 'CSRF token missing or incorrect.')

    @classmethod
    def generate_token(cls):
        """Generate a CSRF token"""
        return cls._CSRFForm().csrf_token.current_token

    @classmethod
    def validate_token(cls):
        """Validate a CSRF token"""
        return cls._CSRFForm(flask.request.values).validate()

    @classmethod
    def exempt(cls, view):
        """
        Use as a decorator or simply call to declare a view or blueprint as
        exempt from CSRF protection:

            CSRF.exempt(my_blueprint)

            @CSRF.exempt
            @app.route('/my-view', methods=['GET', 'POST'])
            def my_view():
                return 'Not CSRF protected'
        """
        if isinstance(view, flask.Blueprint):
            cls._exempt_blueprints.add(view.name)
        else:
            cls._exempt_views.add('{v.__module__}.{v.__name__}'.format(v=view))

        return view
