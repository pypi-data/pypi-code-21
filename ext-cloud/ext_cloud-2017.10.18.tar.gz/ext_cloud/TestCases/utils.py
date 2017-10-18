
def get_cloud_obj():
    from ext_cloud import get_ext_cloud
    return get_ext_cloud("openstack", username='admin', password='admin', tenant_name='admin', auth_url='http://192.168.3.130:5000/v2.0/')
