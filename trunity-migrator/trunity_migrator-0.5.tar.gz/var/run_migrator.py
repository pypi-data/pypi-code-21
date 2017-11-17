# Run this to test trunity-migrator

import importlib.util

from trunity_migrator.migrator import Migrator
from trunity_migrator.html_fixer import HTMLFixer
from trunity_migrator.fixers import *


path_to_settings = '/home/hunting/projects/trunity_migrator/var/settings.py'

spec = importlib.util.spec_from_file_location("settings.py", path_to_settings)
settings = importlib.util.module_from_spec(spec)
spec.loader.exec_module(settings)

html_fixer = HTMLFixer(settings=settings)

migrator = Migrator(
        trunity_2_login=settings.TRUNITY_2_LOGIN,
        trunity_2_password=settings.TRUNITY_2_PASSWORD,
        trunity_3_login=settings.TRUNITY_3_LOGIN,
        trunity_3_password=settings.TRUNITY_3_PASSWORD,
        t2_book_title=settings.TRUNITY_2_BOOK_NAME,
        t3_book_title=settings.TRUNITY_3_BOOK_NAME,
        html_fixer=html_fixer,
    )


migrator.migrate_book()
