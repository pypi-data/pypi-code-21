from Acquisition import aq_parent
from collective.z3cform.datagridfield.datagridfield import DataGridFieldObjectSubForm
from ftw.referencewidget.browser.utils import get_root_path_from_source
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from Products.Five import BrowserView
import json


class GeneratePathbar(BrowserView):

    def __call__(self):
        widget = self.context

        if isinstance(self.context.form, DataGridFieldObjectSubForm):
            widget.context = self.context.__parent__.context

        mtool = getToolByName(widget.context, 'portal_membership')

        originpoint = self.request.get('origin', None)
        if not originpoint:
            originpoint = widget.get_start_path()

        if isinstance(originpoint, unicode):
            originpoint = originpoint.encode('utf-8')

        obj = widget.context.unrestrictedTraverse(originpoint)
        results = []

        root_path = get_root_path_from_source(widget)

        while True:
            clickable = mtool.checkPermission('View', obj)
            path = '/'.join(obj.getPhysicalPath())
            results.insert(0, {'title': obj.Title(),
                               'path': path,
                               'clickable': bool(clickable)})

            if root_path and root_path == path:
                break
            elif IPloneSiteRoot.providedBy(obj):
                break
            else:
                obj = aq_parent(obj)
        self.request.RESPONSE.setHeader("Content-type", "application/json")
        return json.dumps(results)
