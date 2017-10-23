import h5py
from keras.utils.np_utils import to_categorical
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder


def class_encoder_to_number(tobe_Y):
    encoder = LabelEncoder()
    encoder.fit(tobe_Y)
    return encoder


def class_number_encode_to_one_hot_code(class_number):
    return to_categorical(class_number)


def one_hot_code_to_class_number_encode(one_hot_code):
    max_item = 0
    max_value = 0
    for item in range(len(one_hot_code)):
        if one_hot_code[item] > max_value:
            max_item = item
            max_value = one_hot_code[item]
    return max_item


def number_to_class_name(encoder, class_number):
    return encoder.inverse_transform(class_number)


def split_dataset_to_tain_test(X, Y, test_size=0.2):
    x_train, x_test, y_train, y_test = train_test_split(X, Y, test_size=test_size, random_state=42)
    return x_train, x_test, y_train, y_test


def load_train_test_data(path='../data/pythonTutorial4/setList_mfcc.h5'):
    hfile = h5py.File(path, 'r')
    X = hfile['X'][:]
    Y = hfile['Y'][:]
    encoder = class_encoder_to_number(Y)
    Y = encoder.transform(Y)
    Y = class_number_encode_to_one_hot_code(Y)
    x_train, x_test, y_train, y_test = train_test_split(X, Y, test_size=0.2, random_state=42)

    return x_train, y_train, x_test, y_test
