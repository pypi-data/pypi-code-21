from django.contrib import admin
from .models import UserProfile


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'uf')
    list_filter = ['uf', 'gender', 'birthdate']
    search_fields = (
        'user__first_name', 'user__email', 'user__username',
        'country')


admin.site.register(UserProfile, UserProfileAdmin)
