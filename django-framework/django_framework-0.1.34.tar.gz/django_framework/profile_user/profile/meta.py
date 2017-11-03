

from django_framework.django_helpers.meta_helpers.meta_registry import register_meta


from django_framework.django_helpers.meta_helpers import BaseMeta

class ProfileMeta(BaseMeta):
    
    ALLOWED_DEFAULT = ['GET'] # not allowed to directly POST, should use special endpoints for that!
    ALLOWED_ADMIN   = ['GET']
    
    
    DEFAULT_ALLOWED_ACTIONS_UNAUTHENTICATED = [] # if not authenticated, what methods are allowed? -- typically ['GET']



register_meta(ProfileMeta)



