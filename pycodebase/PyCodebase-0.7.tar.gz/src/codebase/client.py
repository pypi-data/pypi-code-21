import ConfigParser
import logging
import os

import notrequests

from . import utils


CODEBASE_API_URL = 'https://api3.codebasehq.com'
logger = logging.getLogger(__file__)


class _Client(object):
    """Codebase API client class."""
    def __init__(self, (username, key)):
        self.auth = (username, key)
        self.base_url = CODEBASE_API_URL

        if not self.base_url.endswith('/'):
            self.base_url += '/'

    def _api_method(self, method, path, params=None, json=None, files=None):
        url = self.base_url + path
        headers = {'Accept': 'application/json'}

        logger.debug('%r %r params:%r', method, url, params)
        response = notrequests.request(
            method,
            url,
            auth=self.auth,
            params=params,
            headers=headers,
            json=json,
            files=files,
            timeout=30,
        )

        try:
            response.raise_for_status()
        except notrequests.HTTPError:
            msg = 'Response %r for %r. Content: %r'
            logger.info(msg, response.status_code, url, response.content)
            raise

        return response

    def _api_put(self, path, params=None, json=None, files=None):
        return self._api_method('PUT', path, params=params, json=json, files=files)

    def _api_post(self, path, params=None, json=None, files=None):
        return self._api_method('POST', path, params=params, json=json, files=files)

    def _api_get(self, path, params=None):
        return self._api_method('GET', path, params=params)

    def _api_get_generator(self, path, params=None):
        """Yields pages of results, until a request gets a 404 response."""
        params = dict(params) if params else {}
        params['page'] = 1

        while True:
            try:
                response = self._api_get(path, params=params)
            except notrequests.HTTPError:
                break
            else:
                yield response

                params['page'] += 1

    def _get_activity(self, path, raw=True, since=None):
        # This is used for both /activity and /foo/activity APIs.

        params = {}

        if raw:
            params['raw'] = 'true'

        if since:
            params['since'] = utils.format_since_dt(since)

        for response in self._api_get_generator(path, params=params):
            data = response.json()

            # /:project/activity returns an empty list, status 200 when there
            # are no more events.
            if not data:
                break

            for obj in data:
                yield obj['event']

    def get_users(self):
        """Get all users for this account.

        :rtype: generator
        """
        path = 'users'
        data = self._api_get(path).json()

        for obj in data:
            yield obj['user']

    def get_activity(self, raw=True, since=None):
        """Get all events on the account.

        :param raw: show all details
        :param since: exclude activity before this date
        :type raw: bool
        :type since: datetime.datetime
        :rtype: generator
        """
        path = 'activity'

        return self._get_activity(path, raw=raw, since=since)

    def get_projects(self):
        """Get all the projects on an account.

        :rtype: generator
        """
        # The API for projects is not paginated, all projects in one request.

        path = 'projects'
        data = self._api_get(path).json()

        for obj in data:
            yield obj['project']

    def get_project_users(self, project):
        """Get the users assigned to a project.

        :param project: permalink for a project
        :type project: str
        :rtype: generator
        """
        path = '%s/assignments' % project
        data = self._api_get(path).json()

        for obj in data:
            yield obj['user']

    def get_project_activity(self, project, raw=True, since=None):
        """Get events for a project.

        :param project: permalink for a project
        :param raw: show all details
        :param since: exclude activity before this date
        :type project: str
        :type raw: bool
        :type since: datetime.datetime
        :rtype: generator
        """
        path = '%s/activity' % project

        return self._get_activity(path, raw=raw, since=since)

    def get_repositories(self, project):
        """Get the code repositories for a project.

        :param project: permalink for a project
        :type project: str
        :rtype: generator
        """
        path = '%s/repositories' % (project,)
        response = self._api_get(path)
        data = response.json()

        for obj in data:
            yield obj['repository']

    def get_commits(self, project, repo, ref):
        """Get commits in a project's repository for the given reference.

        :param project: permalink for a project
        :param repo: permalink for a repository in the project
        :param ref: branch, tag or commit reference
        :type project: str
        :type repo: str
        :type ref: str
        :rtype: generator
        """
        path = '%s/%s/commits/%s' % (project, repo, ref)

        for response in self._api_get_generator(path):
            data = response.json()

            # The API is supposed to 404 when there are no more pages, but
            # /:project/:repo/commits/:ref returns an empty list, status 200.
            if not data:
                break

            for obj in data:
                yield obj['commit']

    def get_deployments(self, project, repo):
        """Get the deployments recorded for a project.

        :param project: permalink for a project
        :param repo: permalink for a repository in the project
        :type project: str
        :type repo: str
        :rtype: generator
        """
        path = '%s/%s/deployments' % (project, repo)

        for response in self._api_get_generator(path):
            data = response.json()

            # The API is supposed to 404 when there are no more pages, but
            # /:project/:repo/deployments returns an empty list, status 200.
            if not data:
                break

            for obj in data:
                yield obj['deployment']

    def create_deployment(self, project, repo, branch, revision, environment, servers):
        """Creates a new deployment.

        You can create a deployment even if the named repo does not exist, but
        then the deployment will not appear when listing deployments.

        :param project: permalink for a project
        :param repo: permalink for a repository in the project
        :param branch: git branch name
        :param revision: git revision ID
        :param environment: a name (e.g. "live" or "staging")
        :param servers: comma-separated list of server names
        :type project: str
        :type repo: str
        :type branch: str
        :type revision: str
        :type evnvironment: str
        :type servers: str
        """
        path = '%s/%s/deployments' % (project, repo)

        payload = {
            'deployment': {
                'branch': branch,
                'revision': revision,
                'environment': environment,
                'servers': servers,
            },
        }

        response = self._api_post(path, json=payload)
        data = response.json()

        return data

    def get_milestones(self, project):
        """Get the milestones for a project.

        :param project: permalink for a project
        :type project: str
        :rtype: generator
        """
        path = '%s/milestones' % (project,)

        # Seems to be unpaginated.
        response = self._api_get(path)
        data = response.json()

        for obj in data:
            yield obj['ticketing_milestone']

    def create_milestone(self, project, name, deadline=None, description=None,
            estimated_time=None, parent_id=None,
            responsible_user_id=None, start_at=None, status=None):
        """Create a new milestone.

        See the API documentation on `milestones`_ for details.

        .. note:: The Codebase API allows multiple milestones to have the same
            name, and this method does not check for duplicates.

        .. _milestones: https://support.codebasehq.com/kb/tickets-and-milestones/milestones

        :param project: permalink for a project
        :param name: new milestone's name
        :param deadline: the date of this milestone's deadline
        :param description: a long description for the new milestone
        :param estimated_time: the estimated time for the milestone
        :param parent_id: the ID of this milestone's parent milestone
        :param responsible_user_id: the id of the user responsible for the milestone
        :param start_at: the date this milestone begins
        :param status: the milestone status. One of "active", "completed" or "cancelled"
        :type project: str
        :type name: str
        :type deadline: str|datetime.date
        :type description: str
        :type estimated_time: int
        :type parent_id: str
        :type responsible_user_id: str
        :type start_at: str|datetime.date
        :type status: str
        :rtype: dict
        """
        path = '%s/milestones' % (project,)

        milestone_data = utils.build_milestone_payload(deadline=deadline,
            description=description, estimated_time=estimated_time, name=name,
            parent_id=parent_id, responsible_user_id=responsible_user_id,
            start_at=start_at, status=status)

        payload = {'ticketing_milestone': milestone_data}
        response = self._api_post(path, json=payload)
        data = response.json()

        return data

    def update_milestone(self, project, milestone_id, deadline=None,
            description=None, estimated_time=None, name=None, parent_id=None,
            responsible_user_id=None, start_at=None, status=None):
        """Update an existing milestone."""
        path = '%s/milestones/%s' % (project, milestone_id)

        milestone_data = utils.build_milestone_payload(deadline=deadline,
            description=description, estimated_time=estimated_time, name=name,
            parent_id=parent_id, responsible_user_id=responsible_user_id,
            start_at=start_at, status=status)

        payload = {'ticketing_milestone': milestone_data}
        response = self._api_put(path, json=payload)
        data = response.json()

        return data

    def get_tickets(self, project, assignee=None, status=None, category=None,
            type=None, priority=None, milestone=None):
        """Get all tickets on a project, or search for tickets.

        Search terms can be a string, or a list of strings.

        :param project: permalink for a project
        :param assignee: search for tickets assigned to a user
        :param status: ticket status, e.g. "open"
        :param category: ticket category, e.g. "General"
        :param type: ticket type, e.g. "Bug"
        :param priority: ticket priority, e.g. "High"
        :param milestone: milestone, e.g. "Sprint 3"
        :type project: str
        :type assignee: str|list
        :type status: str|list
        :type category: str|list
        :type type: str|list
        :type priority: str|list
        :type milestone: str|list
        :rtype: generator
        """
        path = '%s/tickets' % project

        query = utils.build_ticket_search_query(
            assignee=assignee,
            status=status,
            category=None,
            type=type,
            priority=priority,
            milestone=milestone,
        )

        params = {'query': query} if query else {}

        for response in self._api_get_generator(path, params=params):
            data = response.json()

            for obj in data:
                yield obj['ticket']

    def create_ticket(self, project, assignee_id=None, category_id=None,
            description=None, milestone_id=None, priority_id=None,
            reporter_id=None, status_id=None, summary=None, type=None,
            upload_tokens=None):
        """Create a new ticket.

        See the API documentation on `tickets and milestones`_ for details.

        .. _tickets and milestones: https://support.codebasehq.com/kb/tickets-and-milestones
        """

        path = '%s/tickets' % project

        payload = {
            'ticket': {
                'summary': summary,
                'ticket_type': type,
                'reporter_id': reporter_id,
                'assignee_id': assignee_id,
                'category_id': category_id,
                'priority_id': priority_id,
                'status_id': status_id,
                'milestone_id': milestone_id,
                'upload_tokens': upload_tokens,
                'description': description,
            },
        }

        response = self._api_post(path, json=payload)
        data = response.json()

        return data

    def get_ticket_notes(self, project, ticket_id):
        """Get all notes for a ticket in a project.

        :param project: permalink for a project
        :param ticket_id: a ticket number
        :type project: str
        :type ticket_id: int
        :rtype: generator
        """
        # The API returns all notes in a single response. Not paginated.

        path = '%s/tickets/%s/notes' % (project, ticket_id)
        data = self._api_get(path).json()

        for obj in data:
            yield obj['ticket_note']

    def create_ticket_note(self, project, ticket_id, assignee_id=None,
            category_id=None, content=None, milestone_id=None, priority_id=None,
            private=None, status_id=None, summary=None, time_added=None,
            upload_tokens=None):
        """Create a new note on a ticket in a project.

        See the API documentation on `updating tickets`_ for details.

        .. _updating tickets: https://support.codebasehq.com/kb/tickets-and-milestones/updating-tickets
        """
        # You can change a ticket's properties by creating a note.
        path = '%s/tickets/%s/notes' % (project, ticket_id)

        note_data = utils.build_create_note_payload(
            assignee_id=assignee_id,
            category_id=category_id,
            content=content,
            milestone_id=milestone_id,
            priority_id=priority_id,
            private=private,
            status_id=status_id,
            summary=summary,
            time_added=time_added,
            upload_tokens=upload_tokens,
        )
        payload = {'ticket_note': note_data}

        data = self._api_post(path, json=payload).json()

        return data

    def upload_files(self, files):
        """Upload files.

        Each file in the list can be one of:

        * A file-like object open for reading.
        * A pair of (filename, file-like object).
        * A pair of (filename, byte-string).

        Returns a generator of upload info dictionaries. The 'identifier' key
        for an uploaded file can be used in the `upload_tokens` argument when
        creating a ticket or note.

        :param files: list of files to upload
        :type files: list
        :rtype: generator
        """
        # https://support.codebasehq.com/kb/uploading-files

        path = 'uploads'
        field_name = 'files[]'
        files_data = [(field_name, obj) for obj in files]
        response = self._api_post(path, files=files_data)
        data = response.json()

        for obj in data:
            yield obj['upload']

    def get_ticket_statuses(self, project):
        """Get all status choices in a project.

        :param project: permalink for a project
        :type project: str
        :rtype: generator
        """
        path = '%s/tickets/statuses' % project
        data = self._api_get(path).json()

        for obj in data:
            yield obj['ticketing_status']

    def get_ticket_categories(self, project):
        """Get all ticket category choices in a project.

        :param project: permalink for a project
        :type project: str
        :rtype: generator
        """
        path = '%s/tickets/categories' % project
        data = self._api_get(path).json()

        for obj in data:
            yield obj['ticketing_category']

    def get_ticket_types(self, project):
        """Get all ticket types in a project.

        :param project: permalink for a project
        :type project: str
        :rtype: generator
        """
        path = '%s/tickets/types' % project
        data = self._api_get(path).json()

        for obj in data:
            yield obj['ticketing_type']

    def get_ticket_priorities(self, project):
        """Get all ticket priorities in a project.

        :param project: permalink for a project
        :type project: str
        :rtype: generator
        """
        path = '%s/tickets/priorities' % project
        data = self._api_get(path).json()

        for obj in data:
            yield obj['ticketing_priority']

    def get_file_contents(self, project, repo, ref, file_path):
        """Get a file's content.

        :param project: permalink for a project
        :param repo: permalink for a repository in the project
        :param ref: branch, tag or commit reference
        :param file_path: path of the file
        :type project: str
        :type repo: str
        :type ref: str
        :type file_path: str
        :rtype: string

        """
        path = '%s/%s/blob/%s/%s' % (project, repo, ref, file_path)
        response = self._api_get(path)

        return response.content

    def _my_username(self):
        username, _ = self.auth
        # Convert 'example/alice' to 'alice'.
        _, _, username = username.rpartition('/')

        return username

    def get_user_keys(self, username):
        """Get public SSH keys for a user.

        The username should be the sort version of a Codebase username. If your
        API username is "example/alice" then the username is "alice".

        :param username: the user's Codebase username
        :type username: str
        """
        path = 'users/%s/public_keys' % username
        data = self._api_get(path).json()

        for obj in data:
            yield obj['public_key_join']

    def get_my_keys(self):
        """Get the public SSH keys for the current authenticated user."""
        username = self._my_username()

        return self.get_user_keys(username)

    def add_user_key(self, username, description, key):
        """Add a new SSH key for a user.

        See the documentation for `public keys`_ for details of the key format.
        See :py:meth:`~Client.get_user_keys` for the username format.

        .. _public keys: https://support.codebasehq.com/kb/public-keys

        :param username: the user's Codebase username
        :param description: a short description for the key
        :param key: the text of the public SSH key
        :type username: str
        :type description: str
        :type key: str
        """
        path = 'users/%s/public_keys' % username
        payload = {
            'public_key': {
                'description': description,
                'key': key,
            },
        }
        data = self._api_post(path, json=payload).json()

        return data

    def add_my_key(self, description, key):
        """Add a new SSH key for the current authenticated user."""
        username = self._my_username()

        return self.add_user_key(username, description, key)

    @classmethod
    def with_secrets(cls, filename):
        """Create a new instance of Client.

        The API username / key are read from a file. A filename like '~/.secrets'
        is expanded to with a home directory.

        The file must be in INI format, with a section named "api" and
        properties for "username" and "key" within the section.

        ::

            [api]
            username = example/alice
            key = topsecret

        :param filename: path to INI file
        :type filename: str
        """
        return new_client_with_secrets_from_filename(cls, filename)


