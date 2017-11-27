from collections import namedtuple
import flask
from flask import request
from hamcrest import *
import json
from flask_simple_pagination import with_pagination
from unittest import TestCase
from marshmallow import Schema, fields

app = flask.Flask("testapp")

class ItemSerializer(Schema):
    name = fields.Str()


Page = namedtuple("Page", ["results", "next_page", "previous_page", "count"])


class WithPaginationTestCase(TestCase):

    def base_url_factory(self, request):
        return request.headers.get("FRONTEND_URL")

    def rendered_page_no(self, url):
        called_with_page_no = None

        @with_pagination(ItemSerializer, self.base_url_factory)
        def view_func(page_no=None):
            nonlocal called_with_page_no
            called_with_page_no = page_no
            return Page([], 0, 0, 0)

        with app.test_request_context(url) as request:
            view_func()
        return called_with_page_no

    def render_page(self, items, next_page=None, prev_page=None, count=None, url="http://test/?page_no=10", base_url=None):
        @with_pagination(ItemSerializer, self.base_url_factory)
        def view_func(page_no=None):
            return Page(items, next_page, prev_page, count)
        headers = {}
        if base_url is not None:
            headers["FRONTEND_URL"] = base_url
        with app.test_request_context(url, headers=headers):
            return json.loads(view_func().get_data(as_text=True))

    def test_calls_view_func_with_page_number(self):
        assert_that(self.rendered_page_no("/?page_no=10"), equal_to(10))

    def test_calls_with_zero_if_page_no_arg_is_not_integer(self):
        assert_that(self.rendered_page_no("/?page_no=something"), equal_to(0))

    def test_calls_with_zero_if_page_no_is_not_present(self):
        assert_that(self.rendered_page_no("/"), equal_to(0))

    def test_calls_with_zero_if_page_no_is_less_than_zero(self):
        assert_that(self.rendered_page_no("/?page_no=-1"), equal_to(0))

    def test_renders_returned_page_using_item_serializer(self):
        result = self.render_page(
            [{"name": "somename"}],
            next_page=11,
            prev_page=9,
            count=1000,
        )
        assert_that(result, has_entries(
            results=contains(has_entry("name", "somename")),
            next_page="http://test/?page_no=11",
            previous_page="http://test/?page_no=9",
            count=1000,
        ))

    def test_does_not_remove_existing_query_params(self):
        result = self.render_page(
            [{"name": "somename"}],
            next_page=11,
            prev_page=9,
            count=1000,
            url="http://test/?something=else&page_no=9",
        )
        assert_that(result, has_entries(
            results=contains(has_entry("name", "somename")),
            next_page="http://test/?something=else&page_no=11",
            previous_page="http://test/?something=else&page_no=9",
            count=1000,
        ))

    def test_uses_base_url_if_set(self):
        result = self.render_page(
            [{"name": "somename"}],
            next_page=11,
            prev_page=9,
            count=1000,
            base_url="https://api.somewhere/somepath",
        )
        assert_that(result, has_entries(
            results=contains(has_entry("name", "somename")),
            next_page="https://api.somewhere/somepath/?page_no=11",
            previous_page="https://api.somewhere/somepath/?page_no=9",
            count=1000,
        ))

    def test_previous_page_is_none_if_no_previous_page(self):
        result = self.render_page(
            [{"name": "somename"}],
            next_page=11,
            prev_page=None,
            count=1000,
            base_url="https://api.somewhere/somepath",
        )
        assert_that(result, has_entries(
            results=contains(has_entry("name", "somename")),
            next_page="https://api.somewhere/somepath/?page_no=11",
            previous_page=None,
            count=1000,
        ))

    def test_next_page_is_none_if_no_previous_page(self):
        result = self.render_page(
            [{"name": "somename"}],
            next_page=None,
            prev_page=9,
            count=1000,
            base_url="https://api.somewhere/somepath",
        )
        assert_that(result, has_entries(
            results=contains(has_entry("name", "somename")),
            next_page=None,
            previous_page="https://api.somewhere/somepath/?page_no=9",
            count=1000,
        ))
