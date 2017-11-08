from colab.plugins.views import ColabProxyView


class ColabDiscoursePluginProxyView(ColabProxyView):
    app_label = 'colab_discourse'
    diazo_theme_template = 'proxy/discourse.html'
