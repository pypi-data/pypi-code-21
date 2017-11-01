from django.db.models import Q
from reviewboard.extensions.base import Extension
from reviewboard.extensions.hooks import TemplateHook
from reviewboard.urls import reviewable_url_names, review_request_url_names
from reviewboard.webapi.resources.review_group import ReviewGroupResource

apply_to_url_names = set(reviewable_url_names + review_request_url_names)


class AutocompleteContainsReviewGroupResource(ReviewGroupResource):
    def get_queryset(self, request, *args, **kwargs):
        # Create mutable QueryDict and pop the 'q' parameter
        request.GET = request.GET.copy()
        try:
            search_q = request.GET.pop('q')[0]
        except:
            search_q = None

        query = ReviewGroupResource.get_queryset(
            self, request=request, *args, **kwargs)

        if search_q:
            q = Q(name__icontains=search_q)

            if request.GET.get('displayname', None):
                q = q | Q(display_name__icontains=search_q)

            query = query.filter(q)

        return query


review_group_resource = AutocompleteContainsReviewGroupResource()


class AutocompleteContains(Extension):
    metadata = {
        'Name': 'Autocomplete Contains',
        'Summary': 'Enhance review groups autocomplete',
        'Author': 'Erik Johansson',
        'Author-email': 'erik@ejohansson.se',
        'License': 'MIT',
        'Home-page': 'https://github.com/erijo/rb-autocomplete-contains'
    }

    resources = [review_group_resource]

    def initialize(self):
        TemplateHook(self, 'base-scripts-post',
                     'autocomplete_contains/modify_field.html',
                     apply_to=apply_to_url_names)
