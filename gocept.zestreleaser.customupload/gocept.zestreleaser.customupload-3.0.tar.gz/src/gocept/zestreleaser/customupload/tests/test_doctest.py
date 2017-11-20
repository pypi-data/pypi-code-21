# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import doctest
import zest.releaser.tests.functional


def test_suite():
    return doctest.DocFileSuite(
        'integration.txt',
        'integration-doc.txt',
        setUp=zest.releaser.tests.functional.setup,
        tearDown=zest.releaser.tests.functional.teardown,
        optionflags=(doctest.ELLIPSIS +
                     doctest.NORMALIZE_WHITESPACE +
                     doctest.REPORT_NDIFF))
