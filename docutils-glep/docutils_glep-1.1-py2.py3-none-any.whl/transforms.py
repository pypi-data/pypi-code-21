# docutils GLEP support
# Copyright (c) 2017 Gentoo Foundation
# Placed in public domain
# based on PEP code by:
#
# Author: David Goodger
# Contact: goodger@users.sourceforge.net
# Revision: $Revision: 1.1 $
# Date: $Date: 2004/07/20 18:23:59 $
# Copyright: This module has been placed in the public domain.

"""
Transforms for PEP processing.

- `Headers`: Used to transform a PEP's initial RFC-2822 header.  It remains a
  field list, but some entries get processed.
- `Contents`: Auto-inserts a table of contents.
"""

__docformat__ = 'reStructuredText'

import datetime
import os
import re
import time
from docutils import nodes, utils, DataError
from docutils.transforms.peps import Headers, mask_email


required_fields = frozenset((
    'GLEP',
    'Title',
    'Author',
    'Type',
    'Status',
    'Version',
    'Created',
    'Last-Modified',
    'Post-History',
    'Content-Type'))

optional_fields = frozenset((
    'Requires',
    'Replaces',
    'Replaced-By'))

valid_types = frozenset((
    'Informational',
    'Standards Track'))

valid_statuses = frozenset((
    'Draft',
    'Active',
    'Accepted',
    'Deferred',
    'Withdrawn',
    'Rejected',
    'Final',
    'Replaced',
    'Moribund'))

version_regex = re.compile('\d+(\.\d+)?')


class GLEPHeaders(Headers):

    """
    Process fields in a GLEP's initial RFC-2822 header.
    """

    pep_url = 'https://www.gentoo.org/glep/glep-%04d.html'

    def apply(self):
        """Override.

        Replaces the first field requirement ('glep' field) and some
        error messages, and changes the link to the content-type spec
        from pep 12 to glep-0002.
        """
        if not len(self.document):
            # @@@ replace these DataErrors with proper system messages
            raise DataError('Document tree is empty.')
        header = self.document[0]
        if not isinstance(header, nodes.field_list) or \
              'rfc2822' not in header['classes']:
            raise DataError('Document does not begin with an RFC-2822 '
                            'header; it is not a GLEP.')
        header['classes'].extend(('table-bordered', 'table-condensed',
            'table-striped', 'pull-right'))
        pep = None
        for field in header:
            if field[0].astext().lower() == 'glep': # should be the first field
                value = field[1].astext()
                try:
                    pep = int(value)
                except ValueError:
                    pep = value
                    msg = self.document.reporter.warning(
                        '"GLEP" header must contain an integer; "%s" is an '
                        'invalid value.' % pep, base_node=field)
                    msgid = self.document.set_id(msg)
                    prb = nodes.problematic(value, value or '(none)',
                                            refid=msgid)
                    prbid = self.document.set_id(prb)
                    msg.add_backref(prbid)
                    if len(field[1]):
                        field[1][0][:] = [prb]
                    else:
                        field[1] += nodes.paragraph('', '', prb)
                break
        if pep is None:
            raise DataError('Document does not contain an RFC-2822 "GLEP" '
                            'header.')
        if len(header) < 2 or header[1][0].astext().lower() != 'title':
            raise DataError('No title!')
        seen = set()
        for field in header:
            name = field[0].astext()
            if name not in required_fields and name not in optional_fields:
                raise DataError('Incorrect GLEP header field: %s' % name)
            seen.add(name)

            body = field[1]
            if len(body) > 1:
                raise DataError('GLEP header field body contains multiple '
                                'elements:\n%s' % field.pformat(level=1))
            elif len(body) == 1:
                if not isinstance(body[0], nodes.paragraph):
                    raise DataError('GLEP header field body may only contain '
                                    'a single paragraph:\n%s'
                                    % field.pformat(level=1))
            else:
                # empty
                continue
            para = body[0]
            if name == 'Author':
                for node in para:
                    if isinstance(node, nodes.reference):
                        node.replace_self(mask_email(node))
            elif name == 'Type':
                if para.astext() not in valid_types:
                    raise DataError('Invalid GLEP type: %s' % para.astext())
            elif name == 'Status':
                if para.astext() not in valid_statuses:
                    raise DataError('Invalid GLEP status: %s' % para.astext())
            elif name == 'Version':
                v = para.astext()
                if not version_regex.match(v):
                    raise DataError('Invalid GLEP version: %s' % para.astext())
            elif name in ('Created', 'Last-Modified'):
                try:
                    datetime.datetime.strptime(para.astext(), '%Y-%m-%d')
                except ValueError:
                    raise DataError('Invalid ISO8601 date in %s: %s' % (name, para.astext()))
            elif name == 'Post-History':
                for v in para.astext().split(','):
                    try:
                        datetime.datetime.strptime(v.strip(), '%Y-%m-%d')
                    except ValueError:
                        raise DataError('Invalid ISO8601 date in %s: %s' % (name, v.strip()))
            elif name in ('Replaces', 'Replaced-By', 'Requires'):
                newbody = []
                space = nodes.Text(' ')
                for refpep in re.split(',?\s+', body.astext()):
                    pepno = int(refpep)
                    newbody.append(nodes.reference(
                        refpep, refpep,
                        refuri=self.pep_url % pepno))
                    newbody.append(space)
                para[:] = newbody[:-1] # drop trailing space
            elif name == 'Content-Type':
                pep_type = para.astext()
                if pep_type != 'text/x-rst':
                    raise DataError('Incorrect Content-Type: %s' % pep_type)
                para[:] = [nodes.reference('', pep_type, refuri=(self.pep_url % 2))]

        if required_fields - seen:
            raise DataError('Missing GLEP header field(s): %s' % ', '.join(required_fields - seen))
