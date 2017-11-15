
from threedb import SimpleStorage


def test_init_storage_without_schema():
    stor = SimpleStorage(".", schema=None)
    assert not stor._schema


def test_init_storage_with_schema():
    config = {
        'schema': {
            'data': {
                'load': 'file_path',
                'match': ['data.*']},
            'etalon': {
                'load': 'file_path',
                'match': ['etalon.*'],
                'type': 'text'}
        }
    }

    stor = SimpleStorage(".", schema=config["schema"])
    assert stor._schema == config["schema"]


def test_read_empty(tmpdir):
    stor = SimpleStorage(str(tmpdir))
    assert not stor.read()


def test_read_single_file_without_schema(tmpdir):
    text = "lala"

    f = tmpdir.mkdir("0001_TestData").join("0001_data.txt")
    f.write("lala")

    stor = SimpleStorage(str(tmpdir))
    item = stor.read()[0]
    assert not item.tags
    assert item.index == "0001_TestData"
    assert item["0001_data_txt"].text == text


def test_read_single_file_with_schema(tmpdir):
    config = {
        'schema': {
            'data': {
                'load': 'file_path',
                'match': ['0001_data.*']}
        }
    }
    text = "lala"

    f = tmpdir.mkdir("0001_TestData").join("0001_data.txt")
    f.write("lala")

    stor = SimpleStorage(str(tmpdir), schema=config["schema"])
    assert stor.read()[0]["data"].text == text
