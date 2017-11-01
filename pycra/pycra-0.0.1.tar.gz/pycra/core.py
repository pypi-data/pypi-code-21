import hashlib
import hmac
import datetime
import random
import pbkdf2helper


def create_challenge(user):
    """
    Create a new Nonce for (This challenge) based on username and some random data
    :param user: A example User Object
    :return: nonce as HMAC
    """

    print("______Create new Challenge________")
    key = str(datetime.datetime.utcnow()) + user.username
    msg = str(random.randint(0, 999999))
    nonce = hmac.new(key.encode(), msg.encode(), hashlib.sha256).hexdigest()

    print("Challenge nonce: " + str(nonce))

    return nonce


def auth_check(user, response):
    """
    Compare Answer for the least given challenge to this User
    :param user: A example User Object
    :param response: Answer from Client
    :return: True or False
    """
    print("______Auth Check________")
    answer = calculate_answer(user.nonce, user.password)
    check = hmac.compare_digest(answer, response)
    print("Is Auth: " + str(check))

    return check


def calculate_answer(challenge, password):
    """
    Calculate Answer on Server and for Client without hashed Passwords
    Needs to save Passwords on Server in Plaintext!
    -> Answer = HMAC(challenge, Plaintext Password, sha256)

    :param challenge:
    :param password:
    :return: answer
    """
    print("______Calculate Answer________")
    answer = hmac.new(challenge.encode(), password.encode(), hashlib.sha256).hexdigest()
    print("Servers answer: " + str(answer))

    return answer


def calculate_answer_for_pbkdf2(challenge, password, algorithm, salt, iterations):
    """
    Calculate Answer on Client for PBKDF2 hashed Passwords.
    -> Answer = HMAC(challenge, PBKDF2 hashed Password, sha256)

    :param challenge:
    :param password:
    :param algorithm:
    :param salt:
    :param iterations:
    :return: answer
    """
    assert algorithm == pbkdf2helper.algorithm

    print("______Calculate Answer________")
    password_hash=pbkdf2helper.encode(password, salt, int(iterations))
    print("Password Hash: "+str(password_hash))
    answer = hmac.new(challenge.encode(), password_hash.encode(), hashlib.sha256).hexdigest()
    print("Client answer: " + str(answer))

    return answer






