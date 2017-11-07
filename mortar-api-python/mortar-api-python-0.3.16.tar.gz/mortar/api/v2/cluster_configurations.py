from requests.exceptions import HTTPError

def get_cluster_configuration(api, cluster_configuration_name):
    """
    Get cluster_configuration details
    
    :raises: requests.exception.HTTPError: if a 40x or 50x error occurs 
    
    :rtype: dict
    :returns: cluster_configuration or None if invalid cluster_configuration
    """
    try:
        return api.get('cluster_configuration/%s' % cluster_configuration_name)
    except HTTPError, e:
        if e.response and e.response.status_code == 404:
            return None
        else:
            raise
