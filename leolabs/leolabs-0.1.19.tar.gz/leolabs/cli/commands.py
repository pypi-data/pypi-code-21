from leolabs.cli.utils import *

def require_catalog_number(catalog_number=None, norad_catalog_number=None):
    if not catalog_number and not norad_catalog_number:
        raise ValueError('Must provide either --catalog-number or --norad-catalog-number')

def require_timespan(start_time=None, end_time=None):
    if not start_time or not end_time:
        raise ValueError('Must provide --start-time and --end-time')

def require_instrument(instrument=None):
    if not instrument:
        raise ValueError('Must provide --instrument')

def require_task(task=None):
    if not task:
        raise ValueError('Must provide --task')

def get_catalog_number(catalog_number=None, norad_catalog_number=None, default=None):
    if catalog_number:
        return catalog_number
    elif norad_catalog_number:
        search_results = catalog_search(norad_catalog_number)
        if search_results:
            return search_results['catalogNumber']
    return default

def catalog_list(**kwargs):
    resource = '/catalog/objects'
    response = api_request(resource)
    return response

def catalog_get(catalog_number=None, norad_catalog_number=None, **kwargs):
    require_catalog_number(catalog_number, norad_catalog_number)
    catalog_number = get_catalog_number(catalog_number, norad_catalog_number)
    resource = '/catalog/objects/{0}'.format(catalog_number)
    response = api_request(resource)
    return response

def catalog_get_measurements(catalog_number=None, norad_catalog_number=None, start_time=None, end_time=None, **kwargs):
    require_catalog_number(catalog_number, norad_catalog_number)
    require_timespan(start_time, end_time)

    catalog_number = get_catalog_number(catalog_number, norad_catalog_number)

    params = {'startTime': start_time, 'endTime': end_time}
    resource = '/catalog/objects/{0}/measurements'.format(catalog_number)
    response = api_request(resource, params=params)
    return response

def catalog_search(norad_catalog_number=None, **kwargs):
    resource = '/catalog/objects/search?noradCatalogNumber={0}'.format(norad_catalog_number)
    response = api_request(resource)
    if response and 'catalogNumber' in response:
        return response
    return None

def catalog_create_task(catalog_number=None, norad_catalog_number=None, start_time=None, end_time=None, **kwargs):
    require_catalog_number(catalog_number, norad_catalog_number)
    require_timespan(start_time, end_time)
    catalog_number = get_catalog_number(catalog_number, norad_catalog_number)

    resource = '/catalog/objects/{0}/tasks'.format(catalog_number)
    response = api_request(resource, data={'startTime': start_time, 'endTime': end_time, 'priority': 100})
    return response

def catalog_planned_passes(catalog_number=None, norad_catalog_number=None, **kwargs):
    catalog_number = get_catalog_number(catalog_number, norad_catalog_number, 'all')

    resource = '/catalog/objects/{0}/passes/planned'.format(catalog_number)
    response = api_request(resource)
    return response

def catalog_list_states(catalog_number=None, norad_catalog_number=None, start_time=None, end_time=None, latest=None, **kwargs):
    if latest is None:
        require_timespan(start_time, end_time)

    catalog_number = get_catalog_number(catalog_number, norad_catalog_number, 'all')

    if latest:
        params = {'latest': 1}
    else:
        params = {'startTime': start_time, 'endTime': end_time}
    resource = '/catalog/objects/{0}/states'.format(catalog_number)
    response = api_request(resource, params=params)
    return response

def catalog_get_state(catalog_number=None, norad_catalog_number=None, state=None, **kwargs):
    require_catalog_number(catalog_number, norad_catalog_number)
    catalog_number = get_catalog_number(catalog_number, norad_catalog_number)
    resource = '/catalog/objects/{0}/states/{1}'.format(catalog_number, state)
    response = api_request(resource)
    return response

def catalog_get_statistics(catalog_number=None, norad_catalog_number=None, state=None, **kwargs):
    catalog_number = get_catalog_number(catalog_number, norad_catalog_number, 'all')
    resource = '/catalog/objects/{0}/statistics'.format(catalog_number)
    response = api_request(resource)
    return response

def catalog_get_propagation(catalog_number=None, norad_catalog_number=None, state=None, start_time=None, end_time=None, timestep=None, **kwargs):
    require_catalog_number(catalog_number, norad_catalog_number)
    catalog_number = get_catalog_number(catalog_number, norad_catalog_number)
    params = {'startTime': start_time, 'endTime': end_time, 'timestep': timestep}
    resource = '/catalog/objects/{0}/states/{1}/propagations'.format(catalog_number, state)
    response = api_request(resource, params=params)
    return response

def instruments_list(**kwargs):
    resource = '/instruments'
    response = api_request(resource)
    return response

def instruments_get(instrument=None, **kwargs):
    require_instrument(instrument)
    resource = '/instruments/{0}'.format(instrument)
    response = api_request(resource)
    return response

def instruments_get_statistics(instrument=None, **kwargs):
    if not instrument:
        instrument = 'all'
    resource = '/instruments/{0}/statistics'.format(instrument)
    response = api_request(resource)
    return response

def instruments_list_tasks(instrument=None, **kwargs):
    require_instrument(instrument)

    resource = '/instruments/{0}/tasks'.format(instrument)
    response = api_request(resource)
    return response

def instruments_create_task(instrument=None, start_time=None, end_time=None, **kwargs):
    require_instrument(instrument)
    require_timespan(start_time, end_time)
    data = {'startTime': start_time, 'endTime': end_time}
    resource = '/instruments/{0}/tasks'.format(instrument)
    response = api_request(resource, data=data)
    return response

def instruments_get_task(instrument=None, task=None, **kwargs):
    require_instrument(instrument)
    require_task(task)

    resource = '/instruments/{0}/tasks/{1}'.format(instrument, task)
    response = api_request(resource)
    return response

def instruments_get_task_measurements(instrument=None, task=None, **kwargs):
    require_instrument(instrument)
    require_task(task)

    resource = '/instruments/{0}/tasks/{1}/measurements'.format(instrument, task)
    response = api_request(resource)
    return response

def configure(**kwargs):
    configparser = import_configparser()

    from os.path import expanduser
    home_dir = expanduser("~")
    leolabs_dir = os.path.join(home_dir, '.leolabs')

    try:
      os.makedirs(leolabs_dir)
    except:
      pass

    config_path = os.path.join(leolabs_dir, 'config')

    access_key = prompt('Access Key: ')
    secret_key = prompt('Secret Key: ')

    config = configparser.ConfigParser()
    config.add_section('credentials')
    config.set('credentials', 'access_key', access_key)
    config.set('credentials', 'secret_key', secret_key)

    with open(config_path, 'w') as f:
      config.write(f)

    return None

