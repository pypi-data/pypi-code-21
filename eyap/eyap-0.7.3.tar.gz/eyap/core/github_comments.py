"""Module for working comments from GitHub backend.
"""

import doctest
import time
import collections
import re
import json
import logging
import zipfile
import base64

import requests

from eyap.core import comments, yap_exceptions


def fake_markdown(text, *args, **kw):
    "Fake markdown"
    _dummy_ignore = args, kw
    return text


try:
    from markdown import markdown
except ImportError as problem:
    logging.warning('\n'.join([
        'Could not import markdown package. Will render as plain.',
        'Install the markdown package if you want comments rendered as',
        'markdown.']))

    def markdown(text, *args, **kw):
        "Fake markdown by just return input text"
        dummy = args, kw
        return text


GitHubInfo = collections.namedtuple('GitHubInfo', [
    'owner', 'realm', 'user', 'token'])


class GitHubAngry(Exception):
    """Exception to indicate something wrong with github API.
    """

    def __init__(self, msg, *args, **kw):
        Exception.__init__(self, msg, *args, **kw)


class GitHubCommentGroup(object):
    """Class to represent a group of github comments.
    """

    def __init__(self, topic_re, gh_info, max_threads=None, params=None):
        """Initializer.

        :arg gh_info:    Instance of GitHubInfo describing how to access github
        :arg param=None: Optional dict of params to pass to github request

        """
        self.topic_re = topic_re
        self.gh_info = gh_info
        self.max_threads = max_threads
        self.base_url = 'https://api.github.com/repos/%s/%s' % (
            self.gh_info.owner, self.gh_info.realm)
        self.params = dict(params) if params else {}

    def get_thread_info(self, enforce_re=True):
        """Return a json list with information about threads in the group.
        """
        result = []
        my_re = re.compile(self.topic_re)
        url = '%s/issues' % (self.base_url)
        while url:
            kwargs = {} if not self.gh_info.user else {'auth': (
                self.gh_info.user, self.gh_info.token)}
            my_req = requests.get(url, params=self.params, **kwargs)
            my_json = my_req.json()
            for item in my_json:
                if (not enforce_re) or my_re.search(item['title']):
                    result.append(item)
                    if self.max_threads is not None and len(
                            result) >= self.max_threads:
                        logging.debug('Stopping after max_threads=%i threads.',
                                      len(result))
                        return result
            url = None
            if 'link' in my_req.headers:
                link = my_req.headers['link'].split(',')
                for thing in link:
                    potential_url, part = thing.split('; ')
                    if part == 'rel="next"':
                        url = potential_url.lstrip('<').rstrip('>')

        return result

    def export(self, out_filename):
        """Export desired threads as a zipfile to out_filename.
        """
        with zipfile.ZipFile(out_filename, 'w', zipfile.ZIP_DEFLATED) as arc:
            id_list = list(self.get_thread_info())
            for num, my_info in enumerate(id_list):
                logging.info('Working on item %i : %s', num, my_info['number'])
                my_thread = GitHubCommentThread(
                    self.gh_info.owner, self.gh_info.realm, my_info['title'],
                    self.gh_info.user, self.gh_info.token,
                    thread_id=my_info['number'])
                csec = my_thread.get_comment_section()
                cdict = [item.to_dict() for item in csec.comments]
                my_json = json.dumps(cdict)
                arc.writestr('%i__%s' % (my_info['number'], my_info['title']),
                             my_json)

    @staticmethod
    def _test_export():
        """Simple regression test to make sure export works.

    NOTE: this test will hit the github web site unauthenticated. There are
          pretty tight rate limits for that so if you are re-running this
          test repeatedly, it will fail. To manually verify you can set
          user and token and re-run.

>>> user, token = None, None
>>> import tempfile, shlex, os, zipfile
>>> from eyap.core import github_comments
>>> info = github_comments.GitHubInfo('octocat', 'Hello-World', user, token)
>>> group = github_comments.GitHubCommentGroup('.', info, max_threads=3)
>>> fn = tempfile.mktemp(suffix='.zip')
>>> group.export(fn)
>>> zdata = zipfile.ZipFile(fn)
>>> len(zdata.filelist)
3
>>> data = zdata.read(zdata.infolist()[0].filename)
>>> len(data) > 10
True
>>> del zdata
>>> os.remove(fn)
>>> os.path.exists(fn)
False
"""


