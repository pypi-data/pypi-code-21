

# this should be imported directly into the URLs
"""chai_django URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin

from django.conf import settings
import importlib


def load_urlpatterns(exclude = None, include = None, fail_silently = False, **kwargs):
    '''Load url patterns from the various registered Applications.  Will automatically check all of them.'''
    urlpatterns = []
    
    # variable checking.  Make sure things are either None or a List
    if exclude != None and include != None:
        raise ValueError('Conflicting commands on loading urlpatterns from applications.  Only exclude OR include can be set')
    
    if exclude != None and type(exclude) is not list:
        raise ValueError('The input variable exclude must be of type list')
    
    if include != None and type(include) is not list:
        raise ValueError('The input variable include must be of type list')


    # dynamically get the urls! we will enforce that the urlpatterns must exist for ALL apps
    for app_name in settings.SERVER_APPS: 
        # skip over everyone explicitly told to skip over
        if exclude is not None and app_name in exclude:
            continue
        
        # only include the things explicitly set to include
        if include is not None and app_name in include:
            pass
        
        # loading urlpatterns from individual files.
        try:
            module = importlib.import_module(app_name + '.urls', package=None)
            urlpatterns += module.urlpatterns
        except Exception as e:
            if fail_silently == False:
                raise

            print('Problem loading {app_name} urlpatterns.'.format(app_name = app_name))
            print('Check to make sure the App has a urls.py file.')
            print('Check to make sure urls.py has list variable urlpatterns')
            print('Error:', e)
    
    return urlpatterns