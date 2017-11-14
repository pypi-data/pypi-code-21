# -*- mode: python; encoding: utf-8 -*-
#
# Copyright 2012 Jens Lindström, Opera Software ASA
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

import base
import background
import syntaxhighlight

from textutils import indent

class HighlightBackgroundServiceError(base.ImplementationError):
    def __init__(self, message):
        super(HighlightBackgroundServiceError, self).__init__(
            "Highlight background service failed: %s" % message)

def requestHighlights(repository, sha1s, mode, async=False):
    requests = [
        {
            "repository_path": repository.path,
            "sha1": sha1,
            "path": path,
            "language": language,
            "mode": mode
        }
        for sha1, (path, language) in sha1s.items()
        if not syntaxhighlight.isHighlighted(sha1, language, mode)
    ]

    if not requests:
        return False

    response = background.utils.issue_command(
        "highlight", {"requests": requests, "async": async})

    if async:
        return True

    if response["status"] == "error":
        raise HighlightBackgroundServiceError(response["error"])

    errors = []

    for result in response["results"]:
        if "failure" in result:
            errors.append(result["failure"])

    if errors:
        raise HighlightBackgroundServiceError(
            "one or more requests failed:\n%s" % "\n".join(map(indent, errors)))

    return True
