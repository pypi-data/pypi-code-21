import falcon
import ujson
from marshmallow.schema import MarshalResult


class MarshmallowMiddleware:

    def process_resource(self, req, resp, resource, params):

        should_parse =  (
            # Veriy that it is safe to parse this resource
            req.method in ('POST', 'PUT'),
            # If there is no data in the body, there is nothing to look at
            bool(req.content_length),
            # If the resource doesn't have a schema the loading would be impossible
            hasattr(resource, 'schema'),
            # Only consider JSON requests for auto-parsing
            req.content_type == 'application/json',
        )

        # Check that all the conditions for parsing are met
        if not all(should_parse):
            req.context['_marshalled'] = False
            return

        stream = req.context['marshalled_stream'] = req.bounded_stream.read()
        data = ujson.loads(stream)

        if req.method == 'PUT':
            data['id'] = params['obj_id']

        schema = resource.schema()
        data = schema.load(data, session=resource.session)

        if data.errors:
            #  This should probably return whatever the accept header indicates
            raise falcon.HTTPStatus(
                falcon.HTTP_400,
                headers={'Content-Type': 'application/json'},
                body=ujson.dumps({'errors': data.errors}),
            )

        req.context['dto'] = data
        req.context['_marshalled'] = True

    def process_response(self, req, resp, resource, req_succeeded):
        if isinstance(resp.body, MarshalResult):
            resp.content_type = 'application/json'
            resp.body = ujson.dumps(resp.body.data)
