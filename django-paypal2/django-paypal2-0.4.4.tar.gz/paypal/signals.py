import django.dispatch

payment_succeed = django.dispatch.Signal(providing_args=['instance'])
