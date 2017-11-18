"""Views module"""
import string

import random
from abc import ABC, abstractmethod
import redis

from django.contrib.auth import get_user_model, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.response import HttpResponseBadRequest, HttpResponseRedirect, HttpResponse
from django.views.generic.base import View

from discourse_django_sso import utils
from discourse_django_sso.utils import ConsumerType


class SSOProviderView(LoginRequiredMixin, View):
    """
    View that implements sso.
    """

    sso_secret = None
    sso_redirect = None
    consumer_type = ConsumerType.DISCOURSE

    def get(self, request, **kwargs):  # pylint: disable=unused-argument
        """Performs the SSO"""
        try:
            sso = request.GET['sso']
            sig = request.GET['sig']
        except KeyError:
            return HttpResponseBadRequest()
        redirect = utils.SSOProviderService(
            sso_key=self.sso_secret
        ).get_signed_url(
            user=request.user,
            redirect_to=self.sso_redirect,
            sso=sso,
            signature=sig,
            consumer_type=self.consumer_type
        )
        if redirect is None:
            return HttpResponseBadRequest()
        return HttpResponseRedirect(
            redirect_to=redirect
        )


class NonceService(ABC):
    """
    Service for managing nonce.
    """

    def __init__(self):
        self.rand = random.SystemRandom()

    @abstractmethod
    def generate_nonce(self):
        """
        Generate nonce.
        """
        val = ''.join(self.rand.choice(string.hexdigits) for _ in range(32))
        while self.is_nonce_already_generated(val):
            val = ''.join(self.rand.choice(string.hexdigits) for _ in range(32))  # pragma: no cover
        return val

    @abstractmethod
    def is_nonce_already_generated(self, nonce) -> bool:
        """
        Return true if nonce was already generated in the past
        :param nonce: Nonce to be checked
        """
        pass

    @abstractmethod
    def is_nonce_valid(self, nonce: str):
        """
        Returns true if nonce is valid
        :param nonce: Nonce to be checked
        """
        pass

    @abstractmethod
    def invalidate_nonce(self, nonce: str):
        """
        Invalidate nonce
        :param nonce: Nonce to be invalidated
        """
        pass


class InMemoryNonceService(NonceService):
    """
    In memory implementation of nonce service
    """

    def __init__(self):
        super().__init__()
        self.generated_nonces = set()
        self.invalid_nonces = set()

    def generate_nonce(self) -> str:
        val = super().generate_nonce()
        self.generated_nonces.add(val)
        return val

    def is_nonce_already_generated(self, nonce) -> bool:
        return nonce in self.generated_nonces or nonce in self.invalid_nonces

    def is_nonce_valid(self, nonce: str) -> bool:
        return nonce in self.generated_nonces and nonce not in self.invalid_nonces

    def invalidate_nonce(self, nonce: str):
        self.invalid_nonces.add(nonce)


class RedisNonceService(NonceService):  # pragma: no cover
    """
    Implementation of NonceService based on Redis
    """

    def __init__(self, host, port, password):
        super().__init__()
        self.host = host
        self.port = port
        self.password = password
        self.redis = None

    def connect(self):
        """
        Connect to Redis server
        """
        self.redis = redis.Redis(self.host, self.port, self.password)

    def is_nonce_already_generated(self, nonce) -> bool:
        return self.redis.get(nonce) is not None

    def invalidate_nonce(self, nonce: str):
        self.redis.set(nonce, 'INVALID')

    def generate_nonce(self):
        val = super().generate_nonce()
        # TODO or maybe use timeout when setting value, so that it expires after some time:
        # setex(name, time, value)  # pylint: disable=wrong-spelling-in-comment
        # Set the value of key name to value that expires in time seconds. time can be represented
        # by an integer or a Python timedelta object.   # pylint: disable=wrong-spelling-in-comment
        self.redis.set(val, 'VALID')

    def is_nonce_valid(self, nonce: str):
        val = self.redis.get(nonce)
        return val is not None and val == 'VALID'


class SSOClientView(LoginRequiredMixin, View):
    """
    View for the client of the sso
    """
    sso_secret = None
    sso_url = None
    nonce_service = None

    def get(self, request, **kwargs):  # pylint: disable=unused-argument
        """
        View which generates redirect to sso provider.
        """
        client_util = utils.SSOClientUtils(self.sso_secret, self.sso_url)
        # TODO how do we know about email value - true/false
        sso_url = client_util.generate_sso_url(self.nonce_service.generate_nonce(), False)

        return HttpResponseRedirect(
            redirect_to=sso_url
        )


class SSOCreateSessionView(LoginRequiredMixin, View):
    """
    View for processing of response from sso provider
    """

    sso_secret = None
    nonce_service = None

    def get(self, request, **kwargs):  # pylint: disable=unused-argument
        """Performs the session creation"""
        try:
            sso = request.GET['sso']
            sig = request.GET['sig']
        except KeyError:
            return HttpResponseBadRequest()
        client_util = utils.SSOClientUtils(self.sso_secret, None)
        if not client_util.validate_sso_against_sid(sso, sig):
            return HttpResponseBadRequest()
        user_data = client_util.decode_client_data(sso)
        nonce = client_util.get_param(user_data, b'nonce')
        if self.nonce_service.is_nonce_valid(nonce):
            try:
                self.create_user_session(request,
                                         client_util.get_param(user_data, b'email'),
                                         client_util.get_param(user_data, b'external_id'),
                                         client_util.get_param(user_data, b'username'))
                # TODO what should we return here? redirect to nice index?
                return HttpResponse(status=201)
            except ValueError:  # pragma: no cover
                pass    # return bad request
            finally:
                self.nonce_service.invalidate_nonce(nonce)

        return HttpResponseBadRequest()     # pragma: no cover

    @classmethod
    def create_user_session(cls, request, user_email, external_id, username):
        # pylint: disable=unused-argument
        """
        Create user session for given user. SSO validation was successful.
        :param user_email: User email
        :param external_id: User id, unique in the external system
        :param username: Optional value of user name
        :return:
        """
        if not user_email or not username:
            raise ValueError('Missing required field')  # pragma: no cover
        user_model = get_user_model()
        user = user_model.objects.get_or_create(
            username='$sso$' + username,
            email=user_email,
            # TODO what about password, should we set some random value
            defaults={'first_name': username, 'is_active': True})
        login(request, user[0])
