import json

class Feature:
    """Class for feature representation
        name - feature's name
        param - param of classifier corresponding to feature
        value - feature's value
        weight - param * value
    """

    def __init__(self, name, param, value=1):
        self.name = name
        self.param = param
        self.value = value
        self.weight = param * value

    def __str__(self):
        return "\t%-30s\t\t%.4f\t%.4f\t%.4f" % (self.name, self.weight, self.param ,self.value)

    def __lt__(self, other):
        return self.weight < other.weight

    def __repr__(self):
        return json.dumps(self, default=lambda o: o.__dict__, indent=4)


class FeatureExploration:
    """Class for expolre features in model
        vectorizer, classifer, preprocessor - steps of model pipeline
            preprocessor: process text
            vectorizer: vectorize proceseed text
            classifer: classify vector
    """

    def __init__(self, vectorizer, classifer, preprocessor=None):
        self.vectorizer = vectorizer
        self.classifer = classifer
        self.preprocessor = preprocessor
        self.features = list(zip(vectorizer.get_feature_names(), classifer.coef_[0]))

    def find_features(self, text):
        """find features in text

        Args:
             text: raw text for analysis
        Returns:
            initial_text: preprocessed text
            features: finded features

        """
        finded_features = []
        if self.preprocessor:
            text = self.preprocessor.transform([text])[0]
        for feature_number, feature_coef in self.vectorizer.transform([text]).todok().items():
            finded_feature = self.features[feature_number[1]]
            finded_features.append(Feature(finded_feature[0], finded_feature[1], feature_coef))
        finded_features = sorted(finded_features, reverse=True)
        return {
            'initial_text': text,
            'features': finded_features
        }

    def show_features(self, text):
        """print finded features from text

        Args:
             text: raw text for analysis
        """
        rez = self.find_features(text)
        print(rez['initial_text'])
        for f in rez['features']:
            print(f)

    def show_most_informative_features(self, n=20):
        """print n most good and bad features of model

        Args:
             n: how many top features should be showed
        """
        feature_names = self.vectorizer.get_feature_names()
        coefs_with_fns = sorted(zip(self.classifer.coef_[0], feature_names))
        top = zip(coefs_with_fns[:n], coefs_with_fns[:-(n + 1):-1])
        for (coef_1, fn_1), (coef_2, fn_2) in top:
            print("\t%.4f\t%-15s\t\t%.4f\t%-15s" % (coef_1, fn_1, coef_2, fn_2))
