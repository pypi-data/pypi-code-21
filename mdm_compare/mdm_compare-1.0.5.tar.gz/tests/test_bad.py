import os
from nose.tools import raises
from tests import utils


DATA_DIR = os.path.join(os.path.dirname(__file__), 'data', 'bad')
reference_mdm_file = os.path.join(DATA_DIR, 'reference.MDM')


def compare_to_reference_mdm(test_mdm_file):
    utils.default_mdm_compare(
        os.path.join(DATA_DIR, test_mdm_file),
        reference_mdm_file
    )

@raises(IOError)
def test_missing_file():
    compare_to_reference_mdm('nonexistent.MDM')

@raises(ValueError)
def test_missing_a_line():
    compare_to_reference_mdm('missing-a-line.MDM')

@raises(ValueError)
def test_different_results():
    compare_to_reference_mdm('different-results.MDM')
