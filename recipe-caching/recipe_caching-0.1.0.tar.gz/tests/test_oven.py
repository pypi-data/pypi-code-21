from recipe.oven import get_oven


def test_create_caching_oven():
    oven = get_oven('sqlite://', name='caching')
    assert oven.engine.driver == 'pysqlite'
    assert oven.Session.kw['bind'] == oven.engine


def test_create_caching_oven_no_target():
    oven = get_oven(name='caching')
    assert oven.engine is None
    assert oven.Session is None
