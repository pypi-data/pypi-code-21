from unittest import TestCase

from flask import Flask
from flask_wtf.html5 import (SearchField, TelField, URLField, EmailField,
                             DateTimeField, DateField, DateTimeLocalField,
                             IntegerField, DecimalField, IntegerRangeField,
                             DecimalRangeField)
from flask_wtf_polyglot import PolyglotForm


class MyForm(PolyglotForm):

    search = SearchField('search')
    tel = TelField('tel')
    url = URLField('url')
    email = EmailField('email')
    date_time = DateTimeField('date_time')
    date = DateField('date')
    date_time_local = DateTimeLocalField('date_time_local')
    integer = IntegerField('integer')
    decimal = DecimalField('decimal')
    integer_range = IntegerRangeField('integer_range')
    decimal_range = DecimalRangeField('decimal_range')


class MyTest(TestCase):

    def setUp(self):
        self.app = self.create_app()
        self.client = self.app.test_client()

    def create_app(self):
        app = Flask(__name__)
        app.secret_key = 'secret'
        return app

    def test_search_field(self):
        with self.app.test_request_context():
            form = MyForm()
            self.assertEqual(form.search(),
                             '<input id="search" name="search" type="search"'
                             ' value="" />')

    def test_tel_field(self):
        with self.app.test_request_context():
            form = MyForm()
            self.assertEqual(form.tel(),
                             '<input id="tel" name="tel" type="tel"'
                             ' value="" />')

    def test_url_field(self):
        with self.app.test_request_context():
            form = MyForm()
            self.assertEqual(form.url(),
                             '<input id="url" name="url" type="url"'
                             ' value="" />')

    def test_email_field(self):
        with self.app.test_request_context():
            form = MyForm()
            self.assertEqual(form.email(),
                             '<input id="email" name="email" type="email"'
                             ' value="" />')

    def test_date_time_field(self):
        with self.app.test_request_context():
            form = MyForm()
            self.assertEqual(form.date_time(),
                             '<input id="date_time" name="date_time"'
                             ' type="datetime" value="" />')

    def test_date_field(self):
        with self.app.test_request_context():
            form = MyForm()
            self.assertEqual(form.date(),
                             '<input id="date" name="date" type="date"'
                             ' value="" />')

    def test_date_time_local_field(self):
        with self.app.test_request_context():
            form = MyForm()
            self.assertEqual(form.date_time_local(),
                             '<input id="date_time_local"'
                             ' name="date_time_local" type="datetime-local"'
                             ' value="" />')

    def test_integer_field(self):
        with self.app.test_request_context():
            form = MyForm()
            self.assertEqual(form.integer(),
                             '<input id="integer" name="integer" step="1"'
                             ' type="number" value="" />')

    def test_decimal_field(self):
        with self.app.test_request_context():
            form = MyForm()
            self.assertEqual(form.decimal(),
                             '<input id="decimal" name="decimal" step="any"'
                             ' type="number" value="" />')

    def test_integer_range_field(self):
        with self.app.test_request_context():
            form = MyForm()
            self.assertEqual(form.integer_range(),
                             '<input id="integer_range" name="integer_range"'
                             ' step="1" type="range" value="" />')

    def test_decimal_range_field(self):
        with self.app.test_request_context():
            form = MyForm()
            self.assertEqual(form.decimal_range(),
                             '<input id="decimal_range" name="decimal_range"'
                             ' step="any" type="range" value="" />')
