"""Extends mitmproxy's onboarding app to include some fizzgun features"""

import os

import tornado.template
import tornado.web
from mitmproxy.addons.onboardingapp import app

import fizzgun.util


def setup(reports_path):
    app.loader = tornado.template.Loader(fizzgun.util.fizzgun_path('data', 'templates'))
    app.application.add_handlers(".*$", [
        (r'/reports/', DirectoryIndexHandler, {'reports_path': reports_path}),
        (r'/reports/(.*)', tornado.web.StaticFileHandler, {'path': reports_path})
    ])


class DirectoryIndexHandler(tornado.web.RequestHandler):

    def initialize(self, reports_path):
        self._reports_path = reports_path

    def get(self):
        files = os.listdir(self._reports_path)
        t = app.loader.load("directory.html")
        self.write(t.generate(files=files))
