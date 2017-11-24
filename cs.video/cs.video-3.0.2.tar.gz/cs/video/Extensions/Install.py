
from StringIO import StringIO

from Products.Archetypes.Extensions.utils import install_subskin
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import getFSVersionTuple

from cs.video.config import GLOBALS

def install(self, reinstall=False):
    out = StringIO()

    tool=getToolByName(self, "portal_setup")

    if not reinstall:
        install_subskin(self, out, GLOBALS, 'skins')

    if getFSVersionTuple()[:3]>=(3,0,0):
        tool.runAllImportStepsFromProfile(
            "profile-cs.video:default",
            purge_old=False)
    else:
        plone_base_profileid = "profile-CMFPlone:plone"
        tool.setImportContext(plone_base_profileid)
        tool.setImportContext("profile-cs.video:default")
        tool.runAllImportSteps(purge_old=False)
        tool.setImportContext(plone_base_profileid)

    print >> out, "cs.video successfully installed"

    return out.getvalue()
    
def uninstall(self):
    out = StringIO()
    uninstall_subskin(self, out, 'video_templates')       
    return out.getvalue()


def uninstall_subskin(self, out, skinlayer):
    skinstool=getToolByName(self, 'portal_skins')
    for skinName in skinstool.getSkinSelections():
        path = skinstool.getSkinPath(skinName)
        layers_list = [i.strip() for i in  path.split(',')]
        if skinlayer in layers_list:
            layers_list.remove(skinlayer)
        else:
            print "Warning: '"+skinlayer+"' layer already removed from '"+skinName+"' skin"
        path = ','.join(layers_list)
        skinstool.addSkinSelection(skinName, path)
