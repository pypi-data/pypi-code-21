from django.contrib import admin
from .models import UserProfile


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'uf')
    list_filter = ['uf', 'gender', 'birthdate', 'birthyear']
    search_fields = (
        'user__first_name', 'user__email', 'user__username',
        'country', 'birthyear')


admin.site.register(UserProfile, UserProfileAdmin)
