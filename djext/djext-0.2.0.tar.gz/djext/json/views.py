class JsonFormMixin(object):
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.method in ('POST', 'PUT') and not self.request.POST \
                and hasattr(self.request, 'json') and self.request.json:
            kwargs['data'] = self.request.json
        return kwargs
