from pyramid.config import Configurator
import bugsnag
import pytest


@pytest.fixture(autouse=True)
def reset_bugsnag():
    yield
    # Reset the default/global client instance and its configuration
    bugsnag.legacy.default_client = bugsnag.legacy.Client()
    bugsnag.legacy.configuration = bugsnag.legacy.default_client.configuration
    bugsnag.configuration = bugsnag.legacy.configuration


def test_without_settings():
    settings = {}
    config = Configurator(settings=settings)
    config.include('pyramid_bugsnag')
    config.commit()


def test_with_settings():
    settings = {
        'bugsnag.api_key': 'POIPOI',
        'bugsnag.app_version': '1.2.3',
        'bugsnag.asynchronous': 'false',
        'bugsnag.ignore_classes': """
            class1
            class2
        """
    }
    config = Configurator(settings=settings)
    config.include('pyramid_bugsnag')
    config.commit()

    assert bugsnag.configuration.api_key == 'POIPOI'
    assert bugsnag.configuration.app_version == '1.2.3'
    assert bugsnag.configuration.asynchronous is False
    assert bugsnag.configuration.ignore_classes == ['class1', 'class2']
