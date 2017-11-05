from django.dispatch import Signal

added_product_to_cart = Signal(providing_args=['request', 'product', 'amount'])
removed_product_from_cart = Signal(providing_args=['request', 'product'])
set_product_amount_in_cart = Signal(providing_args=['request', 'product', 'amount'])

order_created = Signal(providing_args=['request', 'order'])
