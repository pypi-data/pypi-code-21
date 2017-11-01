import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

import steam_api
import pytest


class TestNews(object):
    def test_initialize_steam_news_class_without_setting_app_id(self):
        with pytest.raises(ValueError):
            steam_api.news.News()

    def test_initialize_steam_news_class_width_app_id(self):
        news = steam_api.news.News(440)
        assert news.app_id == 440

    def test_steam_news_items_with_app_id(self):
        news = steam_api.news.News(440)
        assert len(news.news_items) > 0

    def test_steam_news_items_with_non_exist_app_id(self):
        news = steam_api.news.News(0)
        assert news.news_items == []