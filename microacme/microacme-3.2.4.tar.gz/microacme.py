# Lifted from the MIT-licensed acme-tiny project, heavily modified:
#  https://github.com/diafygi/acme-tiny/blob/master/acme_tiny.py

import re
import copy
import json
import time
import logging
import textwrap
from io import BytesIO

import requests

from cryptography import x509
from cryptography.x509.oid import NameOID, ExtensionOID
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa

from jwcrypto.jwk import JWK
from jwcrypto.jws import JWS
from jwcrypto.common import base64url_encode as b64

NONCE_HEADER = 'replay-nonce'
STAGING_CA = "https://acme-staging.api.letsencrypt.org/directory"
PRODUCTION_CA = "https://acme-v01.api.letsencrypt.org/directory"
DEFAULT_CA = STAGING_CA

log = logging.getLogger(__name__)


class ACMEError(Exception):
    def __init__(self, code, message, parsed_message=None):
        self.code = code
        self.message = message
        self.parsed_message = parsed_message or {}

    def __repr__(self):
        return str(self)

    def __str__(self):
        detail = self.parsed_message.get('error', {}).get('detail', self.message)
        return "<{}: {} {}>".format(self.__class__.__name__, self.code, detail)


class RateLimit(ACMEError):
    pass


class AccountRegistrationRateLimit(RateLimit):
    pass


class DomainAuthorizationError(ACMEError):
    pass


class FQDNRateLimit(RateLimit):
    pass


class FailedAuthRateLimit(RateLimit):
    pass


class NoAvailableChallengeError(ACMEError):
    pass


class UnknownHostError(ACMEError):
    pass


class BadNonceError(ACMEError):
    pass


class ValidationConnectionError(ACMEError):
    pass


