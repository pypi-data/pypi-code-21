#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 18 16:29:59 2017

@author: robin
"""

from sklearn.ensemble import VotingClassifier
from sk_postal import sk_postal
from ft_model import sk_ft


clf=sk_postal()
clf=sk_ft()

eclf1=VotingClassifier(estimators=[('sk',clf),('sk2',clf2)])

eclf1.fit(val,y)

eclf


from sklearn.base import BaseEstimator, ClassifierMixin
from pyfasttext import FastText


class addr_voting(BaseEstimator, ClassifierMixin):
    postal_clf=sk_postal()
    ft_clf=sk_ft()
    def __init__(self, classifiers=[('postal',postal_clf),('ft',ft_clf)]):
        self.model =VotingClassifier(estimators=classifiers)


    def fit(self, X, y):
        self.model.fit(X,y)
        return self

    def predict(self, X):
        results = []
        if isinstance(X, str):  #
            results = results + [self.model.predict_single(X)]
        elif type(X) == list:
            results = results + self.model.predict(X)
        return results

    def predict_proba(self,X):
        results = []
        if isinstance(X, str):  #
            results = results + [self.model.predict_single(X)]
        elif type(X) == list:
            results = results + self.model.predict(X)
        return results


def score(self, X, y=None):
    return sum(self.predict(X))
