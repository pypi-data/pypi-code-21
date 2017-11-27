from jcms.models import Article
from django.conf import settings
from django.conf.urls import url, include
import importlib


'''
Gets the shortcode for a article
'''
def shortcode(shortcode):
    article = Article.objects.get(shortcode=shortcode)
    return article


'''
Adds the crud urls to the jcms urls
'''
def add_crud(cruds):
    crud_urls = []

    for crud_model in cruds:
        crud_urls += crud_model.get_crud_urls(crud_model)
    return crud_urls


'''
Adds the menu items to jcms urls
'''
def add_menu_urls():
    jcms_urls = []

    for jcms_app in settings.JCMS_APPS:
        slug = importlib.import_module(jcms_app + '.jcms.menu_item').MenuItem.slug
        jcms_urls.append(url(r'^' + slug + '/', include(jcms_app + '.jcms.urls')))
    return jcms_urls