class ACMEClient:
    def __init__(self, account_key=None, CA=DEFAULT_CA, default_key_size=2048, pending_challenge_sleep_seconds=1):
        self.CA = CA
        new_account_key = account_key is None
        if new_account_key:
            self.account_key = JWK.generate(kty='RSA', size=default_key_size)
        else:
            self.account_key = JWK.from_pem(account_key)
        self.urls = self.get_acme_urls(CA)
        self.generate_request_header()
        if new_account_key:
            self.register_account()
        self.pending_challenge_sleep_seconds = pending_challenge_sleep_seconds

    def generate_request_header(self):
        self.request_header = {
            "alg": "RS256",
            "jwk": json.loads(self.account_key.export_public()),
        }

    def get_acme_urls(self, directory_url):
        response = requests.get(directory_url)
        self.set_nonce(response)
        directory_data = response.json()
        return {
            'directory': directory_url,
            'key-change': directory_data['key-change'],
            'terms-of-service': directory_data['meta']['terms-of-service'],
            'new-authz': directory_data['new-authz'],
            'new-cert': directory_data['new-cert'],
            'new-reg': directory_data['new-reg'],
            'revoke-cert': directory_data['revoke-cert'],
        }

    def send_signed_request(self, url, payload, expected_responses=None, bad_nonce_retries=2):
        expected_responses = expected_responses or {}
        signer = JWS(json.dumps(payload))
        protected = copy.deepcopy(self.request_header)
        protected["nonce"] = self.get_nonce()
        signer.add_signature(self.account_key, protected=json.dumps(protected))
        response = self.post_to_acme(url, signer.serialize())
        self.set_nonce(response)
        if response.status_code in expected_responses:
            log.info("Got {} response from {} => {}".format(response.status_code, url, expected_responses[response.status_code]))
        else:
            err = self.get_acme_error(response.status_code, response.text)
            if isinstance(err, (BadNonceError,)) and bad_nonce_retries > 0:
                self.set_nonce(None)
                return self.send_signed_request(url, payload, expected_responses, bad_nonce_retries - 1)
            raise err
        return response

    def post_to_acme(self, url, data):
        return requests.post(url, data)

    def get_nonce(self):
        if getattr(self, '_last_nonce', None) is None:
            self._last_nonce = requests.head(self.urls['directory']).headers[NONCE_HEADER]
        nonce = self._last_nonce
        self._last_nonce = None
        return nonce

    def set_nonce(self, response=None):
        if response and response.status_code < 500:
            self._last_nonce = response.headers.get(NONCE_HEADER, None)
        else:
            self._last_nonce = None

    def register_account(self):
        log.info("Registering account...")
        self.send_signed_request(
            url=self.urls['new-reg'],
            payload={
                "resource": "new-reg",
                "agreement": self.urls['terms-of-service'],
            },
            expected_responses={
                201: 'New account registered!',
                409: 'Account was already registered!'
            }
        )

    def record_progress(self, message, **data):
        pass

    def get_certificate(self, csr):
        self.record_progress('Started get_certificate', csr=csr)
        self.record_progress('Started get_domains_from_csr', csr=csr)
        domains = self.get_domains_from_csr_obj(csr)
        self.record_progress('Completed get_domains_from_csr', csr=csr, domains=domains)
        self.record_progress('Started verify_domains', domains=domains)
        self.verify_domains(domains)
        self.record_progress('Completed verify_domains', domains=domains)
        self.record_progress('Started issue_certificate', csr=csr)
        cert, ca_cert = self.issue_certificate_from_csr_obj(csr)
        self.record_progress('Completed issue_certificate', cert=cert, ca_cert=ca_cert)
        self.record_progress('Completed get_certificate', csr=csr, domains=domains, cert=cert, ca_cert=ca_cert)
        return cert, ca_cert

    def load_csr(self, pem, backend=default_backend()):
        csr = x509.load_pem_x509_csr(pem, backend)
        return csr

    def get_domains_from_csr(self, pem, backend=default_backend()):
        log.info("Parsing CSR...")
        csr = self.load_csr(pem, backend=backend)
        return self.get_domains_from_csr_obj(csr)

    def get_domains_from_csr_obj(self, csr):
        domains = set()
        common_name = csr.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
        domains.add(common_name)
        try:
            san_extension = csr.extensions.get_extension_for_oid(ExtensionOID.SUBJECT_ALTERNATIVE_NAME)
            san_names = san_extension.value.get_values_for_type(x509.DNSName)
            domains.update(san_names)
        except x509.ExtensionNotFound:
            pass
        return domains

    def verify_domains(self, domains):
        self.record_progress('Started generate_challenges')
        available_challenges = {
            domain: self.generate_challenges(domain)
            for domain in domains
        }
        self.record_progress('Completed generate_challenges', available_challenges=available_challenges)
        self.record_progress('Started selecting challenges')
        try:
            selected_challenges = {}
            for domain, challenges in available_challenges.items():
                self.record_progress('Started select_challenge', domain=domain, challenges=challenges)
                selected_challenges[domain] = self.select_challenge(domain, challenges)
                self.record_progress('Completed select_challenge', domain=domain, selected_challenge=selected_challenges[domain])
            self.record_progress('Completed selecting challenges', selected_challenges=selected_challenges)
            for domain, challenge in selected_challenges.items():
                self.record_progress('Started set_challenge')
                self.set_challenge(domain, challenge)
                self.record_progress('Completed set_challenge', domain=domain, challenge=challenge)
            for domain, challenge in selected_challenges.items():
                self.record_progress('Started validate_challenge')
                self.validate_challenge(domain, challenge)
                self.record_progress('Completed validate_challenge', domain=domain, challenge=challenge)
            for domain, challenge in selected_challenges.items():
                self.record_progress('Started notify_challenge_met')
                self.notify_challenge_met(domain, challenge)
                self.record_progress('Completed notify_challenge_met', domain=domain, challenge=challenge)
            for domain, challenge in selected_challenges.items():
                self.record_progress('Started verify_challenge_completion')
                self.verify_challenge_completion(domain, challenge)
                self.record_progress('Completed verify_challenge_completion', domain=domain, challenge=challenge)
            for domain, challenge in selected_challenges.items():
                self.record_progress('Started cleanup_completed_challenge')
                self.cleanup_completed_challenge(domain, challenge)
                self.record_progress('Completed cleanup_completed_challenge', domain=domain, challenge=challenge)
        except ACMEError:
            self.record_progress("Started remove_failed_challenges")
            for domain, challenges in available_challenges.items():
                self.remove_failed_challenges(domain, challenges)
            self.record_progress("Completed remove_failed_challenges")
            raise

    def generate_challenges(self, domain):
        challenge_response = self.send_signed_request(
            url=self.urls['new-authz'],
            payload={
                "resource": "new-authz",
                "identifier": {"type": "dns", "value": domain},
            },
            expected_responses={
                201: "Challenge created!"
            }
        )
        return challenge_response.json()['challenges']

    def select_challenge(self, domain, challenges):
        pass

    def set_challenge(self, domain, challenge):
        raise NotImplementedError("Need to implement a function to set the challenge.")

    def get_challenge_status(self, domain, challenge):
        return requests.get(challenge['uri']).json()

    def validate_challenge(self, domain, challenge):
        """
        Used to give the ACMEClient instance a chance to make sure
        that the outside world will see the changes made by set_challenge.

        By default, does nothing.  Could be used, for example, to sleep(1) while waiting
        for an asynchronous upload to take place to a remote webserver.  Or to wait while
        DNS propagation occurs.
        """
        pass

    def notify_challenge_met(self, domain, challenge):
        self.send_signed_request(
            url=challenge['uri'],
            payload={
                "resource": "challenge",
                "keyAuthorization": self.get_key_authorization(challenge),
            },
            expected_responses={
                202: 'Notified ACME Server that challenge was met.'
            }
        )

    def verify_challenge_completion(self, domain, challenge):
        while True:
            challenge_status = self.get_challenge_status(domain, challenge)
            if challenge_status['status'] == "pending":
                time.sleep(self.pending_challenge_sleep_seconds)
            elif challenge_status['status'] == "valid":
                log.info("{0} verified!".format(domain))
                return
            else:
                raise self.get_acme_error(400, json.dumps(challenge_status))

    def cleanup_completed_challenge(self, domain, challenge):
        pass

    def remove_failed_challenges(self, domain, challenges):
        pass

    def get_key_authorization(self, challenge):
        return "{0}.{1}".format(challenge['token'], self.account_key.thumbprint())

    def issue_certificate_from_csr_obj(self, csr):
        log.info("Issuing certificate...")
        response = self.send_signed_request(
            url=self.urls["new-cert"],
            payload={
                "resource": "new-cert",
                "csr": b64(csr.public_bytes(serialization.Encoding.DER)),
            },
            expected_responses={201: "New certificate issued!"}
        )
        return self.format_certificate(response.content), self.get_ca_cert(response)

    def get_ca_cert(self, response):
        self._cached_ca_certs = getattr(self, '_cached_ca_certs', {})
        ca_url = response.links.get('up', {}).get('url')
        if not ca_url:
            log.warning("CA cert not referenced in Link header of cert response.")
            return None
        if ca_url not in self._cached_ca_certs:
            log.debug("Retrieving CA cert from: {}".format(ca_url))
            resp = requests.get(ca_url)
            issuer_cert = x509.load_der_x509_certificate(resp.content, default_backend())
            pem_text = issuer_cert.public_bytes(serialization.Encoding.PEM).decode()
            self._cached_ca_certs[ca_url] = pem_text
        else:
            log.debug("Using cached CA cert instead of retrieving from: {}".format(ca_url))
        return self._cached_ca_certs[ca_url]

    def format_certificate(self, material):
        cert_obj = der_to_cert(material)
        pem = cert_to_pem(cert_obj)
        return pem.decode('utf8')

    def get_acme_error(self, code, message):
        try:
            parsed = json.loads(message)
            error = parsed['error'] if 'error' in parsed else parsed
        except (ValueError, TypeError, KeyError):  # No JSON!
            return ACMEError(code, message)
        if error['type'] == 'urn:acme:error:rateLimited':
            detail = error['detail'].lower()
            if 'exact set of domains' in detail:
                return FQDNRateLimit(code, error['detail'], parsed)
            if 'too many failed authorizations recently' in detail:
                return FailedAuthRateLimit(code, error['detail'], parsed)
            elif 'error creating new registration' in detail:
                return AccountRegistrationRateLimit(code, error['detail'], parsed)
            return RateLimit(code, message, parsed)
        elif error['type'] == "urn:acme:error:unauthorized":
            return DomainAuthorizationError(code, message, parsed)
        elif error['type'] == "urn:acme:error:unknownHost":
            return UnknownHostError(code, message, parsed)
        elif error['type'] == "urn:acme:error:badNonce":
            return BadNonceError(code, message, parsed)
        elif error['type'] == "urn:acme:error:connection":
            return ValidationConnectionError(code, message, parsed)
        return ACMEError(code, message, parsed)


