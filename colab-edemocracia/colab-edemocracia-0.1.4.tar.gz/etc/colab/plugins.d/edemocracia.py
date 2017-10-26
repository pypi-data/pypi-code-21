name = 'colab_edemocracia'
verbose_name = 'Colab eDemocracia Plugin'

urls = {
    'include': 'colab_edemocracia.urls',
    'prefix': '',
    'namespace': 'colab_edemocracia',
    'login': '/home'
}

middlewares = ['colab_edemocracia.middlewares.ForceLangMiddleware']

dependencies = ['djangobower', 'compressor', 'easy_thumbnails',
                'image_cropping', 'widget_tweaks']

settings_variables = {
    'STATICFILES_FINDERS': (
        'djangobower.finders.BowerFinder',
        'compressor.finders.CompressorFinder',
    ),
    'BOWER_COMPONENTS_ROOT':
        '/colab-plugins/edemocracia/src/colab_edemocracia/static',
    'BOWER_INSTALLED_APPS': (
        'foundation-sites#6.2.3',
        'jquery-mask-plugin',
        'https://github.com/labhackercd/fontastic-labhacker.git',
    ),
    'COMPRESS_PRECOMPILERS': (
        ('text/x-scss', 'django_libsass.SassCompiler'),
    ),
    'LIBSASS_SOURCEMAPS': 'DEBUG',
    'COMPRESS_ROOT': "/colab-plugins/edemocracia/src/colab_edemocracia/static",
    'COLAB_TEMPLATES': (
        "/colab-plugins/edemocracia/src/colab_edemocracia/templates",
    ),
    'COLAB_STATICS': [
        '/colab-plugins/edemocracia/src/colab_edemocracia/static'
    ]
}
