#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from gitwebui.main import app
from gitwebui.blueprint import BlueGitWebUi, MULTI_REPOS

app.config['REPO_ROOT'] = os.getenv('GITWEBUI_REPO', '/var/lib/git')
app.register_blueprint(BlueGitWebUi(mode=MULTI_REPOS, viewonly=True))