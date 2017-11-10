#!/usr/bin/env python

from hca import upload

# URN you got from creating a new Submision Envelope
urn = "dcp:upl:aws:dev:deadbeef-dead-dead-dead-beeeeeeeeeef:eyJBV1NfQUNDRVNTX0tFWV9JRCI6ICJBS0lBSjJCRjNYN0NQRlhVQ1ZDUSIsICJBV1NfU0VDUkVUX0FDQ0VTU19LRVkiOiAiOFovRU1PWGpqTTZRd09CZ0ZzUGtvQmlDRzFqTG5VV2l2LzdYb0pPVCJ9"

upload.select_area(urn=urn)
upload.upload_file('LICENSE', quiet=True)
print("")  # report_progress doesn't print a newline
