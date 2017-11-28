
from django_framework.django_helpers.worker_helpers.job_widgets import BaseGenerateResponse

class GenerateResponse(BaseGenerateResponse):

    def run(self):
        
        message = self.initial_payload['message']

        self.response  = {}
        self.response['status'] = 0
        self.response['random_message'] = 1
        self.response['passthrough']    = message

    def get_response(self):
        return self.response