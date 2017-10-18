"""hudai.helpers.http_errors

Mock HTTP responses used when the wrapper does magic on behalf of the API for
convenience
"""

def api_404():
    """
    Returns standard 404 object
    """
    return {
        'message': 'Not Found',
        'status': 404,
        'type': 'not_found_error'
    }
