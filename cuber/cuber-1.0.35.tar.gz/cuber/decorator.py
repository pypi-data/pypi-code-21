from cuber import cube
import copy
import inspect

def to_cube(**cube_static_params):
    for key in cube_static_params.keys():
        assert key in {'immutable_args', 'restorable', 'version'}
    def to_cube_spec(fn):
        class CubeTmp(cube.Cube):
            def __init__(self, **kwargs):
                kwargs = copy.deepcopy(kwargs)
                possible_args = inspect.getargspec(f)[0]
                for key in kwargs:
                    if key not in possible_args:
                        raise ValueError('Argument "{}" is passed, but cube can accept only these arguments: {}'.format(key, kwargs))

                for possible_arg in possible_args:
                    if possible_arg not in kwargs:
                        kwargs[possible_arg] = None

                self.__dict__ = kwargs

            def eval(self):
                return fn(**self.__dict__)
        CubeTmp.__name__ = fn.__name__
        for key, value in cube_static_params.iteritems():
            setattr(CubeTmp, key, value)
        return CubeTmp
    return to_cube_spec
