from widget import ModelJobAPI

# we don't create a cached version of this because we really don't want to!
# jobs can be updated pretty low level....

def api_model_jobs(request, model_name_slug, model_pk = None, model_uuid = None):
    api = ModelJobAPI(model_name = model_name_slug, model_pk = model_pk, model_uuid = model_uuid,  request = request, job_pk = None)
    api.run()
    response = api.format_data(api.data)
    return response


def api_model_job(request, model_name_slug, model_pk = None, model_uuid = None, job_uuid = None):

    api = ModelJobAPI(model_name = model_name_slug, request = request, model_pk = model_pk, model_uuid=model_uuid, job_pk= job_uuid)
    api.run()
    response = api.format_data(api.data)
    return response


def api_admin_model_jobs(request, model_name_slug, model_pk = None, model_uuid = None, job_uuid = None):
    api = ModelJobAPI(admin=True, model_name = model_name_slug, model_pk = model_pk, model_uuid=model_uuid, request = request)
    api.run()
    response = api.format_data(api.data)
    return response


def api_admin_model_job(request, model_name_slug, model_pk = None, model_uuid = None, job_uuid = None):
    api = ModelJobAPI(admin = True, model_name = model_name_slug, request = request, model_pk = model_pk,model_uuid=model_uuid, job_pk= job_uuid)
    api.run()
    response = api.format_data(api.data)
    return response