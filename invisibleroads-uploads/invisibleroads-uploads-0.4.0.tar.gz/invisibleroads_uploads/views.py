from pyramid.csrf import check_csrf_origin, check_csrf_token

from .models import Upload


def add_routes(config):
    config.add_route('files.json', '/files.json')

    config.add_view(
        receive_file,
        permission='file-upload',
        renderer='json',
        request_method='POST',
        require_csrf=False,
        route_name='files.json')


def receive_file(request):
    if request.authenticated_userid:
        check_csrf_origin(request) and check_csrf_token(request)
    upload = Upload.save_from(request, 'files[]')
    return {'upload_id': upload.id}
