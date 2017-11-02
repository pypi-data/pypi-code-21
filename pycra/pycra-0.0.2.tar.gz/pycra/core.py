import hashlib
import hmac
import datetime
import pbkdf2helper


def sign_message(msg, psk, cnonce):
    """
    Sign Server Message with psk

    :param msg:
    :param psk:
    :param cnonce:
    :return:
    """

    key = cnonce+psk
    return hmac.new(key.encode(), msg.encode(), hashlib.sha256).hexdigest()


def verify_message(msg, psk, cnonce, response):
    """
    Helper function to verfiy message with psk

    :param msg:
    :param psk:
    :param cnonce:
    :param response:
    :return: True or False
    """

    key = cnonce + psk
    encoded=hmac.new(key.encode(), msg.encode(), hashlib.sha256).hexdigest()
    check = hmac.compare_digest(encoded, response)
    return check


def create_challenge(user):
    """
    Create a new Nonce for (This challenge) based on username and some random data

    :param user: A example User Object
    :return: nonce/cnonce  as HMAC
    """

    key = str(datetime.datetime.utcnow()) + user.username
    msg = pbkdf2helper.generate_salt(12)
    nonce = hmac.new(key.encode(), msg.encode(), hashlib.sha256).hexdigest()

    return nonce


def auth_check(user, response):
    """
    Compare Answer for the least given challenge to this User
    :param user: A example User Object
    :param response: Answer from Client
    :return: True or False, nextnonce
    """
    print("______Auth Check________")
    print("Response from client: " + str(response))

    answer = calculate_answer(user.nonce, user.cnonce, user.password).hexdigest()

    print("Answer on server: " + str(answer))

    check = hmac.compare_digest(answer, response)
    print("Is Auth: " + str(check))
    if check:
        nextnonce = answer
    else:
        nextnonce = None

    return check, nextnonce


def calculate_answer(challenge, cnonce, password):
    """
    Calculate Answer on Server and for Client without hashed Passwords
    Needs to save Passwords on Server in Plaintext!
    -> Answer = HMAC(challenge, Plaintext Password, sha256)

    :param challenge:
    :param cnonce:
    :param password:

    :return: answer, verify_hash
    """

    answer = hmac.new(challenge.encode(), password.encode(), hashlib.sha256)
    #answer = hmac.new(password.encode(),challenge.encode(), hashlib.sha256)

    answer.update(cnonce.encode())

    return answer


def calculate_answer_for_pbkdf2(challenge, cnonce, password, algorithm, salt, iterations):
    """
    Calculate Answer on Client for PBKDF2 hashed Passwords.
    -> Answer = HMAC(challenge, PBKDF2 hashed Password, sha256)

    :param challenge:
    :param cnonce
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
    #answer = hmac.new(password_hash.encode(), challenge.encode(), hashlib.sha256)
    answer = hmac.new(challenge.encode(), password_hash.encode(), hashlib.sha256)

    print("Client answer: " + str(answer))

    answer.update(cnonce.encode())

    return answer






