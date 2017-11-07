
from itertools import chain
from collections import defaultdict

from scipy.stats import mode

import pandas as pd
import numpy as np

from ..compat import STRING_TYPES
from ..utils.crypto import ChineseCoding


class DataFramePipe(object):
    """ DataFrame processing pipeline

    此Pipe用于Machine learning过程中的特征处理，将操作串行化功能最小化
    """
    default_label_name = 'y'

    def __init__(self, data, label_name=None, file_type='json',
                 categorical_feats=None, numerical_feats=None, dummies_feats=None):
        """ DataFramePipe for pd.DataFrame processing

        :param data: string or `pandas.DataFrame`
                     if type is string, must be data file path
        :param label_name: the label column name
        :param file_type: support json or csv
        """
        if label_name is None:
            label_name = self.default_label_name

        self.label_name = label_name
        self.file_type = file_type

        self._df = data
        if isinstance(data, STRING_TYPES):
            self._df = pd.DataFrame()   # here consider use odo ???, load data to DataFrame

        if self.label_name in self._df.columns:
            self._y = pd.DataFrame(list(self._df[self.label_name]), index=self._df.index, columns=['tag'])  # ensure the same index
            self._df = self._df.drop([self.label_name], axis=1)

        self.categorical_feats = categorical_feats if categorical_feats else []
        self.numerical_feats = numerical_feats if numerical_feats else []
        self.dummies_feats = dummies_feats if dummies_feats else []

        self.missing_feats = []  # missing data features
        self.zero_feats = []     # zero data features

        self.classes_encode_ = {}

    @property
    def data(self):
        """ Return features data frame """
        if hasattr(self, '_y'):
            return pd.merge(self._df, self._y, left_index=True, right_index=True)

        return self._df

    @property
    def deleted_feature(self):
        return list(chain(*(self.missing_feats, self.zero_feats)))

    def set_feats(self, attribute, value):
        """ 设置属性

        Examples
        ========
        >>> import pandas as pd
        >>> pipe = DataFramePipe(pd.DataFrame([{}]))
        >>> pipe.set_feats('categorical_feats', ['a', 'b']).set_feats('numerical_feats', ['c'])
        """
        setattr(self, attribute, value)

        return self

    def find_missing_data(self):  # pragma: no cover
        total = self._df.isnull().sum().sort_values(ascending=False)
        percent = (self._df.isnull().sum() / self._df.isnull().count()).sort_values(ascending=False)

        return pd.concat([total, percent], axis=1, keys=['total', 'percent'])

    def drop_missing_data(self, null_criteria=0.25):
        """ Drop missing data """
        null_percents = (self._df.isnull().sum() / self._df.isnull().count())\
            .sort_values(ascending=False)

        self.missing_feats = null_percents[null_percents > null_criteria].index.tolist()

        self._df = self._df.drop(self.missing_feats, axis=1)

        return self

    def drop_high_zero_data(self, zero_criteria=0.75):
        """ Drop high zero data """
        columns = self._df.columns
        res = defaultdict(list)
        for column in columns:
            try:
                zero = self._df[column].value_counts()[0]
                percent = zero / self._df.shape[0]
            except Exception as e:
                zero = 0
                percent = 0

            res['zero'].append(zero)
            res['percent'].append(percent)

        zero_data = pd.DataFrame(res, index=columns).sort_values('percent', ascending=False)
        high_zero_data = zero_data[zero_data.percent > zero_criteria]
        self.zero_feats = high_zero_data.index.tolist()

        self._df = self._df.drop(self.zero_feats, axis=1)
        return self

    def classify_encode_conversion(self, encoded=None):
        """ 中文分类特征编码转换
        :param encoded  表示之前是否已经做过分类特征编码，传入之前分类的编码列表
            >>> encoded = {
            ...     "age": {
            ...         "男": "0",
            ...         "女": "1"
            ...     }
            ... }
        """
        if encoded is None:
            encoded = {}

        to_encode_feats = list(set(self.categorical_feats) - set(self.deleted_feature))
        for feat_name in to_encode_feats:
            feat_values = np.unique(self._df[feat_name].dropna())

            # 检测一下分类里是不是有中文
            if any(map(ChineseCoding.check_chinese, feat_values)):
                if encoded and encoded.get(feat_name):
                    # TODO there is a bug when a new category to join
                    self.classes_encode_[feat_name] = encoded[feat_name]
                else:
                    self.classes_encode_[feat_name] = \
                        {label: str(idx) for idx, label in enumerate(feat_values)}

                self._df[feat_name] = self._df[feat_name].map(self.classes_encode_[feat_name])

        return self

    def fill_na(self, fill_val=None):
        """ fill nan """
        if fill_val is None:
            fill_val = self._df.mean()

        self._df = self._df.fillna(fill_val)

        return self

    def one_hot_encoding(self):
        """ One hot encoding or dummy """
        self._df = pd.get_dummies(self._df)

        return self

    @classmethod
    def _fill_unknown_dummies(cls, col, raw_df=None):

        mode_result = mode(raw_df[col])
        mode_value = mode_result[0][0]
        return'%s_%s' % (col, str(mode_value))

    def fill_dummies(self, dummies_cols=None, categorical_cols=None,
                     numerical_cols=None, raw_df=None):
        """ Fill the new feature after one hot encoding

        Parameters
        dummies_cols: list  one hot encoding后的分类衍生出来的列(特征)
        categorical_cols: list  分类类型特征列
        numerical_cols:  list  数值类型特征列
        raw_df: DataFrame  训练使用的DataFrame
        """
        if None in (dummies_cols, categorical_cols):
            return self

        assert isinstance(self._df, pd.DataFrame)

        feats_len = self._df.shape[0]
        dummies_len = len(dummies_cols)

        cate_df = pd.DataFrame(
            np.zeros((feats_len, dummies_len)),
            columns=dummies_cols
        )

        for idx in self._df.index:
            for col in categorical_cols:
                col_val = self._df.loc[idx, col]
                dummy_str = '%s_%s' % (col, str(col_val))

                if dummy_str in dummies_cols:
                    cate_df.loc[idx, dummy_str] = 1
                else:
                    # Unknown category, and get mode from raw_df
                    dummy_str = self._fill_unknown_dummies(col, raw_df=raw_df)
                    if dummy_str is not None:
                        cate_df.loc[idx, dummy_str] = 1

        if numerical_cols is None:
            self._df = cate_df
        else:
            numerical_df = self._df[numerical_cols]
            self._df = pd.concat([numerical_df, cate_df], join='inner', axis=1)

            feature_cols = sorted(list(chain(numerical_cols, dummies_cols)))
            self._df = self._df.ix[:, feature_cols]   # 对columns列进行排序，为了满足xgb算法的要求，做fill dummy也要保证顺序

        return self

    def to_pickle(self, pickle_path):
        self._df.to_pickle(pickle_path)

        return self
