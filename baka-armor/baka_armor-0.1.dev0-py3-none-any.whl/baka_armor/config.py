import trafaret as T

CONFIG = T.Dict({
    T.Key('armor'):
        T.Dict({
            'ext': T.String(),
            'config': T.String(),
            'assets': T.String(),
            'bundles': T.String(),
            'url': T.String(),
            'manifest': T.String(),
            'debug': T.Bool(),
            'cache': T.Bool(),
            'auto_build': T.Bool(),
            'plim': T.Bool(),
        }),
})
