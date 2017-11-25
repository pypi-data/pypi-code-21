from .http.response import JsonResponseBadRequest


class JsonFormMixin(object):
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.method in ('POST', 'PUT') and not self.request.POST \
                and hasattr(self.request, 'json') and self.request.json:
            kwargs['data'] = self.request.json
        return kwargs

    def form_invalid(self, form):
        errors = {
            field: [error for data in error_list.data for error in data]
            for field, error_list in form.errors.items()
        }
        return JsonResponseBadRequest({'errors': errors})
