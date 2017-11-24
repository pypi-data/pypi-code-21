from cms_qe_auth.utils import pk_to_uidb64
from cms_qe_auth.models import User
from django.urls import reverse
from pytest_data import use_data


@use_data(user_data={'username': 'testuser', 'password': 'testpass'})
def test_login(client, user):
    res = client.post('/en/auth/login/', {'username': 'testuser', 'password': 'testpass'})
    assert res.status_code == 302


def test_register(client):
    assert not len(User.objects.filter(username='testuser'))
    res = client.post('/en/auth/register/', {
        'username': 'testuser',
        'password1': 'testpass',
        'password2': 'testpass',
        'email': 'testuser@example.com',
    })
    assert res.status_code == 302
    user = User.objects.get(username='testuser')
    assert user.email == 'testuser@example.com'


@use_data(user_data={'is_active': False})
def test_activation(client, user):
    assert not user.is_active
    token = user._generate_activation_token()
    uid = pk_to_uidb64(user.pk)
    url = reverse('activate', kwargs={'uidb64': uid, 'token': token})
    response = client.get(url)
    user.refresh_from_db()
    assert user.is_active
    # Test automatic login
    assert response.context['user'].is_authenticated
