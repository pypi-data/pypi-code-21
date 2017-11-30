'''Miscellaneous utility functions'''

# Standard library imports
import json 
import csv

# Imports
# Import as pyjwt to avoid namespace conflicts
import jwt as pyjwt
import click

# Package imports
from . import constants

# Maintain legacy meaning of jwt_signed
def jwt_signed(*args, **kwargs):
    return jwt_signed_study(*args, **kwargs)

def jwt_signed_study(
        study_id, external_id, study_api_key, subsidy_in_cents=None, 
        url_template=constants.DEEPLINK_URL_STUDY):
    '''Helper function for generating study JWT

    A user can be forwarded to Gencove by providing them with a link containing
    this JWT and they will be accepted to the referenced study.

    Link format is: https://dl.gencove.com/research/<JWT>

    Args:
        study_id (int): study id from gencove backend
        external_id (str): external user id for identifying user
        study_api_key (str): secret study api key used for signing JWT and
            verifying authenticity of token.
        subsidy_in_cents (int): amount the kit will be subsidized by study
        url_template (str): template to use for URL. Must contain "{jwt}". Set 
            to None to output only JWT without URL.

    Returns:
        str: encoded JWT

    Raises:
        TypeError: a parameter has incorrect type
        ValueError: a parameter has incorrect value

    '''

    # Type validation of study_id
    if type(study_id) is not int:
        raise TypeError('study_id must be an integer')

    if study_id<=0:
        raise ValueError('study_id must be >0')

    # Type validation of external_id
    if not (type(external_id) is int or is_text(external_id)):
        raise TypeError('external_id must be integer or text')

    # Type validation of study_api_key
    if not is_text(study_api_key):
        raise TypeError('study_api_key must be a text')

    payload = {
        'study_id': study_id,
        'external_id': external_id
    }

    if subsidy_in_cents is not None:
        if type(subsidy_in_cents) is not int:
            raise TypeError('subsidy_in_cents must be an integer')

        if subsidy_in_cents<0:
            raise ValueError('subsidy_in_cents must be >=0')

        payload['subsidy_in_cents'] = subsidy_in_cents

    jwt_out = pyjwt.encode(payload, study_api_key, algorithm='HS256')\
        .decode('ascii')

    if url_template:
        if not is_text(url_template):
            raise TypeError('url_template must be text')

        if '{jwt}' not in url_template:
            raise ValueError('url_template must contain \'{jwt}\'')

        return url_template.format(jwt=jwt_out)
    else:
        return jwt_out

def jwt_signed_app(
        app_id, external_id, signing_key, subsidy_in_cents=None, 
        url_template=constants.DEEPLINK_URL_APP):
    '''Helper function for generating app JWT

    A user can be forwarded to Gencove by providing them with a link containing
    this JWT and they will be accepted to the referenced app.

    Link format is: https://dl.gencove.com/connect/<JWT>

    Args:
        app_id (int): app id from gencove backend
        external_id (str): external user id for identifying user
        signing_key (str): secret app signing key used for signing JWT and
            verifying authenticity of token.
        subsidy_in_cents (int): amount the kit will be subsidized by app
        url_template (str): template to use for URL. Must contain "{jwt}". Set 
            to None to output only JWT without URL.

    Returns:
        str: encoded JWT

    Raises:
        TypeError: a parameter has incorrect type
        ValueError: a parameter has incorrect value

    '''

    # Type validation of app_id
    if type(app_id) is not int:
        raise TypeError('app_id must be an integer')

    if app_id<=0:
        raise ValueError('app_id must be >0')

    # Type validation of external_id
    if not (type(external_id) is int or is_text(external_id)):
        raise TypeError('external_id must be integer or text')

    # Type validation of signing_key
    if not is_text(signing_key):
        raise TypeError('signing_key must be a text')

    payload = {
        'app_id': app_id,
        'external_id': external_id
    }

    if subsidy_in_cents is not None:
        if type(subsidy_in_cents) is not int:
            raise TypeError('subsidy_in_cents must be an integer')

        if subsidy_in_cents<0:
            raise ValueError('subsidy_in_cents must be >=0')

        payload['subsidy_in_cents'] = subsidy_in_cents

    jwt_out = pyjwt.encode(payload, signing_key, algorithm='HS256')\
        .decode('ascii')

    if url_template:
        if not is_text(url_template):
            raise TypeError('url_template must be text')

        if '{jwt}' not in url_template:
            raise ValueError('url_template must contain \'{jwt}\'')

        return url_template.format(jwt=jwt_out)
    else:
        return jwt_out

