from djtool.review import View
from django.http import JsonResponse
from django.core.cache import cache


class SignOutView(View):
    def post(self, request, *args, **kwargs):
        try:
            del request.session['login']
            cache.set('admin%s' % request.admin.unionuuid, 0)
            response = JsonResponse(self.msg(20000))
        except:
            response = JsonResponse(self.msg(50000))
        clientid = request.META.get('INVOCATION_ID', '_login')
        response.delete_cookie(clientid, domain='yantuky.com')
        return response
