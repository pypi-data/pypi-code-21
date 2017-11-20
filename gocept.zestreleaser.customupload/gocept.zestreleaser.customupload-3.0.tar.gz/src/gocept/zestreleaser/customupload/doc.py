# Copyright (c) 2012 gocept gmbh & co. kg
# See also LICENSE.txt

from gocept.zestreleaser.customupload.upload import choose_destination
from gocept.zestreleaser.customupload.upload import read_configuration
import os
import os.path
import zest.releaser.utils


def upload(context):
    destination = choose_destination(
        context['name'], read_configuration('~/.zestreleaserrc'),
        'gocept.zestreleaser.customupload.doc')
    if not destination:
        return
    # XXX make configurable?
    if os.path.isfile('./bin/doc'):
        os.system('./bin/doc')
    if not zest.releaser.utils.ask('Upload documentation to %s' % destination):
        return
    # XXX make configurable?
    source = '/'.join([context['workingdir'], 'build', 'doc', ''])
    host, root = destination.split(':')
    directory = '/'.join([root, context['name']])
    os.system(' '.join(['ssh', host, 'mkdir', '-p', directory]))
    fullpath = '/'.join([destination, context['name'], context['version']])
    os.system(' '.join(['rsync', '-av', '--delete', source, fullpath]))
