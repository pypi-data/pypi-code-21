import pytest

from manhattan.comparable.change_log import ChangeLogEntry

pytest_plugins = ['fixtures']


def test_init(mongo_client):
    """Should create a new ChangeLogEntry instance"""
    entry = ChangeLogEntry()
    assert isinstance(entry, ChangeLogEntry)

def test_diff_html(mongo_client):
    """Should return an entry's diff as HTML"""

    original = {
        'bar': 'bar',
        'foo': 'foo'
        }

    new = {
        'bar': 'foo',
        'zee': 'zee'
        }

    entry = ChangeLogEntry()
    entry.add_diff(original, new)

    assert entry.diff_html.strip() == '''<div class="change change--add">
    <div class="change__field">zee</div>
    <div class="change__values">
        <div class="change__value change__value--new">
            zee
        </div>
    </div>
</div>
<div class="change change--update">
    <div class="change__field">bar</div>
    <div class="change__values">
        <div class="change__value change__value--original">
            bar
        </div>
        <div class="change__value change__value--new">
            foo
        </div>
    </div>
</div>
<div class="change change--delete">
    <div class="change__field">foo</div>
    <div class="change__values">
        <div class="change__value change__value--original">
            foo
        </div>
    </div>
</div>'''

def test_is_diff(mongo_client):
    """Should return True if there are any logged difference for the entry"""

    entry = ChangeLogEntry()

    entry.add_note('Testing no diff')
    assert entry.is_diff is False

    entry.add_diff({'foo': 'bar'}, {})
    assert entry.is_diff is True

def test_add_diff(mongo_client):
    """
    Should set the detials of the entry as the difference between 2 dictionaries
    (original vs. new).
    """

    original = {
        'bar': 'bar',
        'foo': 'foo'
        }

    new = {
        'bar': 'foo',
        'zee': 'zee'
        }

    entry = ChangeLogEntry()
    entry.add_diff(original, new)

    assert entry.details == {
        'additions': {'zee': 'zee'},
        'deletions': {'foo': 'foo'},
        'updates': {'bar': ['bar', 'foo']}
        }

def test_add_note(mongo_client):
    """Should add a note as the entries details"""

    entry = ChangeLogEntry()
    entry.add_note('Testing')

    assert entry.details == {'note': 'Testing'}

def test_diff_to_html(mongo_client):
    """Should return the given set of details as HTML"""

    # Additions
    additions = ChangeLogEntry.diff_to_html({'additions': {'zee': 'zee'}})
    assert additions == '''<div class="change change--add">
    <div class="change__field">zee</div>
    <div class="change__values">
        <div class="change__value change__value--new">
            zee
        </div>
    </div>
</div>'''

    # Updates
    updates = ChangeLogEntry.diff_to_html({'updates': {'bar': ['bar', 'foo']}})
    assert updates == '''<div class="change change--update">
    <div class="change__field">bar</div>
    <div class="change__values">
        <div class="change__value change__value--original">
            bar
        </div>
        <div class="change__value change__value--new">
            foo
        </div>
    </div>
</div>'''

    # Deletions
    deletions = ChangeLogEntry.diff_to_html({'deletions': {'foo': 'foo'}})
    assert deletions == '''<div class="change change--delete">
    <div class="change__field">foo</div>
    <div class="change__values">
        <div class="change__value change__value--original">
            foo
        </div>
    </div>
</div>'''

    # Note
    note = ChangeLogEntry.diff_to_html({'note': 'Testing'})
    assert note == '<div class="change change--note">Testing</div>'

def test_diff_safe(mongo_client, dragon):
    """Should return a value that can safely be stored as a diff"""

    safe_dragon = {'_str': str(dragon), '_id': dragon._id}

    assert ChangeLogEntry.diff_safe('foo') == 'foo'
    assert ChangeLogEntry.diff_safe(dragon) == safe_dragon
    assert ChangeLogEntry.diff_safe([dragon]) == [safe_dragon]