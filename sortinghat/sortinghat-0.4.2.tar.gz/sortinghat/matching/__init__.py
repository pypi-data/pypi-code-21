# -*- coding: utf-8 -*-
#
# Copyright (C) 2014-2017 Bitergia
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# Authors:
#     Santiago Dueñas <sduenas@bitergia.com>
#

from __future__ import absolute_import
from __future__ import unicode_literals

from .email import EmailMatcher
from .email_name import EmailNameMatcher
from .github import GitHubMatcher
from .username import UsernameMatcher


SORTINGHAT_IDENTITIES_MATCHERS = {
                                  'default'    : EmailMatcher,
                                  'email'      : EmailMatcher,
                                  'email-name' : EmailNameMatcher,
                                  'github'     : GitHubMatcher,
                                  'username'   : UsernameMatcher
                                  }
