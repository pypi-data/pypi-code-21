# -*- coding:utf-8 -*-
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import FormView

__author__ = 'denishuang'
from . import helper, forms


@csrf_exempt
def ports(request):
    echostr = request.GET.get("echostr")
    api = helper.api
    flag = api.check_tencent_signature(request)
    if flag:
        um = api.deal_post(request.body)
        if um:
            response = HttpResponse(api.response_user(um), "text/xml; charset=utf-8")
            response._charset = "utf-8"
            return response
    return HttpResponse(echostr)


@csrf_exempt
def notice(request):
    return HttpResponse(helper.api.pay_result_notify(request.body))


class TestPayView(FormView):
    template_name = "wechat/mp/test_pay.html"
    form_class = forms.PayInfoForm

    def get_initial(self):
        import time
        return {"title": u"iphone 6手机", "orderId": int(time.time()), "detail": u"土豪金,128G内存", "totalFee": 0.01,
                "notifyUrl": helper.PAID_NOTIFY_URL}

    def form_valid(self, form):
        context = self.get_context_data()
        context['form'] = form
        wxuser = self.request.user.wxusers.first()
        data = helper.api.order(wxuser and wxuser.openId,
                                form.cleaned_data['orderId'],
                                form.cleaned_data['title'],
                                form.cleaned_data['totalFee'],
                                self.request.META['REMOTE_ADDR'],
                                detail=form.cleaned_data['detail'],
                                notifyUrl=form.cleaned_data['notifyUrl']
                                )
        context['JSPayParams'] = helper.api.get_jspay_params(data.get("prepay_id"))
        return self.render_to_response(context)
