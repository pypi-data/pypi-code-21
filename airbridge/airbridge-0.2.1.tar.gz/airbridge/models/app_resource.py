#-*- coding:utf-8 -*-
import uuid
import time
import json
from sqlalchemy.sql import text
from airbridge.utils.tools import ret_one_row, is_empty, \
                                  ret_one_row_without_exception, \
                                  remove_trailing_br_tag


class AppResource():

    def __init__(self, read_engine, subdomain=None, app_id=None, engine=None):

        # Engines
        self.read_engine = read_engine
        self.engine = engine if engine is not None else read_engine

        # Arguments
        if subdomain is None and app_id is None:
            raise ValueError("It needs subdomain or app_id.")

        self.subdomain = subdomain
        self.app_id = app_id

        # Attributes
        self.app = {}
        self.app_property = [
            "app_id",
            "app_name",
            "app_subdomain",
            "app_icon_image_url",
            "dominant_colors",
            "ios_market",
            "android_market",
            "web_landing",
            "sdk_flag",
            "app_keywords",
            "app_title",
            "app_description",
            "auto_link_generate",
            "no_review",
            "created_at",
            "owner_user_id"
        ]

        self.set_app_data()

        self.app['app_description'] = remove_trailing_br_tag(self.app['app_description']) if not is_empty(self.app['app_description']) else ""
        self.app_id = self.app['app_id']
        self.subdomain = self.app['app_subdomain']

    def get_ios_app_store_id(self):
        if type(self.app.get('ios_market')) is str \
            or type(self.app.get('ios_market')) is unicode:
            return self.app.get('ios_market').split('id')[1].split('?')[0] if 'id' in self.app.get('ios_market') else None
        else:
            return None

    def get_android_package_name(self):
        if type(self.app.get('android_market')) is str \
            or type(self.app.get('android_market')) is unicode:
            return self.app.get('android_market').split('?id=')[1].split('&')[0] if '?id=' in self.app.get('android_market') else None
        else:
            return None

    def set_app_data(self):
        query_str = """
                    SELECT
                        apps.id as app_id,
                        apps.name as app_name,
                        apps.subdomain as app_subdomain,
                        apps.app_icon_image_url,
                        apps.dominant_colors,
                        apps.android_market,
                        apps.ios_market,
                        apps.web_landing,
                        apps.sdk_flag,
                        apps.keywords as app_keywords,
                        apps.app_title,
                        apps.app_description,
                        apps.auto_link_generate,
                        apps.no_review,
                        apps.created_at,
                        apps.owner_user_id

                    FROM
                        tbl_apps as apps

                    {0}
                    """

        if self.subdomain is not None:
            query_str = query_str.format("WHERE apps.subdomain = :subdomain AND apps.status = 1")
            rows = self.read_engine.execute(text(query_str), subdomain=self.subdomain)
        elif self.app_id is not None:
            query_str = query_str.format("WHERE apps.id = :app_id AND apps.status = 1")
            rows = self.read_engine.execute(text(query_str), app_id=self.app_id)

        result = ret_one_row(rows, "There is no such app. Please check.")

        self.app = {}
        for prop in self.app_property:
            self.app[prop] = result[prop]
