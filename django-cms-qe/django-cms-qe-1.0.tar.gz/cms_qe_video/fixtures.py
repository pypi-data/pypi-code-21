# pylint: disable=invalid-name

import pytest
from pytest_data import get_data

from .models import HostingVideoPlayer, SourceFileVideoPlayer


@pytest.fixture
def cms_qe_video_source_file_video_player_model(request):
    return SourceFileVideoPlayer(**get_data(
        request,
        'cms_qe_video_source_file_video_player_model_data',
    ))


@pytest.fixture
def cms_qe_video_hosting_video_player_model(request):
    return HostingVideoPlayer(**get_data(
        request,
        'cms_qe_video_hosting_video_player_model_data',
    ))
