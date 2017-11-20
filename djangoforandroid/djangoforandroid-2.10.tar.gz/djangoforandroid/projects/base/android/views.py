from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse


########################################################################
class Home(View):
    """"""
    template = 'home.html'

    #----------------------------------------------------------------------
    def get(self, request):
        """"""

        return render(request, self.template, locals())
