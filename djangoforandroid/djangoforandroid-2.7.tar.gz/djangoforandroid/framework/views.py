from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse, HttpResponse
from django.conf import settings
import xml.etree.ElementTree as ET
from .theme import THEME, CSS

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
                if v is None:
                    return JsonResponse({'__D4A__': 0,})
                #if v in [False, True]:
                    #return JsonResponse({'__D4A__': int(v),})
                else:
                    return JsonResponse({'__D4A__': v,})




########################################################################
class theme(View):
    """"""

    #----------------------------------------------------------------------
    def get(self, request):
        """"""
        theme_settings = settings.ANDROID.get('THEME', None)

        if theme_settings:

            if 'colors' in theme_settings:
                tree = ET.parse(theme_settings['colors'])
                theme = {child.attrib['name']:child.text for child in tree.getroot()}

                equivalents = {
                    'primaryColor': '--mdc-theme-primary',
                    'primaryLightColor': '--mdc-theme-primary-light',
                    'primaryDarkColor': '--mdc-theme-primary-dark',

                    'secondaryColor': '--mdc-theme-secondary',
                    'secondaryLightColor': '--mdc-theme-secondary-light',
                    'secondaryDarkColor': '--mdc-theme-secondary-dark',

                    'primaryTextColor': '--mdc-theme-text-primary-on-primary',
                    'secondaryTextColor': '--mdc-theme-text-primary-on-secondary',
                }


                if 'primaryColor' in theme:
                    THEME[equivalents['primaryColor']] = theme['primaryColor']
                    THEME[equivalents['primaryLightColor']] = theme['primaryLightColor']
                    THEME[equivalents['primaryDarkColor']] = theme['primaryDarkColor']

                    THEME[equivalents['secondaryColor']] = theme.get('secondaryColor', theme['primaryColor'])
                    THEME[equivalents['secondaryLightColor']] = theme.get('secondaryLightColor', theme['primaryLightColor'])
                    THEME[equivalents['secondaryDarkColor']] = theme.get('secondaryDarkColor', theme['primaryDarkColor'])

                if 'primaryTextColor' in theme:
                    THEME['--mdc-theme-text-primary-on-primary'] = theme['primaryTextColor']
                    THEME['--mdc-theme-text-primary-on-primary-dark'] = theme['primaryTextColor']

                if 'secondaryTextColor' in theme:
                    THEME['--mdc-theme-text-primary-on-secondary'] = theme['secondaryTextColor']
                    THEME['--mdc-theme-text-primary-on-secondary-dark'] = theme['secondaryTextColor']


            else:
                THEME.update(theme_settings)



        content = ":root{\n"
        for key in THEME:
            color = THEME[key]
            content += "{}: {};\n".format(key, color)

        content += "\n"

        save_for_var = ["--mdc-theme-primary", "--mdc-theme-secondary"]
        for c in save_for_var:
            color = THEME[c]
            name = c.replace('--mdc', '--var')
            color = color.lstrip('#')
            color = [int(color[i:i+2], 16) for i in range(0, len(color), 2)]
            content += '{}: {}, {}, {};'.format(name, *color)


        content += "\n}"
        content += CSS


        response = HttpResponse(content=content)
        response['Content-Type'] = 'text/css'
        response['Content-Disposition'] = 'attachment; filename="mdc-theme.css"'

        return response




