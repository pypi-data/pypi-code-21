
import os
import logging
import unittest

import pandas as pd

from velenxc.preprocessing.pipeline import DataFramePipe

logging.basicConfig(level=logging.DEBUG)


class PreProcessingPipelineTestCase(unittest.TestCase):

    def setUp(self):
        self.test_df = pd.DataFrame([
            {'f1': 1, 'f2': 's', 'f3': 10.298, 'f4': '1'},
            {'f1': 4, 'f2': 'ss', 'f3': 10.298, 'f4': '1'},
            {'f1': 10, 'f2': 's', 'f3': 10.298, 'f4': '2'},
            {'f1': 20, 'f2': 's', 'f3': 10.298, 'f4': '3'},
        ])

        self.dummies_cols = ['f2_s', 'f2_ss', 'f4_1', 'f4_2', 'f4_3']
        self.categorical_cols = ['f2', 'f4']
        self.numerical_cols = ['f1', 'f3']

    def test_init_by_string(self):
        test_pipe = DataFramePipe('df.csv')

        self.assertTrue(len(test_pipe.data) == 0)

    def test_init_with_y_tag(self):

        test_df = pd.DataFrame([
            {'f1': 1, 'f2': 's', 'f3': 10.298, 'f4': '1', 'tag': 1},
            {'f1': 4, 'f2': 'ss', 'f3': 10.298, 'f4': '1', 'tag': 0},
            {'f1': 10, 'f2': 's', 'f3': 10.298, 'f4': '2', 'tag': 0},
            {'f1': 20, 'f2': 's', 'f3': 10.298, 'f4': '3', 'tag': 0},
        ])

        test_pipe = DataFramePipe(data=test_df, label_name='tag')

        self.assertTrue(hasattr(test_pipe, '_y'))
        self.assertTrue(test_pipe._y is not None)

        shape = test_pipe.data.shape
        self.assertTrue(shape[0] == 4 and shape[1] == 5)
        self.assertTrue(test_pipe.data['tag'][0] == 1)

    def _to_dummies(self, data):
        test_pipe = DataFramePipe(data)

        dummies_df = test_pipe.fill_dummies(
            dummies_cols=self.dummies_cols, categorical_cols=self.categorical_cols,
            numerical_cols=self.numerical_cols, raw_df=self.test_df
        )

        return dummies_df

    def test_fill_dummies_by_gte_2_records(self):
        dummies_df = self._to_dummies(self.test_df)

        self.assertTrue('f2_s' in dummies_df.data.columns)
        self.assertTrue(dummies_df.data.loc[0, 'f2_s'] == 1)

    def test_fill_dummies_by_1_record(self):
        dummies_df = self._to_dummies(
            pd.DataFrame([{'f1': 3, 'f2': 'ss', 'f3': 2.298, 'f4': '3'}])
        )

        logging.debug(dummies_df.data)
        self.assertTrue('f2_s' in dummies_df.data.columns)
        self.assertTrue(dummies_df.data.loc[0, 'f2_ss'] == 1)

    def test_fill_dummies_by_unknown(self):
        dummies_df = self._to_dummies(
            pd.DataFrame([{'f1': 3, 'f2': 'ss', 'f3': 2.298, 'f4': '4'}])
        )

        logging.debug(dummies_df.data)
        self.assertTrue('f4_4' not in dummies_df.data.columns)
        self.assertTrue(dummies_df.data.loc[0, 'f4_1'] == 1)

    def test_fill_dummies_by_None(self):
        dummies_df = self._to_dummies(
            pd.DataFrame([{'f1': 3, 'f2': None, 'f3': 2.298, 'f4': '4'}])
        )

        logging.debug(dummies_df.data)
        self.assertTrue('f4_4' not in dummies_df.data.columns)
        self.assertTrue(dummies_df.data.loc[0, 'f2_s'] == 1)

    def test_fill_dummies_without_numerical_cols(self):
        raw_df = pd.DataFrame([
            {'f2': 's', 'f4': '1'},
            {'f2': 'ss', 'f4': '1'},
            {'f2': 's', 'f4': '2'},
            {'f2': 's', 'f4': '3'},
        ])

        test_pipe = DataFramePipe(pd.DataFrame([{'f2': None, 'f4': '4'}]))

        test_pipe.fill_dummies(
            dummies_cols=self.dummies_cols, categorical_cols=self.categorical_cols,
            numerical_cols=None, raw_df=raw_df
        )

        self.assertTrue(test_pipe.data.loc[0, 'f2_s'] == 1)
        self.assertTrue(test_pipe.data.loc[0, 'f4_1'] == 1)

    def test_fill_dummies_categorical_cols_none(self):

        test_pipe = DataFramePipe(pd.DataFrame([{'f2': None, 'f4': '4'}]))

        test_pipe.fill_dummies(
            dummies_cols=None, categorical_cols=self.categorical_cols,
            numerical_cols=None, raw_df=self.test_df
        )

        self.assertTrue(test_pipe.data.loc[0, 'f4'] == '4')

    def test_one_hot_encoding(self):

        test_pipe = DataFramePipe(self.test_df)
        test_pipe.one_hot_encoding()

        self.assertTrue(test_pipe.data.loc[0, 'f2_s'] == 1)
        self.assertTrue(test_pipe.data.loc[0, 'f2_ss'] == 0)

    def test_fill_na(self):
        test_pipe = DataFramePipe(
            pd.DataFrame([
                {'f1': 9, 'f2': 's', 'f3': 10.298, 'f4': '1'},
                {'f1': None, 'f2': 'ss', 'f3': 10.298, 'f4': None},
                {'f1': 4, 'f2': 's', 'f3': None, 'f4': '3'}
            ])
        )

        test_pipe.fill_na()

        self.assertTrue(test_pipe.data.loc[2, 'f3'] == 10.298)
        self.assertTrue(test_pipe.data.loc[1, 'f1'] == 6.5)
        self.assertTrue(test_pipe.data.loc[1, 'f4'] is None)

    def test_drop_missing_value(self):

        test_pipe = DataFramePipe(
            pd.DataFrame([
                {'f1': 9, 'f2': 's'},
                {'f1': 8, 'f2': 's'},
                {'f1': 6, 'f2': None},
                {'f1': 3, 'f2': None},
                {'f1': 1, 'f2': None},
                {'f1': 10, 'f2': None},
                {'f1': 4, 'f2': None},
            ])
        )

        test_pipe.drop_missing_data()
        self.assertTrue('f2' not in test_pipe.data.columns)

    def test_pipe_flow_of_training(self):

        test_pipe = DataFramePipe(
            pd.DataFrame([
                {'f1': 9, 'f2': 's', 'f3': '1'},
                {'f1': 8, 'f2': 's', 'f3': None},
                {'f1': None, 'f2': None, 'f3': '3'},
                {'f1': 3, 'f2': None, 'f3': '1'},
                {'f1': 1, 'f2': None, 'f3': '3'},
                {'f1': None, 'f2': None, 'f3': '1'},
                {'f1': 4, 'f2': None, 'f3': '2'},
            ])
        )

        test_pipe.drop_missing_data()\
            .fill_na()\
            .one_hot_encoding()

        self.assertTrue(test_pipe.data.loc[1, 'f3_1'] == 0)
        self.assertTrue('f2' not in test_pipe.data.columns)

    def test_drop_high_zero_data(self):

        test_pipe = DataFramePipe(
            pd.DataFrame([
                {'f1': 9, 'f2': 's'},
                {'f1': 8, 'f2': 0},
                {'f1': 6, 'f2': 0},
                {'f1': 3, 'f2': 0},
                {'f1': 1, 'f2': 0},
                {'f1': 10, 'f2': 0},
                {'f1': 4, 'f2': 0},
            ])
        )

        test_pipe.drop_high_zero_data()
        self.assertTrue('f2' not in test_pipe.data.columns)

        self.assertTrue('f2' in test_pipe.deleted_feature)

    def test_set_feats(self):
        test_pipe = DataFramePipe(pd.DataFrame([
            {'f1': 9, 'f2': 's'},
            {'f1': 8, 'f2': 'a'}
        ]))

        test_pipe.set_feats('categorical_feats', ['f2'])
        self.assertTrue(['f2'] == test_pipe.categorical_feats)

    def test_classify_encode_conversion_with_not_encoded(self):

        test_pipe = DataFramePipe(
            pd.DataFrame([
                {'f1': 9, 'f2': '通过'},
                {'f1': 8, 'f2': '未通过'},
                {'f1': 6, 'f2': 'UK'},
                {'f1': 3, 'f2': '待验证'}
            ]),
            categorical_feats=['f2']
        )

        test_pipe.classify_encode_conversion()
        self.assertTrue('f2' in test_pipe.classes_encode_)

    def test_classify_encode_conversion_with_encoded(self):

        test_pipe = DataFramePipe(
            pd.DataFrame([
                {'f1': 9, 'f2': '通过'},
                {'f1': 8, 'f2': '未通过'},
                {'f1': 6, 'f2': 'UK'},
                {'f1': 3, 'f2': '待验证'}
            ]),
            categorical_feats=['f2']
        )

        test_pipe.classify_encode_conversion(encoded={'f2': {'通过': '0', '未通过': 1, '待验证': '2', 'UK': '3'}})
        self.assertTrue('f2' in test_pipe.classes_encode_)
        self.assertTrue(test_pipe.data['f2'][0] == '0')

    def test_to_pickle(self):
        test_pipe = DataFramePipe(
            pd.DataFrame([
                {'f1': 9, 'f2': '通过'},
                {'f1': 8, 'f2': '未通过'},
                {'f1': 6, 'f2': 'UK'},
                {'f1': 3, 'f2': '待验证'}
            ]),
            categorical_feats=['f2']
        )

        pickle_path = os.path.join(os.path.dirname(__file__), 'test.pkl')

        test_pipe.to_pickle(pickle_path)

        self.assertTrue(os.path.exists(pickle_path))

        # delete the pickle object
        os.remove(pickle_path)
