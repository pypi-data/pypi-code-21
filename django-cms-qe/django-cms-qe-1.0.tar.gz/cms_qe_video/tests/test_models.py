import pytest
from cms_qe_video.models import VIMEO, YOUTUBE
from django.core.exceptions import ValidationError
from pytest_data import use_data

non_default_data = {
    'controls': False,
    'width': 500,
    'height': 500,
    'autoplay': True,
    'loop': True,
    'muted': True,
}


def test__get_attributes_str_to_html_with_default_attributes(cms_qe_video_source_file_video_player_model):
    attr_str = cms_qe_video_source_file_video_player_model._get_attributes_str_to_html(
        ('width', 'height', 'controls', 'autoplay', 'loop', 'muted'))
    assert 'width=500' not in attr_str and 'height=500' not in attr_str
    assert 'controls' in attr_str
    assert 'autoplay' not in attr_str
    assert 'loop' not in attr_str
    assert 'muted' not in attr_str


@use_data(cms_qe_video_source_file_video_player_model_data=non_default_data)
def test__get_attributes_str_to_html_with_non_default_attributes(cms_qe_video_source_file_video_player_model):
    attr_str = cms_qe_video_source_file_video_player_model._get_attributes_str_to_html(
        ('width', 'height', 'controls', 'autoplay', 'loop', 'muted'))
    assert 'width=500' in attr_str and 'height=500' in attr_str
    assert 'controls' not in attr_str
    assert 'autoplay' in attr_str
    assert 'loop' in attr_str
    assert 'muted' in attr_str


def test__get_attributes_str_to_url_with_default_attributes(cms_qe_video_source_file_video_player_model):
    attr_str = cms_qe_video_source_file_video_player_model._get_attributes_str_to_url(
        ('width', 'height', 'controls', 'autoplay', 'loop', 'muted'))
    assert 'width' not in attr_str and 'height' not in attr_str
    assert 'controls=1' in attr_str
    assert 'autoplay' not in attr_str
    assert 'loop' not in attr_str
    assert 'muted' not in attr_str


@use_data(cms_qe_video_source_file_video_player_model_data=non_default_data)
def test__get_attributes_str_to_url_with_non_default_attributes(cms_qe_video_source_file_video_player_model):
    attr_str = cms_qe_video_source_file_video_player_model._get_attributes_str_to_url(
        ('width', 'height', 'controls', 'autoplay', 'loop', 'muted'))
    assert 'width=500' in attr_str and 'height=500' in attr_str
    assert 'controls' not in attr_str
    assert 'autoplay=1' in attr_str
    assert 'loop=1' in attr_str
    assert 'muted=1' in attr_str
    assert attr_str.count('&') == 4


@use_data(
    cms_qe_video_hosting_video_player_model_data={'video_hosting_service': YOUTUBE,
                                                  'video_url': 'isnotyoutube.com/somevideo', })
def test_clean_youtube_bad_url(cms_qe_video_hosting_video_player_model):
    with pytest.raises(ValidationError) as validation_exception:
        cms_qe_video_hosting_video_player_model.clean()
    validation_exception.match(r'.*YouTube.*')


@use_data(
    cms_qe_video_hosting_video_player_model_data={'video_hosting_service': VIMEO,
                                                  'video_url': 'notvimeo.com/somevideo', })
def test_clean_vimeo_bad_url(cms_qe_video_hosting_video_player_model):
    with pytest.raises(ValidationError) as validation_exception:
        cms_qe_video_hosting_video_player_model.clean()
    validation_exception.match(r'.*Vimeo.*')


@use_data(cms_qe_video_hosting_video_player_model_data={'video_url': 'youtube.com/somevideo',
                                                        'video_hosting_service': YOUTUBE})
def test_clean_youtube_good_urls(cms_qe_video_hosting_video_player_model):
    cms_qe_video_hosting_video_player_model.clean()


@use_data(cms_qe_video_hosting_video_player_model_data={'video_url': 'vimeo.com/somevideo',
                                                        'video_hosting_service': VIMEO})
def test_clean_vimeo_good_urls(cms_qe_video_hosting_video_player_model):
    cms_qe_video_hosting_video_player_model.clean()


@use_data(cms_qe_video_hosting_video_player_model_data={'video_url': 'vimeo.com/somevideo',
                                                        'video_hosting_service': VIMEO,
                                                        'controls': False})
def test_clean_vimeo_disabled_controls(cms_qe_video_hosting_video_player_model):
    with pytest.raises(ValidationError) as validation_exception:
        cms_qe_video_hosting_video_player_model.clean()
    validation_exception.match(r'.*Vimeo.*controls.*')