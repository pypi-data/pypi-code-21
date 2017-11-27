

from django_framework.django_helpers.meta_helpers.meta_registry import register_meta

from django_framework.django_helpers.meta_helpers import BaseMeta

class BasicProfileRunMeta(BaseMeta):
    
    ALLOWED_DEFAULT = ['GET', 'PUT', 'POST', 'DELETE'] # not allowed to directly POST, should use special endpoints for that!
    ALLOWED_ADMIN   = ['GET', 'PUT', 'POST', 'DELETE']


register_meta(BasicProfileRunMeta)
