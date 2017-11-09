

from django_framework.django_helpers.meta_helpers.meta_registry import register_meta

from django_framework.django_helpers.meta_helpers import BaseMeta

class BasicTestRunRequireAuthMeta(BaseMeta):
    
    ALLOWED_DEFAULT = ['GET', 'PUT', 'POST', 'DELETE'] # not allowed to directly POST, should use special endpoints for that!
    ALLOWED_ADMIN   = ['GET', 'PUT', 'POST', 'DELETE']

    DEFAULT_REQUIRE_AUTHENTICATION = True # do you need to be an authenticated user to view anything?
    DEFAULT_ALLOWED_ACTIONS_UNAUTHENTICATED = [] # if not authenticated, what methods are allowed? -- typically ['GET']
    
    ADMIN_REQUIRE_AUTHENTICATION   = True # do admin endpoints require authentication
    


register_meta(BasicTestRunRequireAuthMeta)
