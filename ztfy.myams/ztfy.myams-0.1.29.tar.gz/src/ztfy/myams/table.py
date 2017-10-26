#
# Copyright (c) 2014 Thierry Florac <tflorac AT onf.fr>
# All Rights Reserved.
#


# import standard packages

# import Zope3 interfaces

# import local interfaces

# import Zope3 packages
from z3c.table.table import Table

# import local packages


class BaseTable(Table):
    """Custom table"""

    data_attributes = {}

    batchSize = 10000
    startBatchingAt = 10000

    @staticmethod
    def checkDataAttribute(attribute, source):
        if isinstance(attribute, (str, unicode)):
            return attribute
        elif callable(attribute):
            return attribute(source)
        else:
            return str(attribute)

    def getDataAttributes(self, element, source, column=None):
        attrs = self.data_attributes.get(element)
        if attrs:
            return ' '.join("%s='%s'" % (item[0], self.checkDataAttribute(item[1], source)) for item in attrs.iteritems())
        else:
            return ''

    def renderTable(self):
        return super(BaseTable, self).renderTable() \
                                     .replace('<table', '<table %s' % self.getDataAttributes('table', self))

    def renderRow(self, row, cssClass=None):
        return super(BaseTable, self).renderRow(row, cssClass) \
                                     .replace('<tr', '<tr %s' % self.getDataAttributes('tr', row[0][0]))

    def renderCell(self, item, column, colspan=0):
        return super(BaseTable, self).renderCell(item, column, colspan) \
                                     .replace('<td', '<td %s' % self.getDataAttributes('td', item, column))