class GitHubCommentThread(comments.CommentThread):
    """Sub-class of CommentThread using GitHub as a back-end.
    """

    __thread_id_cache = {}

    # Base url to use in searching for issues.
    search_url = 'https://api.github.com/search/issues'
    url_extras = ''  # useful in testing to add things to URL

    def __init__(self, *args, attachment_location='files', **kw):
        """Initializer.

        :arg *args, **kw:  As for CommentThread.__init__.

        """
        comments.CommentThread.__init__(self, *args, **kw)
        self.base_url = 'https://api.github.com/repos/%s/%s' % (
            self.owner, self.realm)
        self.attachment_location = attachment_location

    @classmethod
    def sleep_if_necessary(cls, user, token, endpoint='search'):
        """Sleep a little if hit github recently to honor rate limit.
        """
        info = requests.get('https://api.github.com/rate_limit',
                            auth=(user, token))
        info_dict = info.json()
        remaining = info_dict['resources'][endpoint]['remaining']
        logging.debug('Search remaining on github is at %s', remaining)
        if remaining <= 5:
            sleep_time = 120
        else:
            sleep_time = 0
        if sleep_time:
            logging.warning('Sleep %i since github requests remaining  = %i',
                            sleep_time, remaining)
            time.sleep(sleep_time)
            return True

        return False

    @classmethod
    def update_cache_key(cls, cache_key, item=None):
        """Get item in cache for cache_key and add item if item is not None.
        """
        contents = cls.__thread_id_cache.get(cache_key, None)
        if item is not None:
            cls.__thread_id_cache[cache_key] = item

        return contents

    @classmethod
    def lookup_cache_key(cls, cache_key):
        "Syntactic sugar for update_cache_key(cache_key)"

        return cls.update_cache_key(cache_key)

    def lookup_thread_id(self):
        """Lookup thread id as required by CommentThread.lookup_thread_id.

        This implementation will query GitHub with the required parameters
        to try and find the topic for the owner, realm, topic, etc., specified
        in init.
        """

        query_string = 'in:title "%s" repo:%s/%s' % (
            self.topic, self.owner, self.realm)
        cache_key = (self.owner, self.realm, self.topic)
        result = self.lookup_cache_key(cache_key)
        if result is not None:
            my_req = self.raw_pull(result)
            if my_req.status_code != 200:
                result = None  # Cached item was no good
            elif my_req.json()['title'] != self.topic:
                logging.debug('Title must have changed; ignore cache')
                result = None
            else:
                logging.debug('Using cached thread id %s for %s', str(result),
                              str(cache_key))
                return result
        data, dummy_hdr = self.raw_search(self.user, self.token, query_string)

        if data['total_count'] == 1:   # unique match
            if data['items'][0]['title'] == self.topic:
                result = data['items'][0]['number']
            else:
                result = None
        elif data['total_count'] > 1:  # multiple matches since github doesn't
            searched_data = [          # have unique search we must filter
                item for item in data['items'] if item['title'] == self.topic]
            if not searched_data:  # no matches
                return None
            elif len(searched_data) > 1:
                raise yap_exceptions.UnableToFindUniqueTopic(
                    self.topic, data['total_count'], '')
            else:
                assert len(searched_data) == 1, (
                    'Confused searching for topic "%s"' % str(self.topic))
                result = searched_data[0]['number']
        else:
            result = None
        self.update_cache_key(cache_key, result)

        return result

    @classmethod
    def raw_search(cls, user, token, query):
        """Do a raw search for github issues.

        :arg user:        Username to use in accessing github.

        :arg token:       Token to use in accessing github.

        :arg query:       String query to use in searching github.

        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        :returns:       JSON result returned from github.

        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        PURPOSE:        Search for issues on github.

        """
        cls.sleep_if_necessary(user, token)

        kwargs = {} if not user else {'auth': (user, token)}
        my_req = requests.get(cls.search_url, params={'q': query}, **kwargs)
        if my_req.status_code != 200:
            raise GitHubAngry(
                'Bad status code %s finding query %s because %s' % (
                    my_req.status_code, query, my_req.reason))

        data = my_req.json()
        return data, my_req.headers

    def raw_pull(self, topic):
        """Do a raw pull of data for given topic down from github.

        :arg topic:    String topic (i.e., issue title).

        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        :returns:      Result of request data from github API.

        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        PURPOSE:       Encapsulate call that gets raw data from github.

        """
        assert topic is not None, 'A topic of None is not allowed'
        kwargs = {} if not self.user else {'auth': (self.user, self.token)}
        my_req = requests.get('%s/issues/%s' % (
            self.base_url, topic), **kwargs)
        return my_req

    def lookup_comment_list(self):
        """Lookup list of comments for an issue.

        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        :returns:  The pair (ISSUE, COMMENTS) where ISSUE is a dict for the
                   main issue and COMMENTS is a list of comments on the issue.

        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        PURPOSE:   Do the work of getting data from github, handling paging,
                   and so on.

        """
        if self.thread_id is None:
            return None, None

        # Just pulling a single issue here so pagination shouldn't be problem
        my_req = self.raw_pull(self.thread_id)
        if my_req.status_code != 200:
            raise GitHubAngry('Bad status code %s because %s' % (
                my_req.status_code, my_req.reason))
        issue_json = my_req.json()
        comments_url = issue_json['comments_url'] + self.url_extras
        kwargs = {} if not self.user else {'auth': (self.user, self.token)}
        comments_json = []
        while comments_url:
            logging.debug('Pulling comments URL: %s', comments_url)
            c_req = requests.get(comments_url, **kwargs)
            my_json = c_req.json()
            assert isinstance(my_json, list)
            comments_json.extend(my_json)
            comments_url = None
            if 'link' in c_req.headers:  # need to handle pagination.
                logging.debug('Paginating in lookup_comment_list')
                link = c_req.headers['link'].split(',')
                for thing in link:
                    potential_url, part = thing.split('; ')
                    if part == 'rel="next"':
                        comments_url = potential_url.lstrip('<').rstrip('>')

        return issue_json, comments_json

    def lookup_comments(self, reverse=False):
        if self.thread_id is None:
            self.thread_id = self.lookup_thread_id()
        issue_json, comment_json = self.lookup_comment_list()
        if issue_json is None and comment_json is None:
            return comments.CommentSection([])
        cthread_list = [comments.SingleComment(
            issue_json['user']['login'], issue_json['created_at'],
            issue_json['body'], issue_json['html_url'],
            markup=markdown(issue_json['body'], extensions=[
                'fenced_code', 'tables', 'markdown.extensions.nl2br']))]

        for item in comment_json:
            comment = comments.SingleComment(
                item['user']['login'], item['updated_at'], item['body'],
                item['html_url'], markup=markdown(
                    item['body'], extensions=[
                        'fenced_code', 'tables', 'markdown.extensions.nl2br']))

            cthread_list.append(comment)

        if reverse:
            cthread_list = list(reversed(cthread_list))

        return comments.CommentSection(cthread_list)

    def add_comment(self, body, allow_create=False, allow_hashes=True):
        """Implement as required by CommentThread.add_comment.

        :arg body:    String/text of comment to add.

        :arg allow_create=False: Whether to automatically create a new thread
                                 if a thread does not exist (usually by calling
                                 self.create_thread).

        :arg allow_hashes=True:  Whether to support hashtag mentions of other
                                 topics and automatically insert comment in
                                 body into those topics as well.

                                 *IMPORTANT*: if you recursively call
                                 add_comment to insert the hashes, you should
                                 make sure to set this to False to prevent
                                 infinite hash processing loops.

        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        :returns:     Response object indicating whether added succesfully.

        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        PURPOSE:      This uses the GitHub API to try to add the given comment
                      to the desired thread.

        """
        if self.thread_id is None:
            self.thread_id = self.lookup_thread_id()
        data = json.dumps({'body': body})
        if self.thread_id is None:
            if allow_create:
                return self.create_thread(body)
            else:
                raise ValueError(
                    'Cannot find comment existing comment for %s' % self.topic)

        result = requests.post('%s/issues/%s/comments' % (
            self.base_url, self.thread_id), data, auth=(self.user, self.token))
        if result.status_code != 201:
            if result.reason == 'Not Found' and allow_create:
                return self.create_thread(body)
            else:
                raise GitHubAngry(
                    'Bad status %s add_comment on %s because %s' % (
                        result.status_code, self.topic, result.reason))

        if allow_hashes:
            self.process_hashes(body)

        return result

    def process_hashes(self, body, allow_create=False):
        """Process any hashes mentioned and push them to related topics.

        :arg body:    Body of the comment to check for hashes and push out.

        :arg allow_create=False:  Whether to allow creating new topics
                                  from hash tag mentions.

        ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

        PURPOSE:    Look for hashtags matching self.hashtag_re and when found,
                    add comment from body to those topics.

        """
        hash_re = re.compile(self.hashtag_re)
        hashes = hash_re.findall(body)
        done = {self.topic.lower(): True}
        for mention in hashes:
            mention = mention.strip('#')
            if mention.lower() in done:
                continue  # Do not duplicate hash mentions
            new_thread = self.__class__(
                owner=self.owner, realm=self.realm, topic=mention,
                user=self.user, token=self.token)
            my_comment = '# Hashtag copy from %s:\n%s' % (self.topic, body)
            new_thread.add_comment(
                my_comment, allow_create=allow_create,
                allow_hashes=False)  # allow_hashes=False to prevent inf loop
            done[mention.lower()] = True

    def create_thread(self, body):
        data = json.dumps({'body': body, 'title': self.topic})
        result = requests.post('%s/issues' % (self.base_url),
                               data, auth=(self.user, self.token))
        if result.status_code != 201:
            raise GitHubAngry(
                'Bad status %s in create_thread on %s because %s' % (
                    result.status_code, self.topic, result.reason))

        return result

    def upload_attachment(self, location, data):
        """Upload attachment as required by CommentThread class.

        See CommentThread.upload_attachment for details.
        """
        self.validate_attachment_location(location)
        content = data.read() if hasattr(data, 'read') else data
        orig_content = content
        if isinstance(content, bytes):
            content = base64.b64encode(orig_content).decode('ascii')
        else:
            pass  # Should be base64 encoded already
        apath = '%s/%s' % (self.attachment_location, location)
        url = '%s/contents/%s' % (self.base_url, apath)
        result = requests.put(
            url, auth=(self.user, self.token), data=json.dumps({
                'message': 'file attachment %s' % location,
                'content': content}))
        if result.status_code != 201:
            raise ValueError(
                "Can't upload attachment %s due to error %s." % (
                    location, result.reason))
        return '[%s](https://github.com/%s/%s/blob/master/%s)' % (
            location, self.owner, self.realm, apath)

    @staticmethod
    def _regr_test_lookup():
        """
    NOTE: this test will hit the github web site unauthenticated. There are
          pretty tight rate limits for that so if you are re-running this
          test repeatedly, it will fail. To manually verify you can set
          user and token and re-run.

>>> user, token = None, None
>>> import tempfile, shlex, os, zipfile
>>> from eyap.core import github_comments
>>> t = github_comments.GitHubCommentThread(
...     'emin63', 'eyap', user, token, thread_id='1')
>>> i, c = t.lookup_comment_list()
>>> t.url_extras = '?per_page=1'
>>> more_i, more_c = t.lookup_comment_list()
>>> i == more_i and c == more_c
True
>>> t.url_extras = ''
        """

if __name__ == '__main__':
    doctest.testmod()
    print('Finished tests')
