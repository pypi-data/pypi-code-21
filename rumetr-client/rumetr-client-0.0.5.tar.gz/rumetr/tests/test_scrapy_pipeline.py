import pytest
from ..scrapy import UploadPipeline


@pytest.fixture
def spider_with_settings():
    class MockedSpider:
        settings = {
            'TEST_SETTING': 1,
            'RUMETR_API_HOST': 'http://host',
            'RUMETR_TOKEN': 'tkn',
            'RUMETR_DEVELOPER': 'dvlpr',
        }
    return MockedSpider


def test_required_settings(spider_with_settings):
    p = UploadPipeline()
    p.spider = spider_with_settings
    p._parse_settings()
    assert p.settings['auth_key'] == 'tkn'
    assert p.settings['developer'] == 'dvlpr'


def test_no_required_setting_error(spider_with_settings):
    del spider_with_settings.settings['RUMETR_DEVELOPER']

    p = UploadPipeline()
    p.spider = spider_with_settings
    with pytest.raises(TypeError):
        p._parse_settings()


def test_non_required_settings(spider_with_settings):
    p = UploadPipeline()
    p.spider = spider_with_settings
    p._parse_settings()
    assert p.settings['api_host'] == 'http://host'


def test_non_required_settings_are_no_present(spider_with_settings):
    del spider_with_settings.settings['RUMETR_API_HOST']
    p = UploadPipeline()
    p.spider = spider_with_settings
    p._parse_settings()

    assert 'api_host' not in p.settings.keys()


def test_settings_are_parsed_only_once(spider_with_settings):
    p = UploadPipeline()
    p.settings = {
        'eggs?': 'SPAM',
    }
    p.spider = spider_with_settings
    p._parse_settings()
    assert p.settings == {
        'eggs?': 'SPAM',
    }  # should remain the same
