from django.contrib import admin
from .models import NotificationReceipt


class NotificationReceiptAdmin(admin.ModelAdmin):
    list_display = ('user', 'payload', 'timestamp')
admin.site.register(NotificationReceipt, NotificationReceiptAdmin)
