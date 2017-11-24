"""
Base settings for Django templates.
"""

# Possible to change to another but all apps have to support that other one.
# For now is counted only with Bootstrap which has the biggest support.
# More info: https://github.com/aldryn/aldryn-boilerplates/
ALDRYN_BOILERPLATE_NAME = 'bootstrap3'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'OPTIONS': {
            'context_processors': [
                # Django's defaults.
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',  # Needed by Django CMS.

                # Django CMS's core context processors.
                'cms.context_processors.cms_settings',
                'sekizai.context_processors.sekizai',  # Static file management for template blocks.
                'aldryn_boilerplates.context_processors.boilerplate',  # Static file management for Aldryn Boilerplates.

                # Other Django's modules.
                'constance.context_processors.config',
            ],
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'aldryn_boilerplates.template_loaders.AppDirectoriesLoader',  # Loader of Aldryn Boilerplate templates.
                'django.template.loaders.app_directories.Loader',
            ],
        },
    },
]
