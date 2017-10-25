from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse

try:
    from jnius import autoclass, cast
except:
    pass

import os



########################################################################
class open_url(View):
    """"""
    #----------------------------------------------------------------------
    def get(self, request):
        """Constructor"""

        url = request.GET.get('url', '')

        try:
            context = autoclass('org.renpy.android.PythonActivity').mActivity
            Uri = autoclass('android.net.Uri')
            Intent = autoclass('android.content.Intent')
            intent = Intent()
            intent.setAction(Intent.ACTION_VIEW)
            intent.setData(Uri.parse(url))
            currentActivity = cast('android.app.Activity', context)
            currentActivity.startActivity(intent)

            return JsonResponse({'success': True,})

        except:

            return JsonResponse({'success': False,})



########################################################################
class logs(View):
    """"""

    template = "djangoforandroid/logs.html"

    #----------------------------------------------------------------------
    def get(self, request):
        """"""
        stdout = os.environ.get('STDOUT', None)
        stderr = os.environ.get('STDERR', None)

        logs = {}

        if stdout and os.path.exists(stdout):
            logs['stdout'] = open(stdout).read()

        if stderr and os.path.exists(stderr):
            logs['stderr'] = open(stderr).read()

        logs = {"stdout": "", "stderr": "127.0.0.1 - - [19/Oct/2017 16:30:58] \"GET / HTTP/1.1\" 200 9774\n127.0.0.1 - - [19/Oct/2017 16:30:58] \"GET /static/djangoforandroid/mdl/mdl-1.3.0/material.min.css HTTP/1.1\" 200 139816\n127.0.0.1 - - [19/Oct/2017 16:30:58] \"GET /static/djangoforandroid/mdl/mdl-1.3.0/material.min.js HTTP/1.1\" 200 62491\n127.0.0.1 - - [19/Oct/2017 16:30:58] \"GET /static/djangoforandroid/hammer/hammer-2.0.8.min.js HTTP/1.1\" 200 20765\n127.0.0.1 - - [19/Oct/2017 16:30:58] \"GET /static/djangoforandroid/scripts/touchdrawer.js HTTP/1.1\" 200 3611\n127.0.0.1 - - [19/Oct/2017 16:30:58] \"GET /static/djangoforandroid/scripts/sliderh.js HTTP/1.1\" 200 4356\n127.0.0.1 - - [19/Oct/2017 16:30:58] \"GET /static/djangoforandroid/dialog-polyfill/dialog-polyfill-0.4.5/dialog-polyfill.css HTTP/1.1\" 200 827\n127.0.0.1 - - [19/Oct/2017 16:30:58] \"GET /static/djangoforandroid/fonts/material-icons.css HTTP/1.1\" 200 1006\n127.0.0.1 - - [19/Oct/2017 16:30:58] \"GET /static/djangoforandroid/fonts/font-roboto.css HTTP/1.1\" 200 1258\n127.0.0.1 - - [19/Oct/2017 16:30:58] \"GET /static/djangoforandroid/fonts/font-awesome.css HTTP/1.1\" 200 37432\n127.0.0.1 - - [19/Oct/2017 16:30:58] \"GET /static/djangoforandroid/fonts/font-ubuntu.css HTTP/1.1\" 200 1849\n127.0.0.1 - - [19/Oct/2017 16:30:58] \"GET /static/mdl_themes/material.min.css HTTP/1.1\" 200 139816\n127.0.0.1 - - [19/Oct/2017 16:30:58] \"GET /static/css/stylesheet.css HTTP/1.1\" 200 1899\n127.0.0.1 - - [19/Oct/2017 16:30:58] \"GET /static/COMPILED/css/controller.css HTTP/1.1\" 200 7382\n127.0.0.1 - - [19/Oct/2017 16:30:58] \"GET /static/djangoforandroid/dialog-polyfill/dialog-polyfill-0.4.5/dialog-polyfill.js HTTP/1.1\" 200 17777\n127.0.0.1 - - [19/Oct/2017 16:30:58] \"GET /static/d4a/d4a.js HTTP/1.1\" 200 745\n127.0.0.1 - - [19/Oct/2017 16:30:58] \"GET /static/COMPILED/coffeescript/script.js HTTP/1.1\" 200 9084\n127.0.0.1 - - [19/Oct/2017 16:30:58] \"GET /static/javascript/jquery.cookie.js HTTP/1.1\" 200 3139\n127.0.0.1 - - [19/Oct/2017 16:30:58] \"GET /static/djangoforandroid/jquery/jquery-3.1.1.min.js HTTP/1.1\" 200 86709\n127.0.0.1 - - [19/Oct/2017 16:30:59] \"GET /static/djangoforandroid/fonts/roboto/Roboto-Regular.ttf HTTP/1.1\" 200 126072\n127.0.0.1 - - [19/Oct/2017 16:30:59] \"GET /static/djangoforandroid/fonts/iconfont/MaterialIcons-Regular.woff2 HTTP/1.1\" 200 44300\nNot Found: /background-r.svg\n127.0.0.1 - - [19/Oct/2017 16:30:59] \"GET /background-r.svg HTTP/1.1\" 404 4143\n127.0.0.1 - - [19/Oct/2017 16:30:59] \"GET /static/images/background-r.svg HTTP/1.1\" 200 220490\n127.0.0.1 - - [19/Oct/2017 16:30:59] \"GET /static/djangoforandroid/fonts/roboto/Roboto-Medium.ttf HTTP/1.1\" 200 127488\nNot Found: /favicon.ico\n127.0.0.1 - - [19/Oct/2017 16:30:59] \"GET /favicon.ico HTTP/1.1\" 404 4128\n127.0.0.1 - - [19/Oct/2017 16:31:06] \"POST /key/ HTTP/1.1\" 200 14\n127.0.0.1 - - [19/Oct/2017 16:31:06] \"POST /vibrate/ HTTP/1.1\" 200 2\n127.0.0.1 - - [19/Oct/2017 16:31:09] \"POST /key/ HTTP/1.1\" 200 14\n127.0.0.1 - - [19/Oct/2017 16:31:09] \"POST /vibrate/ HTTP/1.1\" 200 2\n127.0.0.1 - - [19/Oct/2017 16:31:26] \"GET / HTTP/1.1\" 200 10120\n127.0.0.1 - - [19/Oct/2017 16:31:27] \"GET /static/djangoforandroid/jquery/jquery-3.1.1.min.js HTTP/1.1\" 200 86709\n127.0.0.1 - - [19/Oct/2017 16:31:27] \"GET /static/djangoforandroid/mdl/mdl-1.3.0/material.min.css HTTP/1.1\" 200 139816\n127.0.0.1 - - [19/Oct/2017 16:31:27] \"GET /static/djangoforandroid/mdl/mdl-1.3.0/material.min.js HTTP/1.1\" 200 62491\n127.0.0.1 - - [19/Oct/2017 16:31:27] \"GET /static/djangoforandroid/hammer/hammer-2.0.8.min.js HTTP/1.1\" 200 20765\n127.0.0.1 - - [19/Oct/2017 16:31:27] \"GET /static/djangoforandroid/scripts/touchdrawer.js HTTP/1.1\" 200 3611\n127.0.0.1 - - [19/Oct/2017 16:31:27] \"GET /static/djangoforandroid/scripts/sliderh.js HTTP/1.1\" 200 4356\n127.0.0.1 - - [19/Oct/2017 16:31:27] \"GET /static/djangoforandroid/dialog-polyfill/dialog-polyfill-0.4.5/dialog-polyfill.css HTTP/1.1\" 200 827\n127.0.0.1 - - [19/Oct/2017 16:31:27] \"GET /static/djangoforandroid/dialog-polyfill/dialog-polyfill-0.4.5/dialog-polyfill.js HTTP/1.1\" 200 17777\n127.0.0.1 - - [19/Oct/2017 16:31:27] \"GET /static/djangoforandroid/fonts/material-icons.css HTTP/1.1\" 200 1006\n127.0.0.1 - - [19/Oct/2017 16:31:27] \"GET /static/djangoforandroid/fonts/font-roboto.css HTTP/1.1\" 200 1258\n127.0.0.1 - - [19/Oct/2017 16:31:27] \"GET /static/djangoforandroid/fonts/font-awesome.css HTTP/1.1\" 200 37432\n127.0.0.1 - - [19/Oct/2017 16:31:27] \"GET /static/djangoforandroid/fonts/font-ubuntu.css HTTP/1.1\" 200 1849\n127.0.0.1 - - [19/Oct/2017 16:31:27] \"GET /static/d4a/d4a.js HTTP/1.1\" 200 745\n127.0.0.1 - - [19/Oct/2017 16:31:27] \"GET /static/mdl_themes/material.min.css HTTP/1.1\" 200 139816\n127.0.0.1 - - [19/Oct/2017 16:31:27] \"GET /static/css/stylesheet.css HTTP/1.1\" 200 1899\n127.0.0.1 - - [19/Oct/2017 16:31:27] \"GET /static/COMPILED/css/controller.css HTTP/1.1\" 200 7382\n127.0.0.1 - - [19/Oct/2017 16:31:27] \"GET /static/COMPILED/coffeescript/script.js HTTP/1.1\" 200 9084\n127.0.0.1 - - [19/Oct/2017 16:31:27] \"GET /static/javascript/jquery.cookie.js HTTP/1.1\" 200 3139\nNot Found: /background-r.svg\n127.0.0.1 - - [19/Oct/2017 16:31:27] \"GET /background-r.svg HTTP/1.1\" 404 4143\n127.0.0.1 - - [19/Oct/2017 16:31:27] \"GET /static/images/background-r.svg HTTP/1.1\" 200 220490\n127.0.0.1 - - [19/Oct/2017 16:31:27] \"GET /static/djangoforandroid/fonts/roboto/Roboto-Regular.ttf HTTP/1.1\" 200 126072\n127.0.0.1 - - [19/Oct/2017 16:31:27] \"GET /static/djangoforandroid/fonts/roboto/Roboto-Medium.ttf HTTP/1.1\" 200 127488\n127.0.0.1 - - [19/Oct/2017 16:31:27] \"GET /static/djangoforandroid/fonts/iconfont/MaterialIcons-Regular.woff2 HTTP/1.1\" 200 44300\nNot Found: /favicon.ico\n127.0.0.1 - - [19/Oct/2017 16:31:30] \"GET /favicon.ico HTTP/1.1\" 404 4128\n127.0.0.1 - - [19/Oct/2017 16:31:31] \"GET / HTTP/1.1\" 200 10120\nNot Found: /background-r.svg\n"}

        return render(request, self.template, locals())
#         return HttpResponse(logs, content_type="application/json")






