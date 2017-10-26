# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import mozlog


def get_logger():
    structured_logger = mozlog.get_default_logger("marionette.driver")

    if structured_logger is None:
        return mozlog.unstructured.getLogger('marionette.driver')

    return structured_logger
