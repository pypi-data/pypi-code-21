name = 'colab_audiencias'
verbose_name = 'Colab Audiencias Plugin Plugin'

upstream = 'http://127.0.0.1:7000/audiencias/'
api_key = 'api_key'

urls = {
    'include': 'colab_audiencias.urls',
    'prefix': '^audiencias/',
    'login': '/audiencas/accounts/login/',
}
