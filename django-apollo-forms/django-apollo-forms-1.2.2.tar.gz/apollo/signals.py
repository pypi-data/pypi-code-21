import django.dispatch

# fired when a form is submitted to the backend, but before the submission is cleaned / validated
form_submitted = django.dispatch.Signal(providing_args=["raw_data", "form_id"])

# fired after a form submission is cleaned / validated
form_submission_cleaned = django.dispatch.Signal(providing_args=["cleaned_data", "form_id", "submission_id"])

# fired on a form submission error
form_submission_error = django.dispatch.Signal(providing_args=["error", "raw_data", "form_id"])