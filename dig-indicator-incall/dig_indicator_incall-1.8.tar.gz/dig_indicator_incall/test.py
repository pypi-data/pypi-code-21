import pickle
import fasttext
from numpy import array


#load pre-trained fasttext bin model
model = fasttext.load_model('./model/fasttext_vec20_model.bin')

# load pre-trained incall model
filename_incall = './model/incall_model.sav'
loaded_model_incall = pickle.load(open(filename_incall, 'rb'))

# load pre-trained outcall model
filename_outcall = './model/outcall_model.sav'
loaded_model_outcall = pickle.load(open(filename_outcall, 'rb'))

# load pre-trained movement model
filename_movement = './model/movement_model.sav'
loaded_model_movement = pickle.load(open(filename_movement, 'rb'))

# load pre-trained multi model
filename_multi = './model/multi_model.sav'
loaded_model_multi = pickle.load(open(filename_multi, 'rb'))

# load pre-trained risky model
filename_risky = './model/risky_model.sav'
loaded_model_risky = pickle.load(open(filename_risky, 'rb'))



def incall_predict_prob(vector_array):
    dic = {}
    dic['value'] = "incall"
    dic['score'] = float(loaded_model_incall.predict_proba(vector_array)[:, -1])
    print  float(loaded_model_incall.predict_proba(vector_array)[:, 0])
    return dic

def outcall_predict_prob(vector_array):
    dic = {}
    dic['value'] = "outcall"
    dic['score'] = float(loaded_model_outcall.predict_proba(vector_array)[:, -1])
    return dic


def movement_predict_prob(vector_array):
    dic = {}
    dic['value'] = "movement"
    dic['score'] = float(loaded_model_movement.predict_proba(vector_array)[:, -1])
    return dic

def multi_predict_prob(vector_array):
    dic = {}
    dic['value'] = "multi_girls"
    dic['score'] = float(loaded_model_multi.predict_proba(vector_array)[:, -1])
    return dic


def risky_predict_prob(vector_array):
    dic = {}
    dic['value'] = "risky_activity"
    dic['score'] = float(loaded_model_risky.predict_proba(vector_array)[:, -1])
    return dic


def rawInputTest():
    x = raw_input("Input: ")
    return x


if __name__ == "__main__":

    # text = raw_input("Input:")

    while (True):
        text = rawInputTest()
        text_vector = array(model[text])
        vector_array = text_vector.reshape(1, -1) # it is a single sample
        print vector_array

        result_lst = []
        result_lst.append(incall_predict_prob(vector_array))
        result_lst.append(outcall_predict_prob(vector_array))
        result_lst.append(movement_predict_prob(vector_array))
        result_lst.append(multi_predict_prob(vector_array))
        result_lst.append(risky_predict_prob(vector_array))
        print result_lst








