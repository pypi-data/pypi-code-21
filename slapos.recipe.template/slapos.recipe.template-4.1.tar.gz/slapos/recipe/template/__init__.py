##############################################################################
#
# Copyright (c) 2010 Vifib SARL and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################
import os

import zc.buildout

class Recipe(object):
  def __init__(self, buildout, name, options):
    download = zc.buildout.download.Download(buildout['buildout'],
                hash_name=True)
    path, is_temp = download(options.pop('url'),
        md5sum=options.get('md5sum'))

    self.mode = None
    if 'mode' in options:
      # Mode is in octal notation
      self.mode = int(options['mode'], 8)

    hidden_option = '__template_content_%s__' % name

    with open(path) as inputfile:
      self.output_content = '$'.join(options._sub(s, None)
        for s in inputfile.read().split('$$'))

    self.output_filename = options['output']

  def install(self):
    with open(self.output_filename, 'w') as outputfile:
      outputfile.write(self.output_content)

    if self.mode is not None:
      os.chmod(self.output_filename, self.mode)

    return self.output_filename

  def update(self):
    return self.install()
