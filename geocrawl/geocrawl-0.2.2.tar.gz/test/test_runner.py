import pytest

from geocrawl.runner import return_item_title


class TestPrint(object):

    @pytest.fixture
    def item(self):
        return {
            'title': 'test title',
            'attribute': 'value'
        }

    def test_return_item_title(self, item):
        assert return_item_title(item, None, None) == item['title']
