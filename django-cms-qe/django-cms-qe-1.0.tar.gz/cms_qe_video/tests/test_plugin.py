import re

from test_utils import render_plugin

from ..cms_plugins import HostingVideoPlayerPlugin, SourceFileVideoPlayerPlugin


def test_render_source_file_video_plugin(cms_qe_video_source_file_video_player_model):
    html = render_plugin(SourceFileVideoPlayerPlugin, cms_qe_video_source_file_video_player_model)
    assert re.search(r'<video(\s|.)*</video>', html)
    assert not re.search(r'<iframe(\s|.)*</iframe>', html)


def test_render_hosting_video_plugin(cms_qe_video_hosting_video_player_model):
    html = render_plugin(HostingVideoPlayerPlugin, cms_qe_video_hosting_video_player_model)
    assert not re.search(r'<video(\s|.)*</video>', html)
    assert re.search(r'<iframe(\s|.)*</iframe>', html)
