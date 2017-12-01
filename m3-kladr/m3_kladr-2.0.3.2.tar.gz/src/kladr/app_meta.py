#coding:utf-8

# совместимость с django 1.6
try:
    from django.conf.urls.defaults import patterns
except ImportError:
    from django.conf.urls import patterns

from actions import kladr_controller, KLADRPack, Kladr_DictPack
from m3 import authenticated_user_required


def register_actions():
    kladr_controller.packs.extend(
        (
            KLADRPack(),
            Kladr_DictPack()
        )
    )
    #kladr_controller.rebuild_patterns()


def register_urlpatterns():
    u"""
    Регистрация конфигурации урлов для приложения kladr
    """
    return patterns(
        '', (r'^m3-kladr', 'kladr.app_meta.kladr_view'),
    )


#===============================================================================
# Представления
#===============================================================================
@authenticated_user_required
def kladr_view(request):
    return kladr_controller.process_request(request)
