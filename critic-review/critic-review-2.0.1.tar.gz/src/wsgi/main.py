# -*- mode: python; encoding: utf-8 -*-
#
# Copyright 2017 the Critic contributors, Opera Software ASA
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License.  You may obtain a copy of
# the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  See the
# License for the specific language governing permissions and limitations under
# the License.

import logging

try:
    import maintenance.configtest
except ImportError:
    import traceback
    import sys

    exc_info = sys.exc_info()

    def application(environ, start_response):
        start_response("500 Internal Server Error",
                       [("Content-Type", "text/plain")])
        header = "Failed to import 'maintenance.configtest' module"
        return (["%s\n%s\n\n" % (header, "=" * len(header))] +
                traceback.format_exception(*exc_info))
else:
    errors, warnings = maintenance.configtest.testConfiguration()

    if errors:
        def application(environ, start_response):
            start_response("500 Internal Server Error",
                           [("Content-Type", "text/plain")])

            header = "Invalid system configuration"
            result = "%s\n%s\n\n" % (header, "=" * len(header))
            for error in errors:
                result += str(error) + "\n\n"
            for warning in warnings:
                result += str(warning) + "\n\n"

            return [result]
    else:
        try:
            import api

            with api.critic.startSession(for_system=True):
                settings = api.critic.settings()

            if settings.paths.coverage:
                import base.coverage
                def import_critic():
                    import wsgi.critic
                base.coverage.call("wsgi", import_critic)

            if settings.system.is_debugging:
                log_level = logging.DEBUG
            else:
                log_level = logging.WARNING

            logging.basicConfig(
                format="%(asctime)s - %(levelname)5s - %(name)s: %(message)s",
                level=log_level)

            import wsgi.critic
        except ImportError:
            import traceback
            import sys

            exc_info = sys.exc_info()

            def application(environ, start_response):
                start_response("500 Internal Server Error",
                               [("Content-Type", "text/plain")])
                header = "Failed to import 'wsgi.critic' module"
                return ([("%s\n%s\n\n" % (header, "=" * len(header))).encode()] +
                        [line.encode() for line in traceback.format_exception(*exc_info)])
        else:
            def application(environ, start_response):
                for item in wsgi.critic.main(environ, start_response):
                    yield item