class Client(_Client):
    """Codebase API client class that allows some ticket properties to be
    referenced by name instead of the object ID.
    """
    def __init__(self, *args, **kwargs):
        super(Client, self).__init__(*args, **kwargs)
        self.reset_cache()

    def reset_cache(self):
        self._cache = {}

    def use_cache(self, project, kwargs):
        """For some ticket classifiers (what Codebase calls organisational
        objects, such as status, category, etc.), return a new dict with the
        classifier's name replaced by the classifier's ID.

        This works by making an API call to get ticket statuses, etc. and
        caching the results for quick lookup. The cache can be cleared with
        Client.reset_cache().
        """
        # We take an argument like 'category', lookup a value and reassign it
        # to 'category_id'.
        classifiers = {
            'assignee': self.cache_assignee,
            'category': self.cache_category,
            'milestone': self.cache_milestone,
            'priority': self.cache_priority,
            'status': self.cache_status,
        }

        # Make a copy of the original, don't mutate the dict we were given.
        kwargs = dict(kwargs)

        # Could use a defaultdict or something. Anyway, setup project's cache.
        if project not in self._cache:
            self._cache[project] = {}

        for name in classifiers:
            if name in kwargs:
                # Check if we have cached the results for this classifier. If
                # not, then call a method like 'Client.cache_category()'
                # and assign the result to the cache. N.B. The cache is
                # per-project.
                if name not in self._cache[project]:
                    self._cache[project][name] = classifiers[name](project)

                # OK. We've cached this classifier's stuff.
                value = kwargs[name]
                value = self._cache[project][name].get(value, value)

                # Now set the '_id' version and unset the original argument.
                kwargs[name + '_id'] = value
                del kwargs[name]

        return kwargs

    def cache_assignee(self, project):
        result = {}
        users = self.get_project_users(project)

        # We allow an assignee to be specified by the username or any of their
        # email addresses.
        for user in users:
            user_id = user['id']
            result[user['username']] = user_id

            for email in user['email_addresses']:
                result[email] = user_id

        return result

    def cache_category(self, project):
        return {obj['name']: obj['id'] for obj in self.get_ticket_categories(project)}

    def cache_milestone(self, project):
        return {obj['name']: obj['id'] for obj in self.get_milestones(project)}

    def cache_priority(self, project):
        return {obj['name']: obj['id'] for obj in self.get_ticket_priorities(project)}

    def cache_status(self, project):
        return {obj['name']: obj['id'] for obj in self.get_ticket_statuses(project)}

    def create_ticket(self, project, **kwargs):
        kwargs = self.use_cache(project, kwargs)

        return super(Client, self).create_ticket(project, **kwargs)

    def create_ticket_note(self, project, ticket_id, **kwargs):
        kwargs = self.use_cache(project, kwargs)

        return super(Client, self).create_ticket_note(project, ticket_id, **kwargs)


def new_client_with_secrets_from_filename(cls, filename):
    """Returns a new instance of codebase.Client. The username / key are read
    from the filename which must be in INI format. A filename like '~/.secrets'
    is expanded to the current user's home directory.
    """
    config = ConfigParser.SafeConfigParser()

    filename = os.path.expanduser(filename)

    with open(filename) as fh:
        config.readfp(fh)

    username = config.get('api', 'username')
    key = config.get('api', 'key')

    return cls((username, key))