def pretty_json(dict_in, file_obj=None):
    '''Converts dict to human-readable JSON

    Args:
        dict_in (dict): input dictionary

    Returns:
        str: formatted JSON
    '''
    kwargs = {
        'sort_keys': True, 
        'indent': 2, 
        'separators': (',', ': ')    
    }
    if file_obj:
        json.dump(
            dict_in, 
            file_obj,
            **kwargs
        )
    else:
        return json.dumps(
            dict_in, 
            **kwargs
        )

def raw_data_csv(list_in, file_obj, header=True):
    '''Converts list of raw data dicts to csv

    Args:
        list_in (list): input list

    Returns:
        str: formatted CSV
    '''

    line_order = [
        'external_id',
        'member_id',
        'bam_url_s3',
        'bai_url_s3',
        'vcf_url_s3',
        'tbi_url_s3',
        'csi_url_s3',
        'snp_url_s3',
        'fastq_nongrch37_url_s3',
        'ancestry_url_s3',
        'microbiome_url_s3'
    ]

    writer = csv.writer(file_obj)

    if header:
        writer.writerow(line_order)

    for el in list_in:
        line = [el[key] for key in line_order]
        writer.writerow(line)

def get_output(dict_in, json_default=False):
    '''Grab developer- or user-targeted output from backend response represented
    as dictionary
    
    Extracts respective keys from dictionary and returns them as str. In case 
    the keys do not exist, optionally return whole dictionary as JSON.

    Args: 
        dict_in (dict): input dictionary representing a backend response
        json_default (bool): whether to convert dictionary to JSON as default

    Returns:
        str: developer- or user-targeted output
    '''
    if 'message_details' in dict_in:
        return dict_in['message_details']
    elif 'message' in dict_in:
        return dict_in['message']
    elif 'description' in dict_in:
        return dict_in['description']
    elif json_default:
        return pretty_json(dict_in)

def extract_backend_message(response):
    '''Grab most informative information from response.

    Attempt to decode JSON content of response and potentially use get_output() 
    to extract informative output. In case it fails to decode JSON, it will 
    return response.text

    Args:
        response (requests.Response): HTTP response to decode

    Returns:
        str: most informative response
    '''
    try:
        response_dict = response.json()
        return get_output(response_dict, json_default=True)
    except ValueError as e:
        return response.text

def is_text(value):
    '''Determines if value is text (str or unicode)

    Args:
        value (any): value to be tested

    Returns:
        bool: whether value is text (str or unicode)
    '''

    # Python 2/3 compat:
    try:
        return isinstance(value, basestring)
    except NameError as e:
        return isinstance(value, str)
    

def prompt_stderr(
        val, label='Password', confirmation_prompt=False, hide_input=True):
    '''Prompt for input, but output label to stderr

    Uses standard prompt() function from Click library for grabbing a value if
    it is None. It outputs to stderr to keep prompt out of standard pipes. Also 
    hides input and allows for a confirmation prompt.

    Args:
        val (str): value to check
        label (str): label to use for prompt
        confirmation_prompt (bool): whether to prompt for confirmation
        hide_input (bool): whether to hide input

    Returns:
        str: val or acquired input in val was None

    Raises:
        click.Abort: in case user aborts when prompted for input
    '''
    new_val = val
    if new_val is None:
        # try:
        new_val = click.prompt(
            label, hide_input=hide_input, err=True, 
            confirmation_prompt=confirmation_prompt)
        # except click.Abort as e: 
        #     click.echo('User abort', err=True)
        #     exit(1)

    return new_val

def get_envs_string():
    '''Return a list of environments

    Returns:
        str: comma-separated list of environments
    '''
    return ', '.join(constants.ENVS.keys())
