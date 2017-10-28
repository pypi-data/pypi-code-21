from django.dispatch import Signal

order_succeeded = Signal(providing_args=['order'])
