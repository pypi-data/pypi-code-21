from dpcolors import ColorString


def test_real_nicknames(nicknames):
    for i in nicknames:
        cs = ColorString.from_dp(i)
        if len(i) > 0:
            assert len(cs.parts) > 0
            assert len(cs.original_bytes) > 0
            assert cs.original_type == 'dp'


def test_real_nicknames_noglyphs(nicknames):
    for i in nicknames:
        cs = ColorString.from_dp(i, use_unicode_for_glyphs=False)
        if len(i) > 0:
            assert len(cs.parts) > 0
            assert len(cs.original_bytes) > 0
            assert cs.original_type == 'dp'
