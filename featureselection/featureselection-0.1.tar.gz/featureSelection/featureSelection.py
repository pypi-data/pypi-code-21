import warnings
warnings.filterwarnings("ignore")
import pandas as pd
import numpy as np
import operator

class featureSelector(object):

    """Hybrid feature importance for feature selection.
    Parameters
    ----------
    model : model instance
        Linear / tree - based model from sklearn.
    scorer : score function
        Ex.: accuracy(y_true, y_pred)
    cv : cross validation strategy instance
        Ex.: KFold(n_splits=5)
    prcnt : float, .0...1.0
        proportion of the features selected on every iteration
    to_keep : int
        minimal feature set length
    tol : float
        maximum difference between chosen feature set score and minimal score
    mode : string; 'reg' or 'class'
        specify type of model
    verbose : bool
        if True, prints out number of features vs. scores on the current iteration

    Returns
    -------
    feature sets : list of tuples
        all feature sets and scores
    best feature set : list
        feature set that satisfying the following condition:
            min(len(features)).score - min(score) <= tol
    """
    
    def __init__(self, model=None, scorer=None, cv=None, prcnt=0.8, to_keep=2, tol=0.05, mode='reg', verbose=False):

        self.mode = mode
        self.model = model
        self.verbose = verbose
        self.scorer = scorer
        self.prcnt = prcnt
        self.to_keep = to_keep
        self.tol = tol
        self.feature_sets = []
        self.best = None
        self.cv = cv

    def rank_pertrub(self, x, y):
        impt = np.zeros(x.shape[1])
        for i, col in enumerate(x.columns):
            hold = x[col]
            x[col] = x[col].sample(frac=1).values
            if self.mode == 'reg':
                score = self.scorer(y, self.model.predict(x))
            if self.mode == 'class':                
                score = self.scorer(y, self.model.predict_proba(x))
            impt[i] = score
            x[col] = hold
        impt /= np.sum(impt)
        return impt
        
    def fit(self, train, y_train):
        self.features = list(train.columns)
        self.scores = []
        trsh = int((self.to_keep / self.prcnt) * (1-self.prcnt) + self.to_keep)
        if trsh <= self.to_keep:
            trsh += 1
        while True:
            if len(self.features) >= trsh:
                score, importances, impt_pertrub, fold = 0, 0, 0, 1
                for train_index, test_index in self.cv.split(train, y_train):
                    self.model.fit(train[self.features].loc[train_index], y_train[train_index])
                    if self.mode == 'reg':
                        score += self.scorer(y_train[test_index], self.model.predict(train[self.features].loc[test_index]))
                    elif self.mode == 'class':
                        score += self.scorer(y_train[test_index], self.model.predict_proba(train[self.features].loc[test_index]))
                    try:
                        importances_std = np.std([tree.feature_importances_ for tree in self.model.estimators_], axis=0)
                        importances_std /= np.sum(importances_std)
                        importances_ = ((self.model.feature_importances_/np.sum(self.model.feature_importances_))*importances_std)
                    except: 
                        importances_ = abs(self.model.coef_[0])
                    importances += importances_ / np.sum(importances_)
                    impt_pertrub += self.rank_pertrub(train[self.features].loc[train_index], y_train[train_index])
                    fold += 1
                importances /= fold
                impt_pertrub /= fold                
                score /= fold
                d = np.std(impt_pertrub)
                importances += impt_pertrub * d
                importances /= np.sum(importances)
                self.scores.append(score)
                if self.verbose:
                    print(len(self.features), ' : ', score)
                sort_importances = sorted([(j,k) for j, k in zip(self.features, importances)], key=operator.itemgetter(1), reverse=True)
                self.feature_sets.append(sort_importances)
                self.features = [i[0] for i in sort_importances[:int(len(sort_importances) * self.prcnt)]]
            else:
                break
        min_ = min(self.scores)
        for score in self.scores[::-1]:
            if score != min_:
                if score < min_ or abs(score - min_) <= self.tol:
                    self.best = self.scores.index(score)
                    break
            else:
                self.best = self.scores.index(min_)

        self.best_features_importances = self.feature_sets[self.best]

    def transform(self, df):
        return df[[i[0] for i in self.feature_sets[self.best]]]
