from keras.models import model_from_json


def save_model(model, model_path='../dnn.json'):
    # serialize model to JSON
    model_json = model.to_json()
    with open(model_path, "w") as json_file:
        json_file.write(model_json)
    print("Saved model to disk")
    return 0


def save_model_weights(model, model_weights_path='../dnn.h5'):
    # serialize weights to HDF5
    model.save_weights(model_weights_path)
    print("Saved model weights to disk")
    return 0


def load_model(model_path):
    # load json and create model
    json_file = open(model_path, 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    loaded_model = model_from_json(loaded_model_json)
    return loaded_model


def load_model_weights(weights_path, model):
    # load weights into  model
    model.load_weights(weights_path)
    print("Loaded model from disk")
    return model