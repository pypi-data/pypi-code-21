from celery import task


@task
def import_xls_price_list(price_list_id):
    from .models import XLSPriceList
    price_list = XLSPriceList.objects.get(pk=price_list_id)
    price_list.process()
