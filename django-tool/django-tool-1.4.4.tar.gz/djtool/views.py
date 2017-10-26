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

    def post(self, request):

        try:
            mobile = request.POST.get('mobile')
            assert mobile
            mns.sms(settings.SMS_SIGN_NAME, settings.SMS_TEMPLATE_CODE)
            code = random.randint(1000, 9999)
            mns.send(mobile, {'code': code})
            request.session['sms_mobile'] = mobile
            request.session['sms_code'] = code
            return JsonResponse(self.msg(20004))
        except AssertionError:
            return JsonResponse(self.msg(50004))
        except TypeError:
            return JsonResponse(self.msg(50010))
        except AttributeError:
            raise Exception('请配置SMS_SIGN_NAME和SMS_TEMPLATE_CODE')
