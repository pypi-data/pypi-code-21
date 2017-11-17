from __future__ import unicode_literals

import logging

from rest_framework import serializers


logger = logging.getLogger(__name__)


def logged_validation_info(error_message):
    logger.info(error_message)
    raise serializers.ValidationError(error_message)


def logged_validation_error(error_message):
    logger.error(error_message)
    raise serializers.ValidationError(error_message)


def logged_validation_warning(error_message):
    logger.warning(error_message)
    raise serializers.ValidationError(error_message)