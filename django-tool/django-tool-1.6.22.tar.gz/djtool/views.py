from djtool.review import View
from django.http import JsonResponse
from django.core.cache import cache
from django.conf import settings


class SignOutView(View):
    def post(self, request, *args, **kwargs):
        try:
            del request.session['login']
            cache.set('admin%s' % request.admin.unionuuid, 0)
            response = JsonResponse(self.msg(20000))
        except:
            response = JsonResponse(self.msg(50000))
        response.delete_cookie('_login', domain=settings.COOKIE_DOMAIN)
        return response
