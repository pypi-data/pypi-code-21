import pytest
from man.manconfig import Version, VersionType


@pytest.fixture
def version():
    return Version(1, 2, 4)


def test_version_need_revert_defaults(version: Version):
    assert version.need_revert == True

    with version:
        pass

    assert version.need_revert == True

    with version:
        version.need_revert = False

    assert version.need_revert == True


def test_version_revert(version: Version):
    with version:
        version[version.PATCH] = 18
        version[version.MINOR] = 42
        version[version.MAJOR] = 123

        assert version.last.version == [1, 2, 4]
        assert isinstance(version.last, Version)

    assert version.version == [1, 2, 4]
    assert version.last is None


def test_version_donot_revert(version: Version):
    with version:
        version[version.MINOR] = 42

        version.need_revert = False

    assert version[version.MINOR] == 42


def test_version_revert_callback(version: Version):
    def revert():
        raise RuntimeError

    with pytest.raises(RuntimeError):
        with version as v:
            assert version is v
            v.revert_version = revert

    assert version.revert_version is not None

    def revert():
        assert 0 == 1

    with version:
        version.revert_version = revert
        version.need_revert = False


def test_version_setitem_by_name(version: Version):
    version['patch'] = 0
    assert version[version.PATCH] == 0

    version['Patch'] = 1
    assert version[version.PATCH] == 1

    version['paTcH'] = 2
    assert version[version.PATCH] == 2

    version['mInOr'] = 3
    assert version[version.MINOR] == 3

    version['MaJoR'] = 4
    assert version[version.MAJOR] == 4


def test_version_constants(version: Version):
    assert version.MAJOR == 0
    assert version.MINOR == 1
    assert version.PATCH == 2


def test_version_setitem_resets_lower_importance(version: Version):
    version[version.PATCH] = 100
    assert version.version == [1, 2, 100]

    version[version.MINOR] += 100
    assert version.version == [1, 102, 0]

    version[version.MAJOR] = 100
    assert version.version == [100, 0, 0]



@pytest.fixture
def vtype():
    return VersionType()


@pytest.mark.parametrize('string, result', [
    ('v1.2.3', [1, 2, 3]),
    ('1.2.3', [1, 2, 3]),
    ('v12345.123456.7890', [12345, 123456, 7890]),
    ('0.0.0', [0, 0, 0]),
])
def test_versiontype_load_succes(vtype: VersionType, string, result):
    assert vtype.load(string).version == result

@pytest.mark.parametrize('input', [
    '1.2.3.4',
    '1.2.3b',
    '1.2',
    'v1',
    'v1.2.',
    'v1..2.3',
    '1..2',
    '1.2..'
])
def test_versiontype_load_fails(vtype: VersionType, input):
    with pytest.raises(ValueError):
        vtype.load(input)


@pytest.mark.parametrize('version, saved', [
    (Version(1, 2, 3), '1.2.3'),
    (Version(0, 0, 0), '0.0.0')
])
def test_versiontype_save(vtype: VersionType, version, saved):
    assert vtype.save(version) == saved
    assert isinstance(vtype.save(version), str)

def test_versiontype_isvalid(vtype: VersionType):
    assert vtype.is_valid(Version(1, 2, 3))
    assert not vtype.is_valid('v1.1.2')
    assert not vtype.is_valid('1.1.2')
    assert not vtype.is_valid([1, 2, 3])


def test_version_type_name(vtype):
    assert vtype.name == 'version'
