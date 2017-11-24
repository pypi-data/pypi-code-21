from ..templatetags.cms_qe_video import cms_qe_video_url_to_embed
import pytest


@pytest.mark.parametrize('url, expected', [
    ('https://servis.com/somevideo', 'https://servis.com/somevideo'),
    ('http://vimeo.com/somevideo', 'http://player.vimeo.com/video/somevideo'),
    ('https://vimeo.com/somevideo', 'https://player.vimeo.com/video/somevideo'),
    ('https://vimeo.com/somevideo?param', 'https://player.vimeo.com/video/somevideo'),
    ('https://youtu.be/watch?v=ZGuQmszmtaQ', 'https://www.youtube.com/embed/ZGuQmszmtaQ'),
    ('https://www.youtube.com/watch?v=ZGuQmszmtaQ', 'https://www.youtube.com/embed/ZGuQmszmtaQ'),
    # Test for bug with additional parameters in link.
    # Related on issue: https://gitlab.labs.nic.cz/websites/django-cms-qe/issues/41
    ('https://www.youtube.com/watch?v=ZGuQmszmtaQ&index=10&list=PLfTu7SiuiT_izjvg_1JRKXkrWSnvuP4pd',
     'https://www.youtube.com/embed/ZGuQmszmtaQ'),
])
def test_url_to_embed(url, expected):
    assert expected == cms_qe_video_url_to_embed(url)
