#!/usr/bin/env python
# -*- coding: utf-8 -*-

__version__ = "0.0.4"
__short_description__ = "A Task Queue Scheduler Framework."
__license__ = "MIT"
__author__ = "Sanhe Hu"
__author_email__ = "husanhe@gmail.com"
__maintainer__ = "Sanhe Hu"
__maintainer_email__ = "husanhe@gmail.com"
__github_username__ = "MacHu-GWU"

try:
    from .task import Task
    from .scheduler import BaseScheduler, BaseDBTableBackedScheduler
    from .scheduler_sqlitedict import SqliteDictScheduler
    from .scheduler_mongodb import MongoDBScheduler
    from .scheduler_status_flag import StatusFlagScheduler
    from .pkg import loggerFactory
except ImportError:  # pragma: no cover
    pass
