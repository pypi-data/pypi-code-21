import subprocess
from requests import get, ConnectionError
from json import loads


def subprocess_cmd(command):
    """
    This method executes a cmd on the host and returns stdout.
    :param command: The command to execute.
    :return: return_stdout: the stander out to return.
    """
    process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    return_stdout = process.communicate()[0].strip().decode('ascii')
    return str(return_stdout)


def send_requests(uri):
    """
    This method sends a HTTP GET request for a given URI.
    :param uri: The URI to send the GET request to.
    :return: The json contents of the GET request 
    :raise ConnectionError: if the response status code is not 200 OK
    """
    response = get(uri)
    if response.status_code == 200:
        return loads(response.content)
    else:
        raise ConnectionError("Response Status Code: " + str(response.status_code))