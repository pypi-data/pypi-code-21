from django.views.generic import View
from django.http import JsonResponse



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

