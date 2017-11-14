import re
import json
import itertools
import urlparse

from datetime import datetime

from .feed import Feed
from ..timeline import Timeline, Tag, PullRequest


class GithubFeed(Feed):
    API_ROOT_URL = 'https://api.github.com'
    UI_ROOT_URL = 'https://github.com'

    def __init__(self, project, token=None):
        self._project = project
        self._token = token
        self._timeline = Timeline(self)

    @property
    def _headers(self):
        headers = {}
        if self._token is not None:
            headers['Authorization'] = 'token {}'.format(self._token)

        return headers

    @property
    def _api_url(self):
        return '{}/repos/{}'.format(self.API_ROOT_URL, self._project)

    @property
    def project_url(self):
        return '{}/{}'.format(self.UI_ROOT_URL, self._project)

    def pull_request_url(self, number):
        return '{}/pull/{}'.format(self.project_url, number)

    def user_url(self, user):
        return '{}/{}'.format(self.UI_ROOT_URL, user)

    def release_url(self, tag):
        return '{}/releases/tag/{}'.format(self.project_url, tag)

    def compare_url(self, base, compare):
        return '{}/compare/{}...{}'.format(
            self.project_url, base, compare
        )

    def _github_request(self, url):
        response = self._request(url, self._headers)
        response_json = json.loads(response.read())
        link = response.info().getheader('Link')
        if link:
            rel = self._read_link(link)
            urls = [
                rel['next'].replace('page=2', 'page={}'.format(page))
                for page in range(2, rel['pages'] + 1)
            ]
            responses = self._github_request_in_pull(urls)
            return itertools.chain(response_json, *responses)

        return response_json

    def _github_request_in_pull(self, urls):
        responses = self._request_in_pool(urls, self._headers)
        return map(lambda response: json.loads(response.read()), responses)

    def _parse_datetime(self, date):
        return datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ')

    def _read_link(self, link):
        match = re.match(
            r'<(?P<url1>[^>]+)>; rel=\"(?P<rel1>\w+)\", '
            r'<(?P<url2>[^>]+)>; rel=\"(?P<rel2>\w+)\"',
            link
        ).groupdict()

        rels = {
            match['rel1']: match['url1'],
            match['rel2']: match['url2']
        }
        if 'last' in rels:
            rels['pages'] = int(urlparse.parse_qs(rels['last'])['page'][0])

        return rels

    def _fetch_all_tags(self, start_at=None):
        tags_url = '{}/{}'.format(self._api_url, 'git/refs/tags')
        tags_sha = [t['object']['sha'] for t in self._github_request(tags_url)]
        tag_info_urls = [
            '{}/{}'.format(self._api_url, 'git/tags/{}'.format(sha))
            for sha in tags_sha
        ]
        for tag in self._github_request_in_pull(tag_info_urls):
            at = self._parse_datetime(tag['tagger']['date'])
            if at < start_at:
                continue

            self._timeline.add(
                Tag(
                    name=tag['tag'],
                    url=self.release_url(tag['tag']),
                    at=at
                )
            )

    def _fetch_all_pull_requests(self, start_at=None):
        pull_requests_url = '{}/{}'.format(
            self._api_url, 'pulls?state=closed&per_page=10')

        for pr in self._github_request(pull_requests_url):
            if not pr.get('merged_at'):
                # closed non-merged PR
                continue

            at = self._parse_datetime(pr['merged_at'])
            if at < start_at:
                continue

            self._timeline.add(
                PullRequest(
                    number=pr['number'],
                    author=pr['user']['login'],
                    title=pr['title'],
                    url=self.pull_request_url(pr['number']),
                    at=at
                )
            )

    def fetch(self, start_at=None):
        self._fetch_all_tags(start_at)
        self._fetch_all_pull_requests(start_at)
        return self._timeline
