def get_headers(access_token, api_user_email=None, content_type='application/json'):
    """
    Generates the headers for a request to the API - can specify which user the API call should be made under.
    Args:
        content_type: What content type should be specified in the request headers. Defaults to application/json.
        access_token: The access token of the account making the request
        api_user_email: If the access token covers more than one user, enter the email of the user the call should be made under

    Returns: A dictionary to be used as the headers argument in requests

    """
    headers = {'Access-Token': access_token}

    if content_type is not None:
        headers.update({'Content-Type': content_type})
    if api_user_email is not None:
        headers.update({'x-api-user': 'email:{}'.format(api_user_email)})

    return headers
