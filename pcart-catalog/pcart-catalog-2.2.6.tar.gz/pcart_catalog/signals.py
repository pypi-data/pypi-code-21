import django.dispatch

product_page_visit = django.dispatch.Signal(
    providing_args=["customer_id", "product_id", "variant_id"])
