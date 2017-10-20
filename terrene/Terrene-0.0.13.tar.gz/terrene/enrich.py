from .apps import BaseApp, BaseAppManager
from coreapi.utils import File
import json



class ModelOptimizer:
    keys = []

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            self.keys.append(key)
            setattr(self, key, value)

    def __call__(self):
        return {key: getattr(self, key) for key in self.keys}


class ModelType:
    mean_absolute_error = 'mean_absolute_error'
    mean_squared_error = 'mean_squared_error'
    mean_absolute_percentage_error = 'mean_absolute_percentage_error'
    mean_squared_logarithmic_error = 'mean_squared_logarithmic_error'
    squared_hinge = 'squared_hinge'
    hinge = 'hinge'
    categorical_hinge = 'categorical_hinge'
    logcosh = 'logcosh'
    categorical_crossentropy = 'categorical_crossentropy'
    sparse_categorical_crossentropy = 'sparse_categorical_crossentropy'
    binary_crossentropy = 'binary_crossentropy'
    kullback_leibler_divergence = 'kullback_leibler_divergence'
    poisson = 'poisson'
    cosine_proximity = 'cosine_proximity'

    regression = mean_squared_error
    classification = binary_crossentropy


class ModelRuntime:
    keras = 'keras'
    tensorflow = 'tensorflow'
    caffe2 = 'caffe2'
    pytorch = 'pytorch'
    theano = 'theano'
    torch = 'torch'

    default = keras


class PredictiveModel(BaseApp):
    def train(self, transfer, epochs=100, loss=ModelType.regression,
              runtime=ModelRuntime.default, optimizer=ModelOptimizer(type='adam')):
        return self.act(['train'], {
            'object_id': self.object_id,
            'transfer': transfer.object_id,
            'epochs': epochs,
            'loss': loss,
            'optimizer': json.dumps(optimizer()),
            'runtime': runtime
        })

    def upload(self, accuracy, loss, file):
        file.seek(0)
        params = {
            'accuracy': accuracy, 'loss': loss, 'object_id': self.object_id,
            'file': File(self.object_id, file.read())}
        return self.act(['upload'], params)


class PredictiveModelManager(BaseAppManager):
    model = PredictiveModel
    namespace = ['enrich']
