import json

from cms_qe.views import get_monitoring_data


def test_get_monitoring_data():
    data = get_monitoring_data()
    assert data['status']
    assert 'cms_qe' in data['app_details']


def test_monitoring_view(client):
    result = client.get('/api/monitoring').content
    data = json.loads(str(result, 'utf8'))
    assert data['status']
