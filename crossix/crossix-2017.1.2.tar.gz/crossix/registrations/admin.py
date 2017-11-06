from . import models
from django.contrib import admin

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'gender', 'min_age']
    list_filter = ['gender']


admin.site.register(models.Category, CategoryAdmin)


class ParticipantAdmin(admin.ModelAdmin):
    list_display = ['firstname', 'lastname', 'birthyear', 'gender', 'email', 'category', 'school', 'promo', 'last_edition']
    list_filter = ['gender', 'category', 'school', 'last_edition']

admin.site.register(models.Participant, ParticipantAdmin)


class EditionAdmin(admin.ModelAdmin):
    list_display = ['date', 'location', 'close_registrations']
    list_filter = ['location']

admin.site.register(models.Edition)
