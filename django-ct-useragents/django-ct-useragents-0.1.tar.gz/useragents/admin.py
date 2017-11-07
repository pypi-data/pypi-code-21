from django.contrib import admin

from .models import Ip, Visit, UserAgent, Path

@admin.register(Ip)
class IpAdmin(admin.ModelAdmin):
    list_display = ['address','visits','created','modified',]
    search_fields = ['address',]
    
@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = ['useragent','ip','path','method','content_type','encoding','created',]
    search_fields = ['useragent__string','ip__address','path__path','method','content_type','encoding']
    
@admin.register(Path)
class PathAdmin(admin.ModelAdmin):
    list_display = ['path','visits','created','modified',]
    search_fields = ['path',]
    
@admin.register(UserAgent)
class UserAgentAdmin(admin.ModelAdmin):
    list_display = ['string','visits','created','modified',]
    search_fields = ['string',]
