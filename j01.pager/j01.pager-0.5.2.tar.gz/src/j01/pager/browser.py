##############################################################################
#
# Copyright (c) 2010 Projekt01 GmbH and Contributors.
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
"""
$Id:$
"""

from zope.traversing.browser import absoluteURL
from zope.security.proxy import removeSecurityProxy

from z3c.template.template import getPageTemplate

from j01.jsonrpc import jspage

# document ready makes sure that we start rendering the pager after page get
# rendered. This allows to calculate the right width if the pager is used in a
# table
j01_pager_template = """
<script type="text/javascript">
  $(document).ready(function(){
    $("%(expression)s").j01Pager({%(settings)s});
  });
</script>
"""

j01_pager_adhoc_template = """
<script type="text/javascript">
  $("%(expression)s").j01Pager({%(settings)s});
</script>
"""


def j01PagerJavaScript(data, j01PagerDocumentReady=True):
    """Paginate generator knows how to generate a pagination JS code.

    The data argument allows you to set custom key, value pairs.
    """
    if data.get('url') is None:
        raise KeyError("Missing url")

    try:
        pagerExpression = data.pop('pagerExpression')
    except KeyError, e:
        pagerExpression = '#j01Pager'

    lines = []
    append = lines.append
    for key, value in data.items():
        if key in ['onClick', 'callback']:
            if not value:
                # skip if empty, use default defined in JS
                pass
            else:
                append("\n    %s: %s" % (key, value))
        elif key in ['onAfterRender', 'onAfterSetResult']:
            if value == False:
                append("\n    %s: false" % key)
            else:
                append("\n    %s: %s" % (key, value))
        elif value is True:
            append("\n    %s: true" % key)
        elif value is False:
            append("\n    %s: false" % key)
        elif value is None:
            append("\n    %s: null" % key)
        elif isinstance(value, int):
            append("\n    %s: %s" % (key, value))
        elif isinstance(value, basestring):
            append("\n    %s: '%s'" % (key, str(value)))
        else:
            raise ValueError("Unknown key, value given %s:%s" % (key, value))
    settings = ','.join(lines)

    if j01PagerDocumentReady:
        # render with document ready. This is the default option and allows to
        # include the javascript in the footer. But it can't render pager
        # loaded with JSON-RPC
        template = j01_pager_template
    else:
        # render inplace. This option must get used if the page containing the
        # pager get loaded with JSON-RPC
        template = j01_pager_adhoc_template

    return template % ({'expression': pagerExpression,
                                  'settings': settings})


