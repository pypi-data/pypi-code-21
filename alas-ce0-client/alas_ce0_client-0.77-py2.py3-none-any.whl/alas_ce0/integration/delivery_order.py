import base64

from alas_ce0.common.client_base import ApiClientBase


class DeliveryOrderIntegrationClient(ApiClientBase):
    def upload_file(self, sender_code, file_content, file_format="txt"):
        params = {
            'sender_code': sender_code,
            'base64_content': base64.encodestring(file_content),
            'format': file_format
        }
        return self.http_post_json("/integration/delivery-orders/_upload-file", params)