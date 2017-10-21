import wget
import yaml
from keras.models import model_from_json
import os
import numpy as np


def download_config(config_file_url):
    config_filename = wget.download(config_file_url)
    with open(config_filename, 'r') as conf_file:
        conf = yaml.load(conf_file)
    os.remove(config_filename)
    return conf


def download_models(models_urls, weights_urls, models_infos):
    return [__init_mdl(__downl_mdl(m, w), i['nb_letters'], i['nb_possible_chars'])
            for m, w, i in zip(models_urls, weights_urls, models_infos)]


def __downl_mdl(model_url, weights_url):
    weights_filename = wget.download(weights_url)
    model_filename = wget.download(model_url)
    with open(model_filename, 'r') as f:
        model = model_from_json(f.read())
    model.load_weights(weights_filename)
    os.remove(weights_filename)
    os.remove(model_filename)
    return model


def __init_mdl(model, nb_letters, nb_possible_chars):
    _ = model.predict(np.asarray([np.zeros((nb_letters, nb_possible_chars))]))[0]
    return model
