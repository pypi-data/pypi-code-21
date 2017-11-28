import pytest
import os
import pandas as pd
from qordoba.commands.find_new_converter import FindNewConverter

#      - '../tests/test_i18n/localization_files/i18n_file_copy.json'
#      - '../tests/test_i18n/localization_files/i18n_file.json'

def test_get_existing_i18n_key_values(i18n_config):
    converter = FindNewConverter()
    localization_keys = converter.get_existing_i18n_key_values(i18n_config)
    assert localization_keys['../tests/test_i18n/localization_files/i18n_file_copy.json']['_override_link_account.bundle_signin.password'] == 'Sign out'

    stringLiteral_value = 'Sign out'
    stringLiteral_key = 'link_account.forgot_password.generic.errors.cant_use_same_password'

    value_return = converter.index_lookup(stringLiteral_value, localization_keys)
    key_return = converter.index_lookup(stringLiteral_key, localization_keys)
    assert value_return == '_override_link_account.bundle_signin.password'
    assert key_return == 'link_account.forgot_password.generic.errors.cant_use_same_password'


def test_csv(i18n_config):
    converter = FindNewConverter()
    csv_file = os.path.join(os.path.dirname(__file__), 'stringLiterals_csv/sample_app_rails_copy.csv')
    DataFrame = converter.generate_CSV_with_key_column(i18n_config, csv_file)
    assert os.path.exists(csv_file) == 1

    output_file = os.path.join(os.path.dirname(__file__), 'stringLiterals_csv/key-sample_app_rails_copy.csv')
    column_names = ['filename', 'startLineNumber', 'startCharIdx', 'endLineNumber', 'endCharIdx', 'text', 'key']
    df2 = pd.read_csv(output_file, header=None, names=column_names)
    assert df2['text'][1]  == 'footer'
    assert df2['key'][2]  == 'link_account.cancel'
