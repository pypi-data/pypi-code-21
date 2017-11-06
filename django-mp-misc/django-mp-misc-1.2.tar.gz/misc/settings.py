import os
import sys
import socket


def get_settings_class():

    host = socket.gethostbyname(socket.gethostname())

    class_name = 'TestSettings' if 'test' in sys.argv else 'Settings'

    file_name = 'local' if host == '127.0.0.1' else 'server'

    return 'core.settings.{}.{}'.format(file_name, class_name)


class HostsSettingsMixin(object):

    ROOT_HOSTCONF = 'core.hosts'

    DEFAULT_HOST = 'root'

    @property
    def INSTALLED_APPS(self):
        return super(HostsSettingsMixin, self).INSTALLED_APPS + [
            'django_hosts',
        ]

    @property
    def MIDDLEWARE(self):
        return super(HostsSettingsMixin, self).MIDDLEWARE + [
            'django_hosts.middleware.HostsRequestMiddleware'
        ]


class BowerSettingsMixin(object):

    @property
    def INSTALLED_APPS(self):
        return super(BowerSettingsMixin, self).INSTALLED_APPS + [
            'djangobower'
        ]

    @property
    def STATICFILES_FINDERS(self):
        return super(BowerSettingsMixin, self).STATICFILES_FINDERS + [
            'djangobower.finders.BowerFinder'
        ]

    @property
    def BOWER_COMPONENTS_ROOT(self):
        return os.path.join(self.BASE_DIR, 'static')


class PipelineSettingsMixin(object):

    STATICFILES_STORAGE = 'pipeline.storage.PipelineStorage'

    @property
    def INSTALLED_APPS(self):
        return super(PipelineSettingsMixin, self).INSTALLED_APPS + [
            'pipeline'
        ]

    @property
    def STATICFILES_FINDERS(self):
        return super(PipelineSettingsMixin, self).STATICFILES_FINDERS + [
            'pipeline.finders.PipelineFinder',
        ]


class CaptchaSettingsMixin(object):

    NOCAPTCHA = True

    @property
    def INSTALLED_APPS(self):
        return super(CaptchaSettingsMixin, self).INSTALLED_APPS + [
            'captcha'
        ]


class DebugToolbarSettingsMixin(object):

    INTERNAL_IPS = ['127.0.0.1']

    @property
    def INSTALLED_APPS(self):
        return super(DebugToolbarSettingsMixin, self).INSTALLED_APPS + [
            'debug_toolbar',
        ]

    @property
    def MIDDLEWARE(self):
        return super(DebugToolbarSettingsMixin, self).MIDDLEWARE + [
            'debug_toolbar.middleware.DebugToolbarMiddleware'
        ]


class PaginationSettingsMixin(object):

    PAGINATION_SETTINGS = {
        'PAGE_RANGE_DISPLAYED': 5,
        'MARGIN_PAGES_DISPLAYED': 2,
        'SHOW_FIRST_PAGE_WHEN_INVALID': True
    }

    @property
    def INSTALLED_APPS(self):
        return super(PaginationSettingsMixin, self).INSTALLED_APPS + [
            'pure_pagination'
        ]


class CKEditorSettingsMixin(object):

    CKEDITOR_UPLOAD_PATH = 'uploads/'

    @property
    def INSTALLED_APPS(self):
        return super(CKEditorSettingsMixin, self).INSTALLED_APPS + [
            'ckeditor',
            'ckeditor_uploader'
        ]


class OpbeatSettingsMixin(object):

    OPBEAT = {
        'ORGANIZATION_ID': '',
        'APP_ID': '',
        'SECRET_TOKEN': '',
    }

    @property
    def INSTALLED_APPS(self):
        return super(OpbeatSettingsMixin, self).INSTALLED_APPS + [
            'opbeat.contrib.django'
        ]

    @property
    def MIDDLEWARE(self):
        return super(OpbeatSettingsMixin, self).MIDDLEWARE + [
            'opbeat.contrib.django.middleware.OpbeatAPMMiddleware'
        ]


class DjangoSettingsMixin(object):

    ROOT_URLCONF = 'core.urls'

    WSGI_APPLICATION = 'core.wsgi.application'

    AUTH_PASSWORD_VALIDATORS = [
        {
            'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
        },
        {
            'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        },
        {
            'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
        },
        {
            'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
        },
    ]

    TIME_ZONE = 'UTC'

    USE_I18N = True

    USE_L10N = True

    USE_TZ = True

    SITE_ID = 1

    STATIC_URL = '/static/'

    MEDIA_URL = '/media/'

    @property
    def MIDDLEWARE(self):
        return [
            'django.middleware.security.SecurityMiddleware',
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.common.CommonMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.middleware.locale.LocaleMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
            'django.middleware.clickjacking.XFrameOptionsMiddleware',
            'misc.middleware.WWWRedirectMiddleware'
        ]

    @property
    def STATIC_ROOT(self):
        return os.path.join(self.BASE_DIR, 'static-collect')

    @property
    def MEDIA_ROOT(self):
        return os.path.join(self.BASE_DIR, 'media')

    @property
    def STATICFILES_DIRS(self):
        return [os.path.join(self.BASE_DIR, 'static')]

    @property
    def LOCALE_PATHS(self):
        return [os.path.join(self.BASE_DIR, 'locale')]
