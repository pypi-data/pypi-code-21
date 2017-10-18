from django.contrib import admin

from paypal.admin import PaypalTransactionAdmin
from paypal.models import PaypalTransaction

admin.site.register(PaypalTransaction, PaypalTransactionAdmin)
