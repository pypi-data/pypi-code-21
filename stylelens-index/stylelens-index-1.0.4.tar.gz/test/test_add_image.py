from __future__ import print_function
import time
import stylelens_index
from stylelens_index.rest import ApiException
from pprint import pprint
# create an instance of the API class
api_instance = stylelens_index.ImageApi()
body = stylelens_index.Image() # Image | Image object that needs to be added to the db.

try:
    # Add a new image
    api_response = api_instance.add_image(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ImageApi->add_image: %s\n" % e)
