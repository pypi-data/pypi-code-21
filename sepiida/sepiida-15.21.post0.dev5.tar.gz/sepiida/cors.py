import re

from flask_cors import CORS

DEFAULT_EXPOSE_HEADERS = [
    'Location',
    'X-Sentry-ID',
]

def register_cors_handlers(app, domains=None, supports_credentials=False, expose_headers=None):
    expose_headers = expose_headers or DEFAULT_EXPOSE_HEADERS
    if not domains:
        return

    if not isinstance(domains, list):
        domains = [domains]

    origins = '|'.join([re.escape(domain) for domain in domains])
    origin_regex = r'(.*)?\.({0})$'.format(origins)

    app.config['CORS_RESOURCES'] = {
        r'/*': { "origins": origin_regex }
    }

    return CORS(
        app,
        supports_credentials=supports_credentials,
        expose_headers=expose_headers,
    )
