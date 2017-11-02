import pytest

from wscheck.checker import WhitespaceChecker
from tests.unit.open_mock import patch_open_read


@pytest.fixture
def checker(mocker):
    instance = WhitespaceChecker()
    mocker.patch.object(instance, 'check_text', auto_spec=True)

    return instance


@pytest.mark.parametrize('file_path,file_content', [
    ('/empty/file', ''),
    ('/contains/anything', ' foo\t\r\nbar '),
])
def test_integration(checker, file_path, file_content):
    mocked_files = {file_path: file_content}

    with patch_open_read(mocked_files):
        checker.check_file(file_path)

    checker.check_text.assert_called_once_with(file_content, source_path=file_path)
