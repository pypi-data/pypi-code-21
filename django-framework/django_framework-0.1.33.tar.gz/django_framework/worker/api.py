# this is where we hold basic things
from django_framework.django_helpers.api_helpers import BaseAPI


class JobAPI(BaseAPI):

    def __init__(self, **kwargs):
        kwargs['run'] = False
        super(JobAPI, self).__init__(**kwargs)

    def special_api(self):
        self.response = {'must be a dict! how i am now a Result!'}

    def get_response(self):
        return self.response
