from dpcolors import ColorString


def test_dp_to_irc():
    s = '^4hello^x112world^^^9bleh'
    cs = ColorString.from_dp(s)
    res = cs.to_irc()
    assert type(res) is bytes
    assert res.count(b'\x03') == 4
    assert res.count(b'^') == 1
    assert res.count(b'\x03\x0f') == 3
    assert res[:3] == b'\x0312'


def test_irc_to_dp():
    s = b'<\x0f\x0301lmnt\x0304,01\xf0\x9f\x94\xa5\x0fnuff\x0f\x0f\x03black>^'.decode('utf8')
    cs = ColorString.from_irc(s)
    res = cs.to_dp()
    assert type(res) is bytes
    assert res.count(b'^x') == 2
    assert res.count(b'^^') == 1
    assert res.count(b'^x000') == 1

def test_dp_to_ansi():
    pass
