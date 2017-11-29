from django.conf import settings

def setting(name, default):
    @property
    def fn(self):
        return getattr(settings, 'EMAIL_%s' % name, default)
    return fn

class AppSettings(object):
    # Coffin users should use `coffin.template.loader.render_to_string`.
    RENDER_METHOD = setting('RENDER_METHOD', 'django.template.loader.render_to_string')

    CONTEXT_PROCESSORS = setting('CONTEXT_PROCESSORS', (
        'email_from_template.context_processors.debug',
        'email_from_template.context_processors.django_settings',
    ))

app_settings = AppSettings()
