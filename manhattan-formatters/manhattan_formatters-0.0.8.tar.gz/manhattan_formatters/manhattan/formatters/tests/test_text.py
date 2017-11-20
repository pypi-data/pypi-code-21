from manhattan import formatters


def test_embed_video_url():
    """Return an embed video URL for a video service"""

    # Vimeo
    vimeo_url = formatters.text.embed_video_url(
        'https://vimeo.com/243498473'
    )
    assert vimeo_url.startswith('https://player.vimeo.com/video/243498473')

    # YouTube
    youtube_url = formatters.text.embed_video_url(
        'https://www.youtube.com/watch?v=7yC2vx_fJy8'
    )
    assert youtube_url.startswith('https://www.youtube.com/embed/7yC2vx_fJy8')

def test_humanize_status():
    """Return a human readable version of a status"""
    assert formatters.text.humanize_status('ACTIVE') == 'Active'
    assert formatters.text.humanize_status('not_available') == 'Not available'

    # Check that custom text formatting is applied when specified
    assert formatters.text.humanize_status('out_of_stock') == 'Out of stock'

    assert formatters.text.humanize_status(
        'invalid_password',
        'INVALID'
        ) == 'INVALID password'

    assert formatters.text.humanize_status(
        'logged_in_as_admin_user',
        'ADMIN',
        'USER'
        ) == 'Logged in as ADMIN USER'

def test_remove_accents():
    """
    Replace any accented characters with there closest non-accented equivalent.
    """
    assert formatters.text.remove_accents('Montréal') == 'Montreal'
    assert formatters.text.remove_accents('Françoise') == 'Francoise'

def test_slugify():
    """Return the given string formatted as a slug"""
    assert formatters.text.slugify('"This is my blog title!"') == 'this-is-my-blog-title'

def test_text_to_html():
    """
    Return a HTML version of the specified text.
    """
    s = '<foo>\nbar\r\n\r\nThis is a link http://www.example.com'.strip()

    # Check output for `inline=True` and `convert_urls=True`
    assert formatters.text.text_to_html(s, True, True) == ('&lt;foo&gt;<br>bar<br>'
            '<br>This is a link <a href="http://www.example.com">'
            'http://www.example.com</a>')

    # Check output for `inline=False` and `convert_urls=True`
    assert formatters.text.text_to_html(s, False, True) == ('<p>&lt;foo&gt;<br>bar</p>'
            '<p>This is a link <a href="http://www.example.com">'
            'http://www.example.com</a></p>')

    # Check output for `inline=True` and `convert_urls=False`
    assert formatters.text.text_to_html(s, True, False) == \
            '&lt;foo&gt;<br>bar<br><br>This is a link http://www.example.com'

    # Check output for `inline=False` and `convert_urls=False`
    assert formatters.text.text_to_html(s, False, False) == ('<p>&lt;foo&gt;'
            '<br>bar</p><p>This is a link http://www.example.com</p>')

def test_upper_first():
    """Return a string with the first character converted to uppercase"""
    assert formatters.text.upper_first('the WWW') == 'The WWW'
    assert formatters.text.upper_first('The WWW') == 'The WWW'
    assert formatters.text.upper_first('the www') == 'The www'

def test_yes_no():
    """Return `'Yes'` if a value coerces to `True`, `'No'` if not."""
    assert formatters.text.yes_no(True) == 'Yes'
    assert formatters.text.yes_no(False) == 'No'
    assert formatters.text.yes_no('foo') == 'Yes'
    assert formatters.text.yes_no(None) == 'No'
