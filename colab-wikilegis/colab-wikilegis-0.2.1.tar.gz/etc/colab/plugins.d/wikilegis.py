name = 'colab_wikilegis'
verbose_name = 'Colab Wikilegis Plugin Plugin'

upstream = 'http://127.0.0.1:9000/'

api_key = 'api_key'

urls = {
    'include': 'colab_wikilegis.urls',
    'prefix': '^wikilegis/',
    'login': '/wikilegis/accounts/login/',
}

settings_variables = {
    'COLAB_STATICS': [
        '/colab-plugins/wikilegis/src/colab_wikilegis/static'
    ]
}
