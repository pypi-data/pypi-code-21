from Products.CMFCore.utils import getToolByName
from Products.PlonePAS.tools.membership import MembershipTool


orig = MembershipTool.getMemberInfo


def getMemberInfo(self, *args, **kwargs):
    info = orig(self, *args, **kwargs)
    if not isinstance(info, dict):
        return info
    home_page = info.get('home_page', '')
    if not home_page or not isinstance(home_page, basestring):
        return info
    if home_page.startswith('http'):
        return info
    # Suspicious.  But if it is internal, it is fine.
    urltool = getToolByName(self, 'portal_url')
    if urltool.isURLInPortal(home_page):
        return info
    # We do not trust this url, so empty it.
    info['home_page'] = ''
    return info

getMemberInfo.__doc__ = orig.__doc__
MembershipTool.getMemberInfo = getMemberInfo
