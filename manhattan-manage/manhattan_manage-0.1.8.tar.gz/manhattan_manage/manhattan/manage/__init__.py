import os

import flask
import jinja2
import pytz

from manhattan.assets import Asset
from manhattan import formatters
from manhattan.mail import EmailTemplate

from . import utils

__all__ = ['Manage']


class Manage:
    """
    The `Manage` class provides the initialization code for the package.
    """

    def __init__(self, app):
        self._app = app

        # Set-up a hidden blueprint to provide access to the templates
        blueprint = flask.Blueprint(
            '_manhattan_manage',
            __name__,
            template_folder='templates'
            )
        self._app.register_blueprint(blueprint)

        # Add filters and functions required by the manage templates

        # If a timezone has been set for the app then we use the timezone to
        # create a filter that is timezone aware.
        humanize_datetime = formatters.dates.humanize_datetime
        if 'TIMEZONE' in app.config:
            humanize_datetime = humanize_datetime_tz

        self._app.jinja_env.filters.update({
            'humanize_date': formatters.dates.humanize_date,
            'humanize_datetime': humanize_datetime,
            'humanize_duration': formatters.dates.humanize_duration,
            'humanize_status': formatters.text.humanize_status,
            'humanize_timediff': formatters.dates.humanize_timediff,
            'price': formatters.currency.price,
            'text_to_html': formatters.text.text_to_html,
            'yes_no': formatters.text.yes_no
            })

        # Make the template context available in the template
        @jinja2.contextfunction
        def get_context(c):
            return c

        self._app.jinja_env.globals['get_context'] = get_context

        # Set up common error handlers
        @app.errorhandler(404)
        def not_found(err):
            return (
                flask.render_template(
                    'manhattan/manage/errors/40X.html',
                    error=err
                ),
                404
            )

        @app.errorhandler(500)
        def server_error(err):
            return (
                flask.render_template(
                    'manhattan/manage/errors/500.html',
                    error=err
                ),
                500
            )

    def send_email(
        self,
        to,
        subject,
        template_path,
        sender=None,
        template_map=None,
        css=None,
        recipient_vars=None,
        global_vars=None,
        cc=None,
        bcc=None,
        attachments=None,
        headers=None,
        format='html',
        encoding='utf-8'
        ):
        """
        Manhattan manage provides a standard email template for sending emails
        to site administrators. This method provides a short-cut for sending
        manage emails.
        """

        assert self._app.mailer, 'No mailer configured'

        config = self._app.config
        env = self._app.jinja_env
        loader = self._app.jinja_env.loader

        # Set the base URL
        base_url = '{0}://{1}'.format(
            config.get('PREFERRED_URL_SCHEME', ''),
            config.get('SERVER_NAME', '')
            )

        # Set the sender
        sender = sender or config.get(
            'EMAIL_FROM',
            'no-reply@' + config.get('SERVER_NAME', '')
            )

        # Build a base template map
        merged_template_map = {}

        # Add common files
        merged_template_map['base'] = loader.get_source(
            env, 'manhattan/manage/emails/base.html')[0]
        merged_template_map['components'] = loader.get_source(
            env, 'manhattan/manage/emails/components.html')[0]

        # Add any passed template map
        merged_template_map.update(template_map or {})

        # Add common global vars
        logo_url = config.get('EMAIL_LOGO_PATH', '/images/logo-inverted.svg')
        if 'get_static_asset' in env.globals:
            logo_url = env.globals['get_static_asset'](logo_url)

        site_url = '{scheme}://{name}'.format(
            scheme=config.get('PREFERRED_URL_SCHEME', 'http'),
            name=config.get('SERVER_NAME', '')
            )

        merged_global_vars = {
            'logo_url': logo_url,
            'project_name': config.get('PROJECT_NAME', ''),
            'site_url': site_url
            }
        merged_global_vars.update(global_vars or {})

        # Add the requested file
        if not template_map:
            template_name = os.path.splitext(os.path.basename(template_path))[0]
            template = loader.get_source(env, template_path)[0]
            merged_template_map[template_name] = template
            template_path = template_name

        # Set the CSS
        if not css:
            css_path = config.get(
                'EMAIL_CSS_PATH',
                os.path.join(
                    self._app.root_path,
                    'webpack/manage/emails/manage.css'
                    )
                )
            if os.path.exists(css_path):
                with open(css_path) as f:
                    css = f.read()
            else:
                # If not set CSS as empty
                css = ''

        # Build the template
        template = ManageEmailTemplate(
            to,
            sender,
            subject,
            template_path,
            template_map=merged_template_map,
            css=css,
            recipient_vars=recipient_vars,
            global_vars=merged_global_vars,
            cc=cc,
            bcc=bcc,
            attachments=attachments,
            headers=headers,
            base_url=base_url,
            format=format,
            encoding=encoding
            )

        self._app.mailer.send(template)


# Utils

class ManageEmailTemplate(EmailTemplate):
    """
    Email template for the manage environment.
    """

    def get_jinja_env(self):
        # Return the environment for the manage app
        manage_app = utils.get_app(flask.current_app._dispatcher)
        return manage_app.jinja_env


def humanize_datetime_tz(dt, *args, **kwargs):
    """A version of `humzanize_datetime` that is timezone aware"""
    if isinstance(dt, str):
        dt = formatters.dates.str_to_datetime(dt)

    timezone = pytz.timezone(flask.current_app.config['TIMEZONE'])
    if dt.tzinfo:
        dt = dt.astimezone(timezone)
    else:
        # We assume that timezone naive datetimes are UTC
        dt = pytz.utc.localize(dt)
        dt = dt.astimezone(timezone)

    return formatters.dates.humanize_datetime(dt, *args, **kwargs)
