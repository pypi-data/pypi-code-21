import os
from binaryornot.check import is_binary
import logging
log = logging.getLogger('qordoba')

from sklearn.pipeline import Pipeline
from sklearn import naive_bayes as nb
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.externals import joblib
import datetime

classifier_model = None

# class Strategy():
#     strategy_name = ''
#
#     def  __init__(self):
#         pass

class Classifier():
    # multi -class problem
    def __init__(self):
        self.strategy_name = 'classifier'

    def train(self):
        pipeline = Pipeline([
            ('vectorizer', CountVectorizer(ngram_range=(3, 5))),
            ('classifier', nb.MultinomialNB())])

        X_train = []
        y_train = []

        # Reading samples as training data
        samples_path = self.get_data('resources/samples')
        for subdir, _, files in os.walk(samples_path):
            if '/'.join(subdir.split('/')[-2:]) == "resources/samples":
                print
                "skip" + subdir
                continue

            lang = subdir.split(os.sep)[-1]

            for f in files:
                if '.DS_Store' in str(f):
                    pass
                elif is_binary(subdir + "/" + f):
                    pass
                else:
                    y_train.append(lang)
                    with open(subdir + "/" + f, "r") as lang_file:
                        X_train.append(lang_file.read())

        time = datetime.datetime.now()
        log.info("-- Start --  training model \n this can take some time (now:{})".format(time))

        pipeline.fit(X_train, y_train)

        log.info("-- Done training. Training time:{}".format(datetime.datetime.now() - time))
        timenew = datetime.datetime.now()

        filename = '../resources/finalized_model.joblib.pkl'
        _ = joblib.dump(pipeline, filename, compress=9)

        log.info("-- Saved trained model to finalized_model (time:{})".format(datetime.datetime.now() - timenew))
        return pipeline

    def predict(self, blob):
        global classifier_model
        if not classifier_model:
            finalized_model_path = self.get_data('resources/finalized_model.joblib.pkl')
            filename = finalized_model_path
            classifier_model = joblib.load(filename)
            log.info('Model loaded')

        time = datetime.datetime.now()
        log.info("Starting prediction")

        Examples = []
        Files = [blob, finalized_model_path]

        for file_ in Files:
            if is_binary(file_):
                pass
            else:
                with open(file_, "r") as src_file_:
                    Examples.append(src_file_.read())

        predict_examples = classifier_model.predict(Examples)

        log.info("Finished with prediction within {} ".format(datetime.datetime.now() - time))
        log.info("predict_examples {} ".format(predict_examples))

        return predict_examples

    def find_type(self, blob):
        finalized_model_path = self.get_data('resources/finalized_model.joblib.pkl')
        if os.path.exists(finalized_model_path):
            log.info("finalized model exists. \n Starting prediction")
            predictions = self.predict(blob)
            return str(predictions[0])
        else:
            open(finalized_model_path, 'w')
            self.train()
            log.info("Training done. Starting prediction")
            predictions = self.predict(blob)
            return str(predictions[0])