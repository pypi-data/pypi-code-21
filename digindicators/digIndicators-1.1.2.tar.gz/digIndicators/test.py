import pickle
import fasttext
from numpy import array


#load pre-trained fasttext bin model
model = fasttext.load_model('./indicator_data/fasttext_vec20_model.bin')

# load pre-trained incall model
filename_incall = './indicator_data/incall_model.sav'
loaded_model_incall = pickle.load(open(filename_incall, 'rb'))

# load pre-trained outcall model
filename_outcall = './indicator_data/outcall_model.sav'
loaded_model_outcall = pickle.load(open(filename_outcall, 'rb'))

# load pre-trained movement model
filename_movement = './indicator_data/movement_model.sav'
loaded_model_movement = pickle.load(open(filename_movement, 'rb'))

# load pre-trained multi model
filename_multi = './indicator_data/multi_model.sav'
loaded_model_multi = pickle.load(open(filename_multi, 'rb'))

# load pre-trained risky model
filename_risky = './indicator_data/risky_model.sav'
loaded_model_risky = pickle.load(open(filename_risky, 'rb'))



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











