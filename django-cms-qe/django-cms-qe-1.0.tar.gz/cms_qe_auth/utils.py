from django.contrib.auth import get_user_model
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

# pylint:disable=invalid-name

def pk_to_uidb64(pk):
    return urlsafe_base64_encode(force_bytes(pk))


def uidb64_to_pk(uidb64):
    return force_text(urlsafe_base64_decode(uidb64))


def get_user_by_uidb64(uidb64):
    User = get_user_model()
    try:
        pk = uidb64_to_pk(uidb64)
        user = User.objects.get(pk=pk)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    return user
