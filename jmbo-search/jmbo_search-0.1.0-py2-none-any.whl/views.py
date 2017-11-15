from haystack.views import search_view_factory
from haystack.generic_views import SearchView as GenericSearchView

from haystack.query import SearchQuerySet
from haystack.inputs import AltParser


class DisMaxSearchView(GenericSearchView):
    parser_name = "dismax"
    query_fields = ["title", "description", "text"]

    def get_queryset(self):
        if self.request.POST:
            parser = AltParser(
                parser_name=self.parser_name,
                query_string=self.request.POST["q"],
                qf=" ".join(self.query_fields),
                q_alt="*:*",
                mm=1
            )
            sqs = SearchQuerySet().filter(content=parser)
            return sqs
        return []

    def get_form_kwargs(self):
        kwargs = super(DisMaxSearchView, self).get_form_kwargs()
        if self.request.method == 'POST' and self.request.POST:
            kwargs.update({
                'data': self.request.POST,
            })
        return kwargs
