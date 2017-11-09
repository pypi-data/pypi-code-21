
import string
import random


def generate_random_string(length=8):
    return ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(length))


def generate_credentials():

    """ Generates a temporary credential pair

    :return: username, password
    """

    return generate_random_string(), generate_random_string()
