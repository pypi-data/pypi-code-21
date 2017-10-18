import random

from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt

from paypal.models import PaypalTransaction


@csrf_exempt
def sample_pay_view(request):
    if request.method == 'GET':
        return render(request, 'sample_pay.html')
    elif request.method == 'POST':
        tx = PaypalTransaction(
            description="sample pay",
        )
        tx.add_item("sample", 'USD', float(request.POST['amount']))
        tx.reference_id = str(random.randint(10000, 99999))
        tx.save()
        return redirect('paypal_redirect', uid=tx.uid)
