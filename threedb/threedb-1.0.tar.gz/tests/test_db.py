
from threedb import ThreeDB
import pytest


def test_read_empty(tmpdir):
    db = ThreeDB(str(tmpdir))
    assert not db.search()


def test_db_search_without_filter(create_test_data):
    db = ThreeDB(str(create_test_data))
    records = db.search()

    assert len(records) == 10


@pytest.mark.parametrize("index", range(10))
def test_db_search_with_filter(index, create_test_data):
    db = ThreeDB(str(create_test_data))

    records = db.search(False, str("000%d" % index))
    assert len(records) == 1


def test_db_search_with_filters(create_test_data):
    db = ThreeDB(str(create_test_data))

    records = db.search(False, "0000", "0009")
    assert len(records) == 2
