
from django.http.response import HttpResponse, HttpResponseBadRequest

from googletrans import Translator

from trans.forms import TranslateForm


def translate(request):

    translator = Translator()

    form = TranslateForm(request.GET)

    if form.is_valid():

        data = form.cleaned_data

        result = translator.translate(data['text'], data['dst'], data['src'])

        return HttpResponse(result.text)

    return HttpResponseBadRequest('Invalid request')
