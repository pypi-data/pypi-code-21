#!/usr/bin/python
from ext_cloud import get_ext_cloud

import warnings
warnings.filterwarnings("ignore")

cloud_obj = get_ext_cloud("openstack")
# cloud_obj = get_ext_cloud("openstack", username='admin', password='admin',
#                          tenant_name='admin', auth_url='http://192.168.3.130:5000/v2.0/')

metrics = cloud_obj.resources.list_metrics()
# metrics = cloud_obj.stats.list_metrics()
for metric in metrics:
    print metric.name, '\t', metric.value, '\t', metric.timestamp
