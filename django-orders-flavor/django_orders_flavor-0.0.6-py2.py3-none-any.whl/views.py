from django.views.generic import DetailView, FormView
from paypal.standard.forms import PayPalPaymentsForm

from . import models
from .shortcuts import paypal_context


class PaypalOrderFormView(DetailView, FormView):
    template_name = 'orders/paypal_form.html'
    queryset = models.Order.objects.pending()
    form_class = PayPalPaymentsForm

    def get_initial(self):
        return paypal_context(
            order=self.object,
            request=self.request
        )