class GenericACMEClient(ACMEClient):
    """
    Use this class as an example to build your
    ACME client.  Override the methods below
    to customize the challenge/response behavior
    of the ACME client.
    """
    def select_challenge(self, domain, challenges):
        """
        Each domain has multiple options for solving challenges.

        Override this function to pick which challenge you want to
        solve for this domain.
        """
        pass

    def set_challenge(self, domain, challenge):
        """
        After a challenge has been selected, it needs to actually exist somewhere.

        This is where you fulfill the challenge requirements.
        """
        raise NotImplementedError("Need to implement a function to set the challenge.")

    def validate_challenge(self, domain, challenge):
        """
        Used to give the ACMEClient instance a chance to make sure
        that the outside world will see the changes made by set_challenge.

        By default, does nothing.  Could be used, for example, to sleep(1) while waiting
        for an asynchronous upload to take place to a remote webserver.  Or to wait while
        DNS propagation occurs.
        """
        pass

    def cleanup_completed_challenge(self, domain, challenge):
        """
        This method is called after the challenge has succeeded.  It is used
        to cleanup any artifacts of solving the challenge.
        """
        pass


class HTTPACMEClient(ACMEClient):
    def select_challenge(self, domain, challenges):
        for challenge in challenges:
            if challenge['type'] == 'http-01':
                return challenge
        raise NoAvailableChallengeError(code=500, message='{"error": "no challenges acceptable to client"}')


