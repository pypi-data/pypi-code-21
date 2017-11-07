# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

from __future__ import unicode_literals

import logging
import django

LOGGER = logging.getLogger('tcell_agent').getChild(__name__)

isDjango15 = False
django15or16 = False
try:
    isDjango15 = django.get_version().startswith('1.5')
except:
    LOGGER.warn("Could not determine Django version for compatibility tests")


def midVersionGreaterThanOrEqualTo(version_string):
    try:
        django_midv = django.get_version().split(".")[:2]
        comparison_midv = version_string.split(".")[:2]
        if int(django_midv[0]) >= int(comparison_midv[0]) and int(django_midv[1]) >= int(comparison_midv[1]):
            return True
    except:
        LOGGER.warn("Could not determine Django midversion for compatibility tests")
    return False


try:
    django15or16 = isDjango15 or django.get_version().startswith('1.6')
except:
    LOGGER.warn("Could not determine Django version for compatibility tests")