class J01PagerCore(object):
    """J01Pager base class used for JSON-RPC and Browser pages.

    Note: This class must get used within a class which offers an update
    methods. The concept works with simple browser pages, forms or JSON-RPC
    pages and forms offered from j01.jsonrpc.

    There is also built in live search support based on a search text widget
    defined within the j01PagerSearchWidgetExpression property. Just provide a
    widget name and the JavaScript will do the relevant calls if someone will
    type some letters. You just ahve to implement your own live search text
    field.

    Usage:

    - implement your own mixin class based on J01PagerCore

    - register a named template called j01Pager for your new mixin class

    - implement a JSONRPC method inherited from your mixin class and
      J01PagerResult

    - implement a JSONRPC page inherited from your own mixin class and
      jspage.JSONRPCPage or jsform.JSONRPCForm

    Sample:

    import j01.jsonrpc import jspage
    import j01.pager.browser import J01PagerCore
    import j01.pager.jsonrpc import J01PagerResult

    class MyPagerMixin(J01PagerCore):

        j01PagerMethodName = 'getMyResult'

        @property
        def j01PagerValues(self):
            for d in self.cursor:
                yield {'title': d.get('title')}

    class MyPager(MyPagerPagerMixin, jspage.JSONRPCPage):
        pass

    class MyPagerResult(MyPagerPagerMixin, J01PagerResult):

        def getMyResult(self, page=1, batchSize=10, sortName=None,
            sortOrder=None, searchString=None):
            return self.getJ01PagerResult(page, batchSize, sortName, sortOrder,
                searchString)

    <!-- named j01Pager template used in MyPager and MyPagerResult -->
    <z3c:template
        name="j01Pager"
        template="pager.pt"
        for=".browser.MyPagerMixin"
        layer="my.layer.IMyLayer"
        />

    <!-- page -->
    <z3c:pagelet
        name="index.html"
        for="my.interfaces.IMyContext"
        class=".browser.MyPager"
        layer="my.layer.IMyLayer"
        permission="my.Permission"
        />

    <z3c:template
        template="page.pt"
        for=".browser.MyPager"
        layer="xpo.layer.IBaseLayer"
        />

    <!-- jsonrpc pager batch method -->
    <z3c:jsonrpc
        for="my.interfaces.IMyContext"
        class=".browser.MyPagerResult"
        methods="getMyResult"
        layer="my.layer.IMyLayer"
        permission="my.Permission"
        />

    """

    j01PagerTemplate = getPageTemplate('j01Pager')

    # internals
    j01PageTotal = 0
    j01PagerContext = None
    _j01PagerURL = None
    cursor = None # iterable batching data

    # implement this attributes as session properties
    j01Page = 1
    j01Pages = 0
    j01PagerSortName = None
    j01PagerSortOrder = None
    j01PagerSortOrderMapping = {} # request string to order value maping

    # search query support
    j01PagerQuery = None
    j01PagerSearchString = None

    # render javascript on document ready
    j01PagerDocumentReady = True

    # expressions
    j01PagerExpression = '#j01Pager'
    j01PagerResultExpression = '#j01PagerResult'

    # JSON-RPC method name
    j01PagerMethodName = 'getJ01PagerResult'

    # sizes
    j01PagerBatchSize = 10
    j01PagerDisplaySize = 10

    # CSS colors
    j01PagerTextColor = '#FF6600'
    j01PagerTextHoverColor = '#CC0000'
    j01PagerBGColor = None
    j01PagerBGHoverColor = None

    # JS event handler
    j01PagerOnClick = False # will use built-in 'doLoadContent' JS method
    j01PagerOnAfterRender = False
    j01PagerOnAfterSetResult = False
    j01PagerRotate = True
    j01PagerMouse = 'press'

    # optional livesearch support
    j01PagerSearchWidgetExpression = None
    j01MaxReSearch = 0
    j01PagerMinQueryLenght = 2

    @property
    def j01PagerConfig(self):
        return {
            'pagerExpression': self.j01PagerExpression,
            'resultExpression': self.j01PagerResultExpression,
            'methodName': self.j01PagerMethodName,
            'url': self.j01PagerURL,
            'count': self.j01Pages,
            'start': self.j01Page,
            # sizes
            'batchSize': self.j01PagerBatchSize,
            'display': self.j01PagerDisplaySize,
            # css colors
            'bgColor': self.j01PagerBGColor,
            'bgHoverColor': self.j01PagerBGHoverColor,
            'textColor': self.j01PagerTextColor,
            'textHoverColor': self.j01PagerTextHoverColor,
            # JS event handler
            'onClick': self.j01PagerOnClick,
            'onAfterRender': self.j01PagerOnAfterRender,
            'onAfterSetResult': self.j01PagerOnAfterSetResult,
            'rotate': self.j01PagerRotate,
            'mouse': self.j01PagerMouse,
            # pager condition
            'showPager': self.showJ01Pager,
            # order support
            'sortName': self.j01PagerSortName,
            'sortOrder': self.j01PagerSortOrder,
            # live search support
            'searchWidgetExpression': self.j01PagerSearchWidgetExpression,
            'maxReSearch': self.j01MaxReSearch,
            'minQueryLenght': self.j01PagerMinQueryLenght}

    @property
    def j01PagerContext(self):
        return self.context

    @property
    def j01PagerBatchContext(self):
        return self.j01PagerContext

    @property
    def j01PagerURL(self):
        if self._j01PagerURL is None:
            self._j01PagerURL = absoluteURL(self.j01PagerContext, self.request)
        return self._j01PagerURL

    @property
    def showJ01Pager(self):
        return self.j01PageTotal > self.j01PagerBatchSize

    @property
    def j01PagerBatchArguments(self):
        """Get new or default page batch data method arguments"""
        page = self.request.get('page', self.j01Page)
        batchSize = self.request.get('batchSize', self.j01PagerBatchSize)
        sortName = self.request.get('sortName', self.j01PagerSortName)
        sortOrder = self.request.get('sortOrder', self.j01PagerSortOrder)
        searchString = self.request.get('searchString', self.j01PagerSearchString)
        return page, batchSize, sortName, sortOrder, searchString

    # cursor properties
    @property
    def j01Pager(self):
        """Setup and return pager batch content

        Note: we setup the j01Pager content not during update the page or form,
        we just do it right before we use them during the render call. This
        allows us to manipulate all relevant pager attributes e.g. j01Page,
        j01PagerBatchSize etc. during form processing or anything else happens
        during update call. Feel free to setup the pager batch data earlier
        in your implementation. As you can see, by default, if the cursor is
        not None, we will skip the pager batch data setup.
        """
        if self.cursor is None:
            # J01PagerResult already called setUpJ01PagerBatchData and created
            # the cursor. Just call this method for browser requests and
            # collect batch setting from request
            page, batchSize, sortName, sortOrder, searchString = \
                self.j01PagerBatchArguments
            self.setUpJ01PagerBatchData(page, batchSize, sortName, sortOrder,
                searchString)
        return self.j01PagerTemplate()

    # cursor setup
    def getJ01PagerQuery(self, page, batchSize, sortName=None,
        sortOrder=None, searchString=None, fields=None, skipFilter=False):
        """Hook for implement queries based on batch and serach criteria"""
        return self.j01PagerQuery

    def getJ01PagerBatchData(self, page, batchSize, sortName=None,
        sortOrder=None, searchText=None, fields=None, skipFilter=False):
        # Note: This method will fit out of the box for our m01.mongo
        # getBatchData implementation. If you like to you use another concept,
        # you need to implement getBatchData or use another method which can
        # return a tuple with the following values:
        # cursor, j01Page, j01Pages, j01PageTotal
        # see: setUpJ01PagerBatchData below for more infomation
        query = self.getJ01PagerQuery(page, batchSize, sortName, sortOrder,
            searchText)
        return self.j01PagerBatchContext.getBatchData(query, page, batchSize,
            sortName, sortOrder, searchText, fields, skipFilter)

    # setup cursor
    def setUpJ01PagerBatchData(self, page=None, batchSize=None, sortName=None,
        sortOrder=None, searchString=None):
        """Pager batch data setup

        We will setup the pager batch data after setup in our render method
        right before we call the render super method.
        This will make sure that our form actions can set new search text or
        other relevant data for batching.

        Note: this method is responsible for setup the relevant pager data
        used in our pager template. e.g. page, pages, total.

        """
        # set pager attributes or use defaults. You should implement this
        # attributes as session properties
        if page is not None:
            self.j01Page = int(page)

        if batchSize is not None:
            self.j01PagerBatchSize = int(batchSize)

        if sortName is not None:
            self.j01PagerSortName = sortName

        if sortOrder:
            self.j01PagerSortOrder = sortOrder

        if searchString is not None:
            self.j01PagerSearchString = searchString

        # setup pager batch data
        cursor, self.j01Page, self.j01Pages, self.j01PageTotal = \
            self.getJ01PagerBatchData(self.j01Page, self.j01PagerBatchSize,
                self.j01PagerSortName, self.j01PagerSortOrder,
                self.j01PagerSearchString)
        self.cursor = removeSecurityProxy(cursor)

    # return cursor
    @property
    def j01PagerValues(self):
        """Implement your own value iterator."""
        return self.cursor

    @property
    def j01PagerJavaScript(self):
        if self.showJ01Pager or self.j01PagerSearchWidgetExpression:
            return j01PagerJavaScript(self.j01PagerConfig,
                self.j01PagerDocumentReady)
        else:
            return u''

    def j01PagerUpdate(self):
        """Update additional pager page and jsonrpc data

        This is the only shared method which get called based on a browser and
        jsonrpc request. This means you should use this method if you need to
        setup properties which you normaly whould do in a BrowserPage update
        method.

        """
        pass

    def update(self):
        self.j01PagerUpdate()
        try:
            # set j01Page value or fail without error
            self.j01Page = int(self.request.get('j01Page'))
        except (TypeError, ValueError), e:
            pass
        super(J01PagerCore, self).update()


class J01PagerPage(J01PagerCore, jspage.JSONRPCPage):
    """JSONRPC based J01Pager page."""
