# This file is a part of the AnyBlok / Pyramid / Beaker project
#
#    Copyright (C) 2016 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.


def anyblok_init_config(unittest=False):
    from anyblok.config import Configuration  # noqa for import order
    from anyblok_pyramid.config import Configuration  # noqa for import order
    from . import config  # noqa to update configuration
