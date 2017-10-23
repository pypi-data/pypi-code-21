import pickle
import fasttext
from numpy import array
import os
import codecs
import requests


# /tmp/dig-indicator-model/<version>/<file_name>

# model_dir = '/tmp/dig-indicator-model'
# model_version = 'master'
# dir_path = os.path.join(model_dir, model_version)
# url_prefix = 'https://github.com/usc-isi-i2/dig3-resources/raw/{}/indicator_data/{}'

# if not os.path.exists(dir_path):
#     os.makedirs(dir_path)

# def download_if_not_exists(file_name):

#     file_path = os.path.join(dir_path, file_name)
#     if os.path.exists(file_path):
#         return file_path

#     url = url_prefix.format(model_version, file_name)
#     resp = requests.get(url)
#     with codecs.open(file_path, 'wb') as output:
#         output.write(resp.content)
#     return file_path

#load pre-trained fasttext bin model
model = None
loaded_model_incall = None
loaded_model_outcall = None
loaded_model_movement = None
loaded_model_multi = None
loaded_model_risky = None
# # load pre-trained outcall model
# filename_outcall = download_if_not_exists('outcall_model.sav')
# loaded_model_outcall = pickle.load(open(filename_outcall, 'rb'))

# # load pre-trained movement model
# filename_movement = download_if_not_exists('movement_model.sav')
# loaded_model_movement = pickle.load(open(filename_movement, 'rb'))

# # load pre-trained multi model
# filename_multi = download_if_not_exists('multi_model.sav')
# loaded_model_multi = pickle.load(open(filename_multi, 'rb'))

# # load pre-trained risky model
# filename_risky = download_if_not_exists('risky_model.sav')
# loaded_model_risky = pickle.load(open(filename_risky, 'rb'))

#load models
def load_fasttext_vec20_model(path):
    global model
    model = fasttext.load_model(path)

def load_model_incall(path):
    global loaded_model_incall
    loaded_model_incall = pickle.load(open(path, 'rb'))

def load_model_outcall(path):
    global loaded_model_outcall
    loaded_model_outcall = pickle.load(open(path, 'rb'))

def load_model_movement(path):
    global loaded_model_movement
    loaded_model_movement = pickle.load(open(path, 'rb'))

def load_model_multi(path):
    global loaded_model_multi
    loaded_model_multi = pickle.load(open(path, 'rb'))

def load_model_risky(path):
    global loaded_model_risky
    loaded_model_risky = pickle.load(open(path, 'rb'))

# indicator domain functions
def incall(text):
    text_vector = array(model[text])
    vector_array = text_vector.reshape(1, -1)  # it is a single sample
    dic = {}
    dic['value'] = "incall"
    dic['score'] = float(loaded_model_incall.predict_proba(vector_array)[:, -1])
    return dic

def outcall(text):
    text_vector = array(model[text])
    vector_array = text_vector.reshape(1, -1)  # it is a single sample
    dic = {}
    dic['value'] = "outcall"
    dic['score'] = float(loaded_model_outcall.predict_proba(vector_array)[:, -1])
    return dic


def movement(text):
    text_vector = array(model[text])
    vector_array = text_vector.reshape(1, -1)  # it is a single sample
    dic = {}
    dic['value'] = "movement"
    dic['score'] = float(loaded_model_movement.predict_proba(vector_array)[:, -1])
    return dic

def multi(text):
    text_vector = array(model[text])
    vector_array = text_vector.reshape(1, -1)  # it is a single sample
    dic = {}
    dic['value'] = "multi_girls"
    dic['score'] = float(loaded_model_multi.predict_proba(vector_array)[:, -1])
    return dic


def risky(text):
    text_vector = array(model[text])
    vector_array = text_vector.reshape(1, -1)  # it is a single sample
    dic = {}
    dic['value'] = "risky_activity"
    dic['score'] = float(loaded_model_risky.predict_proba(vector_array)[:, -1])
    return dic

def indicators(text):
    result_lst = []
    result_lst.append(incall(text))
    result_lst.append(outcall(text))
    result_lst.append(movement(text))
    result_lst.append(multi(text))
    result_lst.append(risky(text))
    return result_lst











