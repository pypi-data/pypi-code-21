# -*- coding: utf-8
import os
import logging
from django.apps import AppConfig
logger = logging.getLogger(__name__)


class ChaosConfig(AppConfig):
    name = 'chaos'

    def _create_directory(self, path):
        """
        Safely creates a directory for you.
        """
        if not os.path.isdir(path):
            try:
                os.makedirs(path)
            except Exception as ex:
                message = ex.message if hasattr(ex, 'message') else ''
                logger.error(
                    'error while creating directory %s. error: %s',
                    path,
                    message,
                    exc_info=True
                )

    def ready(self):
        from django.conf import settings
        CHAOS_EXPORT_PATH = (settings.CHAOS_EXPORT_PATH
                             if hasattr(settings, 'CHAOS_EXPORT_PATH')
                             else os.path.join(settings.MEDIA_ROOT, 'export', 'chaos'))
        self._create_directory(CHAOS_EXPORT_PATH)
