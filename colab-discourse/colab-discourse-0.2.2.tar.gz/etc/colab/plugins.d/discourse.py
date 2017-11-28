name = 'colab_discourse'
verbose_name = 'Colab Discourse Plugin Plugin'

upstream = 'http://127.0.0.1:8080/expressao/'
api_key = 'api_key'
api_username = 'system'
sso_secret = 'sso_secret'

urls = {
    'include': 'colab_discourse.urls',
    'prefix': '^expressao/',
    'login': '/expressao/accounts/login/',
}

settings_variables = {
    'COLAB_STATICS': [
        '/colab-plugins/discourse/src/colab_discourse/static'
    ]
}
