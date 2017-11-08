try:
    from App.ImageFile import ImageFile
    misc_ = {'method.gif': ImageFile('www/method.gif', globals())}
except ImportError:
    pass

def initialize(context):
    from AccessControl.Permissions import view_management_screens
    import Method
    context.registerClass(
        Method.ZSPARQLMethod,
        permission=view_management_screens,
        constructors=(Method.manage_addZSPARQLMethod_html,
                      Method.manage_addZSPARQLMethod),
    )
