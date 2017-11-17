from __future__ import print_function
import requests
import logging
import json
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from .Project import Project

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

logger_name = 'qmenta.client'


# FIXME: Update the base url below when DEV-761 is fixed.
class Account:
    """
    It represent your QMENTA Account and implements the HTTP connection
    with the server. Once it is instantiated it will act as an identifier
    used by the rest of objects.

    :param username: username of the platform. To get one go to https://platform.mint-labs.com
    :param password: the password assigned to the username.
    :param base_url: the base url of the platform.
    :param verify_certificates: verify SSL certificates?

    :type username: String
    :type password: String
    """

    def __init__(self, username, password, base_url="https://platform.qmenta.com", verify_certificates=True):
        self._cookie = None
        self._project_id = None
        self.username = username
        self.password = password
        self.baseurl = base_url
        self.verify_certificates = verify_certificates
        self.login()

    def __repr__(self):
        rep = "<Account session for {}>".format(self.username)
        return rep

    def login(self):
        """Login to the platform."""
        content = self.send_request("login",
                                    {"username": self.username,
                                     "password": self.password})
        logger = logging.getLogger(logger_name)
        if content["success"]:
            logger.info("Logged in as {0}".format(self.username))
            return True
        else:
            logger.error("Login is invalid")
            return False

    def logout(self):
        """
        Logout from the platform.

        :return: True if logout was successful, False otherwise.
        :rtype: Bool
        """

        content = self.send_request("logout")
        logger = logging.getLogger(logger_name)
        if content["success"]:
            logger.info("Logged out successfully")
            self._cookie = None
            return True
        else:
            logger.error("Logout was unsuccesful")
            return False

    def get_project(self, project_id):
        """
        Retrieve a project instance, given its id, which can be obtained
        checking account.projects.

        :param project_id: id of the project to retrieve, either the numeric
                           id or the name
        :type project_id: Int or string

        :return: a project object representing the desired project
        :rtype: Project
        """
        if type(project_id) == int or type(project_id) == float:
            return Project(self, int(project_id))
        elif type(project_id) == str:
            projects = self.projects
            projects_match = [
                proj for proj in projects if proj['name'] == project_id]
            if not projects_match:
                raise Exception(("Project {} does not exist or is not "
                                 "available for this user."
                                 ).format(project_id))
            return Project(self, int(projects_match[0]["id"]))

    @property
    def projects(self):
        """
        List all the projects available to the current user.

        :return: List of project identifiers (strings)
        :rtype: List(Strings)
        """

        content = self.send_request("projectset_manager/get_projectset_list")
        logger = logging.getLogger(logger_name)
        if content.get("success", False):
            titles = []
            for project in content["data"]:
                titles.append({"name": project["name"], "id": project["_id"]})
            return titles
        else:
            message = "unable to get project list"
            logger.error('{}; response data: {}'.format(message, content))
            raise Exception(message)

    def add_project(self, project_abbreviation, project_name,
                    description="", users=[], from_date="", to_date=""):
        """
        Add a new project to the user account.

        :param project_abbreviation: Abbreviation of the project name.
        :param project_name: Project name.
        :param description: Description of the project.
        :param users: List of users to which this project is available.
        :param from_date: Date of beginning of the project.
        :param to_date: Date of ending of the project.

        :type project_abbreviation: String
        :type project_name: String
        :type description: String
        :type users: List(Strings)
        :type from_date: String
        :type to_date: String

        :return: True if project was correctly added, False otherwise
        :rtype: Bool

        """
        logger = logging.getLogger(logger_name)
        for project in self.projects:
            if project["name"] == project_name:
                logger.error("Project name or abbreviation already exists.")
                return False

        content = self.send_request(
            "projectset_manager/upsert_project",
            req_parameters={"name": project_name,
                            "description": description,
                            "from_date": from_date,
                            "to_date": to_date,
                            "abbr": project_abbreviation,
                            "users": "|".join(users)})
        if content.get("success", False):
            for project in self.projects:
                if project["name"] == project_name:
                    logger.info("Project was successfuly created.")
                    return Project(self, int(project["id"]))
            logger.error("Project could note be created.")
            return False
        else:
            logger.error("There was an error.")
            return False

    # This function should be made private. See DEV-412.
    def send_request(self, path, req_parameters=None, req_headers=None,
                     stream=False, return_raw_response=False,
                     response_timeout=900.0):
        """
        Send a request to the QMENTA Platform.

        Interaction with the server is performed as POST requests.

        :param req_parameters: data to send in the POST request.

        :param req_headers: "extra" headers to include in the request:
                            {"header-name": "value"}.
        :param stream: defer downloading the response body until accessing the
                       Response.content attribute.

        :param return_raw_response: When True, return the response from the
                                    server as-is. When False (by default),
                                    parse the answer as json to return a
                                    dictionary.
        :param response_timeout: The timeout time to wait for the response.

        :type req_parameters: Dict
        :type req_headers: Dict
        :type stream: Bool
        :type return_raw_response: Bool
        """

        req_headers = req_headers or {}
        req_url = '/'.join((self.baseurl, path))
        if self._cookie is not None:
            req_headers["Cookie"] = self._cookie
        req_headers["Mint-Api-Call"] = "1"

        logger = logging.getLogger(logger_name)
        try:
            response = requests.post(
                req_url,
                data=req_parameters or {},
                headers=req_headers,
                timeout=response_timeout,
                stream=stream,
                verify=self.verify_certificates
            )
            response.raise_for_status()
        except Exception as e:
            error = "Could not send request. ERROR: {0}".format(e)
            logger.error(error)
            raise

        # Set the login cookie in our object
        if "set-cookie" in response.headers:
            self._cookie = response.headers["set-cookie"]

        if return_raw_response:
            return response

        # raise exception if there is no response from server
        if not response:
            error = "No response from server."
            logger.error(error)
            raise Exception(error)

        try:
            parsed_content = json.loads(response.text)
        except Exception:
            error = "Could not parse the response as JSON data: {}".format(response.text)
            logger.error(error)
            raise Exception(error)

        # throw exceptions if anything strange happened
        if "error" in parsed_content:
            error = parsed_content["error"] or "Unknown error"
            logger.error(error)
            raise Exception(error)
        elif 'success' in parsed_content and parsed_content['success'] == 3:
            error = parsed_content['message']
            logger.error(error)
            raise Exception(error)
        return parsed_content
