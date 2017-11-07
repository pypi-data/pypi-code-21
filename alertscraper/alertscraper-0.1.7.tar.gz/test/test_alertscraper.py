'''
Tests for `alertscraper` module.
'''
from alertscraper import alertscraper

# TODO add more tests


class TestParseLines:
    def test_parse_lines_simple(self):
        assert alertscraper.parse_lines(['stuff|whatever|thing']) == ['stuff']


class TestListItem:
    def test_list_item_basic(self):
        test_html = '''
            <div>
                <a href="some/long/path">This~~~ is it!!!</a>
                <a href="#">ignore me</a>
            </div>
        '''
        li = alertscraper.ListItem(test_html, ['ignore me'], False)
        assert str(li) == 'This is it!!!'
        assert li.normalized_text == 'thisisit'
        assert li.html.replace(' ', '') == '''
            <a href="some/long/path">This~~~ is it!!!</a>
            <a href="#">ignore me</a>
        '''.replace(' ', '')

    def test_list_item_cleanup(self):
        test_html = '''
            <div>
                <a href="some/path">Link!</a>
                <a href="#">ignore me</a>
            </div>
        '''
        li = alertscraper.ListItem(test_html, ['ignore me'], True)
        assert li.html == '<a href="some/path">Link!</a>'
