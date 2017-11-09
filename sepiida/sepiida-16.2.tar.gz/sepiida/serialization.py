import csv
import io
import json
import urllib.parse

import accept_types

import sepiida.errors


def loads(request):
    content_type = request.headers.get('Content-Type', '')
    if not content_type:
        raise sepiida.errors.InvalidPayload(
            "Your request did not include the 'Content-Type' header and RFC2616 does not specify a default encoding. Since "
            "we cannot know how your request is encoded we do not know how to decode it. Please include an appropriate "
            "Content-Type header"
        )

    try:
        return REQUEST_CONTENT_TYPES[content_type](request)
    except KeyError:
        error = "The content-type header you specified, {}, is not one that we support. Please try one of {}".format(
            content_type,
            ', '.join(REQUEST_CONTENT_TYPES.keys())
        )
        raise sepiida.errors.InvalidPayload(error)
    except ValueError as e:
        raise sepiida.errors.InvalidPayload(
            "Your payload specified a Content-Type of {} but we were unable to decode it as such: {}".format(content_type, e)
        )

def loads_form(request):
    return request.values.to_dict()

def loads_json(request):
    try:
        decoded = request.data.decode('utf-8')
    except ValueError as e:
        raise ValueError("Your request was not UTF-8 encoded: {}".format(e))

    return json.loads(decoded)

def dumps_csv(response, signature):
    signature = signature.signature if signature else None

    buff = io.StringIO()
    writer = csv.writer(buff, dialect='excel')
    if isinstance(response, dict):
        try:
            resources = response['resources']
        except KeyError:
            resources = [response]
    elif isinstance(response, (list, tuple, set)):
        resources = response
    else:
        resources = [response]
    if not resources:
        return ''
    signature = signature or resources[0]
    if signature:
        keys = sorted(signature.keys())
        writer.writerow(keys)
    for row in resources:
        writer.writerow([row[key] for key in keys])
    buff.seek(0)
    return buff.read()

def dumps_form(response, signature): # pylint: disable=unused-argument
    preprocessed = preprocess_form(response)
    return urllib.parse.urlencode(preprocessed)

def dumps_json(response, signature): # pylint: disable=unused-argument
    return json.dumps(response)



REQUEST_CONTENT_TYPES = {
    'application/json'                  : loads_json,
    'application/x-www-form-urlencoded' : loads_form,
}
RESPONSE_CONTENT_TYPES = {
    'application/json'                  : dumps_json,
    'application/x-www-form-urlencoded' : dumps_form,
    'text/csv'                          : dumps_csv,
}
CONTENT_TYPE_PREFERENCE_ORDER = [
    'application/json',
    'application/x-www-form-urlencoded',
    'text/csv',
]
assert set(RESPONSE_CONTENT_TYPES.keys()) == set(CONTENT_TYPE_PREFERENCE_ORDER), (
    "Please ensure that every key in REQUEST_CONTENT_TYPES is also in CONTENT_TYPE_PREFERENCE_ORDER"
)

def prepare_response(request, response, headers, signature):
    content_type = request.headers.get('Content-Type') or 'application/json' # Sometimes we get empty strings for Content-Type
    match = accept_types.get_best_match(request.headers.get('Accept', content_type), CONTENT_TYPE_PREFERENCE_ORDER)
    if not match:
        raise sepiida.errors.UnableToSerialize(title=(
            "No serializers are able to respond in a format you would accept. "
            "Check your Accept header and alter it to accept more types for this request. "
            "Possible MIME types include: {}".format(", ".join(RESPONSE_CONTENT_TYPES.keys()))
        ))
    new_headers = headers.copy()
    new_headers['Content-Type'] = match
    return RESPONSE_CONTENT_TYPES[match](response, signature), new_headers

def preprocess_form(data):
    "This should covert a nested dictionary with lists into a flat dictionary in preparation for urlencoding, recursively"
    results = {}
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, (int, float, str, type(None))):
                results[k] = v
            else:
                preprocessed = preprocess_form(v)
                for subk, subv in preprocessed.items():
                    results["{}{}".format(k, subk if subk.startswith('[') else "." + subk)] = subv
    else:
        for i, d in enumerate(data):
            if isinstance(d, (int, float, str, type(None))):
                results["[{}]".format(i)] = d
            else:
                for subk, subv in preprocess_form(d).items():
                    results["[{}].{}".format(str(i), subk)] = subv
    return results