def generate_rsa_key(key_bits=3072, public_exponent=65537, backend=default_backend()):
    return rsa.generate_private_key(
        public_exponent=public_exponent,
        key_size=key_bits,
        backend=backend
    )


def crypto_key_to_pem(key, passphrase=None):
    "Write our key to disk for safe keeping"
    kwargs = {
        "encoding": serialization.Encoding.PEM,
        "format": serialization.PrivateFormat.TraditionalOpenSSL,
        "encryption_algorithm": serialization.NoEncryption(),
    }
    if passphrase is not None:
        kwargs['encryption_algorithm'] = serialization.BestAvailableEncryption(passphrase)
    with BytesIO() as f:
        f.write(key.private_bytes(**kwargs))
        return f.getvalue()


def pem_to_crypto_key(pem, passphrase=None, backend=default_backend()):
    return serialization.load_pem_private_key(pem, passphrase, backend)


def generate_crypto_key(key_size=2048, backend=default_backend()):
    return rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
        backend=backend,
    )


def csr_to_pem(csr):
    with BytesIO() as f:
        f.write(csr.public_bytes(serialization.Encoding.PEM))
        return f.getvalue()


def pem_to_csr(pem, backend=default_backend()):
    csr_obj = x509.load_pem_x509_csr(pem, default_backend())
    return csr_obj


def pem_to_cert(pem, backend=default_backend()):
    cert_obj = x509.load_pem_x509_certificate(pem, backend=backend)
    return cert_obj


def der_to_cert(der_material, backend=default_backend()):
    cert_obj = backend.load_der_x509_certificate(der_material)
    return cert_obj


def cert_to_pem(cert_obj):
    with BytesIO() as f:
        f.write(cert_obj.public_bytes(serialization.Encoding.PEM))
        return f.getvalue()


def generate_csr(private_key, country, state, locality, org_name, common_name, alt_names=None, backend=default_backend(), auto_www=True):
    alt_names = set(alt_names or [])

    if not common_name.startswith('www.') and auto_www:
        alt_names.add(common_name)
        common_name = 'www.' + common_name
    # Generate a CSR
    csr = x509.CertificateSigningRequestBuilder()
    
    # Add our basic info to it...
    csr = csr.subject_name(x509.Name([
        # Provide various details about who we are.
        x509.NameAttribute(NameOID.COUNTRY_NAME, country),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, state),
        x509.NameAttribute(NameOID.LOCALITY_NAME, locality),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, org_name),
        x509.NameAttribute(NameOID.COMMON_NAME, common_name),
    ]))

    # Add SANs
    if alt_names:
        csr = csr.add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName(alt_name) for alt_name in alt_names
            ]),
            critical=False,
        )

    # Sign the CSR with our private key.
    csr = csr.sign(private_key, hashes.SHA256(), backend)
    return csr
