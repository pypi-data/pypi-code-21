from dpcolors import ColorString


def test_irc():
    s = b'<\x0f\x0301lmnt\x0304,01\xf0\x9f\x94\xa5\x0fnuff\x0f\x0f\x03black>'.decode('utf8')
    cs = ColorString.from_irc(s)
    assert len(cs.parts) == 4
    assert cs.parts[1].color.r == cs.parts[1].color.g == cs.parts[1].color.b == 0
    assert cs.parts[2].bg_color.r == cs.parts[2].bg_color.g == cs.parts[2].bg_color.b == 0

