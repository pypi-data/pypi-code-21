import posixpath

# Misc rubbish
SITE_ID = 1
DEFAULT_PER_PAGE = 20

# Sites built on coop all share a common URL structure and WSGI application
ROOT_URLCONF = 'coop.urls'
WSGI_APPLICATION = 'coop.wsgi.application'


# URLs for assets
ASSETS_URL = '/assets/'
MEDIA_URL = posixpath.join(ASSETS_URL, 'media/')
STATIC_URL = posixpath.join(ASSETS_URL, 'static/')


# What is installed by default
INSTALLED_APPS = [
    'coop',

    # Third party apps
    'taggit',
    'modelcluster',
    'wagtailmetadata',
    'wagtailaccessibility',
    'wagtailfontawesome',

    # Django apps
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.sitemaps.views',

    # Wagtail apps
    'wagtail.wagtailcore',
    'wagtail.wagtailadmin',
    'wagtail.wagtaildocs',
    'wagtail.wagtailsnippets',
    'wagtail.wagtailsites',
    'wagtail.wagtailusers',
    'wagtail.wagtailimages',
    'wagtail.wagtailembeds',
    'wagtail.wagtailsearch',
    'wagtail.wagtailredirects',
    'wagtail.contrib.settings',
    'wagtail.contrib.table_block',
]


# Localisation - most sites are Australian
TIME_ZONE = 'Australia/Hobart'
LANGUAGE_CODE = 'en-au'

USE_I18N = True
USE_L10N = False
USE_TZ = True


# Standard middleware required by Wagtail
MIDDLEWARE_CLASSES = [
    'bugsnag.django.middleware.BugsnagMiddleware',

    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'wagtail.wagtailcore.middleware.SiteMiddleware',
    'wagtail.wagtailredirects.middleware.RedirectMiddleware',
]


# Wagtail uses Django templates, but we use Jinja templates.
# Some common Jinja extensions are used that cover most use-cases we need.
TEMPLATES_DJANGO = {
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            'django.contrib.auth.context_processors.auth',
            'django.template.context_processors.debug',
            'django.template.context_processors.i18n',
            'django.template.context_processors.media',
            'django.template.context_processors.static',
            'django.template.context_processors.tz',
            'django.contrib.messages.context_processors.messages',
            'django.template.context_processors.request',
            'wagtail.contrib.settings.context_processors.settings',
        ]
    }
}
TEMPLATES_JINJA = {
    'BACKEND': 'django.template.backends.jinja2.Jinja2',
    'APP_DIRS': True,
    'OPTIONS': {
        'extensions': [
            'wagtail.wagtailcore.jinja2tags.core',
            'wagtail.wagtailadmin.jinja2tags.userbar',
            'wagtail.wagtailimages.jinja2tags.images',
            'wagtail.contrib.settings.jinja2tags.settings',
            'coop.jinja2tags.core.Extension',
            'wagtailaccessibility.jinja2tags.tota11y',
            'wagtailmetadata.jinja2tags.WagtailMetadataExtension',
        ],
    },
}

TEMPLATES = [TEMPLATES_DJANGO, TEMPLATES_JINJA]


# Who to email when things break
ADMINS = [
    ('Django debug', 'django@takeflight.com.au'),
]
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
        'bugsnag_filter': {
            '()': 'coop.logging.RequireNoBugsnagSetting'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false', 'bugsnag_filter'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
    }
}
