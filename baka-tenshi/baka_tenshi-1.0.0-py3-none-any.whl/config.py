import trafaret as T

CONFIG = T.Dict({
    T.Key('tenshi'):
        T.Dict({
            T.Key('inject', default=False, optional=True): T.Bool(),
            T.Key('should_create_all', default=False, optional=True): T.Bool(),
            T.Key('should_drop_all', default=False, optional=True): T.Bool(),
        }),
})
