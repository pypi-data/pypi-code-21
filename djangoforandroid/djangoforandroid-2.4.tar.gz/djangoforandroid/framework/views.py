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

        return render(request, self.template, locals())



########################################################################
class BrythonView(View):
    """"""

    #----------------------------------------------------------------------
    def post(self, request):
        """"""
        name = request.POST.get('name', None)
        args = eval(request.POST.get('args', '[]'))
        kwargs = eval(request.POST.get('kwargs', '{}'))

        if name:
            v = getattr(self, name)(*args, **kwargs)

            if isinstance(v, dict):
                return JsonResponse(v)
            else:
                return JsonResponse({'__D4A__': v,})

