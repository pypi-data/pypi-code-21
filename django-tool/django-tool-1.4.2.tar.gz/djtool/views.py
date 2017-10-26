from djtool.review import View
from django.http import JsonResponse
from django.core.cache import cache
from djtool.mns import mns
from django.conf import settings
import six
import random


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


class SendView(View):

    def __init__(self, **kwargs):
        for key, value in six.iteritems(kwargs):
            setattr(self, key, value)
        try:
            self.sign_name = settings.SMS_SIGN_NAME
            self.template_code = settings.SMS_TEMPLATE_CODE
        except:
            raise Exception('请配置SMS_SIGN_NAME和SMS_TEMPLATE_CODE')

    def post(self, request):

        try:
            mobile = request.POST.get('mobile')
            assert mobile
            mns.sms(self.sign_name, self.template_code)
            code = random.randint(1000, 9999)
            mns.send(mobile, {'code': code})
            request.session['sms_mobile'] = mobile
            request.session['sms_code'] = code
            return JsonResponse(self.msg(20004))
        except:
            return JsonResponse(self.msg(50004))
