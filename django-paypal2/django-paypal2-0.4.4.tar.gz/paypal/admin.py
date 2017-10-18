from django.contrib import admin


class PaypalTransactionAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'payment_id', 'reference_id', 'description',
                    'currency', 'amount_total', 'payer_email', 'state', 'is_succeed')
    search_fields = ('payment_id', 'invoice_number', 'payer_email', 'reference_id')
    list_filter = ('state',)
    raw_id_fields = ('user',)
