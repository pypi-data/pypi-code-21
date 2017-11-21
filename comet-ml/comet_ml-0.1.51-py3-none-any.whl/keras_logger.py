import sys

from comet_ml import config


def fit_logger(real_fit):
    def wrapper(*args, **kwargs):
        if (config.experiment):
            callback = config.experiment.keras_callback()
            if 'callbacks' in kwargs and kwargs['callbacks'] is not None:
                kwargs['callbacks'].append(callback)
            else:
                kwargs['callbacks'] = [callback]

        return real_fit(*args, **kwargs)

    return wrapper


def patch():
    if sys.version_info[0] >= 3:
        from comet_ml import class_loader_py3
        sys.meta_path.insert(0, class_loader_py3.Finder('keras.models', "fit", fit_logger,
                                   class_name="Model"))
    else:
        from comet_ml import class_loader_py2
        sys.meta_path.insert(0, class_loader_py2.Finder('keras',"models", "Model", "fit", fit_logger))


if "keras" in sys.modules:
    raise SyntaxError("Please import Comet before importing any keras modules")

patch()

