from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import VarianceThreshold
from sklearn.feature_selection import chi2


def removeLowVarianceFeatures(feature=[[1, 0, 1], [0, 1, 0]]):
    sel = VarianceThreshold(threshold=(.8 * (1 - .8)))
    feature = sel.fit_transform(feature)
    return feature


def selectKbestFeature(featureX, targetY, KbestNum):
    feature = SelectKBest(chi2, KbestNum).fit_transform(featureX, targetY)
    return feature


