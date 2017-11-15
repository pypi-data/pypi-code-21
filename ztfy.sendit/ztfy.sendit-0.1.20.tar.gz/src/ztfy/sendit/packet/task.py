### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2013 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################


# import standard packages
from datetime import datetime

# import Zope3 interfaces
from hurry.query.interfaces import IQuery

# import local interfaces
from ztfy.sendit.packet.interfaces import IPacketArchiverTask

# import Zope3 packages
from hurry.query.query import And
from hurry.query.value import Eq, Le
from zope.component import getUtility
from zope.interface import implements
from zope.traversing.api import getParent, getName

# import local packages
from ztfy.scheduler.task import BaseTask
from ztfy.security.search import getPrincipal
from ztfy.utils.size import getHumanSize
from ztfy.utils.timezone import tztime
from ztfy.utils.request import newParticipation, endParticipation
from zope.schema.fieldproperty import FieldProperty


class PacketArchiverTask(BaseTask):
    """Packet archiver task"""

    implements(IPacketArchiverTask)

    principal_id = FieldProperty(IPacketArchiverTask['principal_id'])

    def run(self, report):
        newParticipation(self.principal_id)
        try:
            query = getUtility(IQuery)
            params = []
            params.append(Eq(('Catalog', 'content_type'), 'IPacket'))
            params.append(Le(('Catalog', 'expiration_date'), tztime(datetime.utcnow())))
            for packet in query.searchResults(And(*params)):
                user = getParent(packet)
                report.write("Removing packet: %s\n" % packet.title)
                owner = getPrincipal(user.owner)
                report.write(" - owner: %s (%s)\n" % (owner.title, owner.id))
                report.write(" - recipients:\n%s\n" % '\n'.join(('    > %s' % getPrincipal(recipient).title for recipient in packet.recipients.split(','))))
                packet_size = sum((document.data.getSize() for document in packet.values()))
                report.write(" - %d document(s) removed (%s)\n" % (len(packet.values()),
                                                                   getHumanSize(packet_size)))
                report.write('--------------------\n')
                parent = getParent(packet)
                del parent[getName(packet)]
        finally:
            endParticipation()
