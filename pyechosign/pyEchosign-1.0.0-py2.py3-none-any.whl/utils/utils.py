def find_user_in_list(lst, key, value):
    """ Loops through a list of Users, and checks to see if the attribute "key" matches "value". If so, it returns that
    user.

    Args:
        lst: The list of users
        key: The attribute to check against
        value: What the matching value should be

    """
    for user in lst:
        if getattr(user, key) == value:
            return user
    return None
