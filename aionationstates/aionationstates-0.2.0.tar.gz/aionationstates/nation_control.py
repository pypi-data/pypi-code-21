import logging
from contextlib import suppress

from aionationstates.types import Issue, IssueResult
from aionationstates.nation_ import Nation
from aionationstates.session import Session, api_query, api_command


logger = logging.getLogger('aionationstates')


class NationControl(Nation, Session):
    """Interface to the NationStates private Nation API.  Subclasses
    :any:`aionationstates.Nation`.

    Credentials are not checked upon initialization, you will only know
    if you've made a mistake after you try to make the first request.
    """
    def __init__(self, name, autologin='', password=''):
        if not password and not autologin:
            raise ValueError('No password or autologin supplied')
        self.password = password
        self.autologin = autologin
        # Weird things happen if the supplied pin doesn't follow the format
        self.pin = '0000000000'
        super().__init__(name)

    async def _base_call_api(self, method, **kwargs):
        headers = {
            'X-Password': self.password,
            'X-Autologin': self.autologin,
            'X-Pin': self.pin
        }
        resp = await super()._base_call_api(method, headers=headers, **kwargs)
        with suppress(KeyError):
            self.pin = resp.headers['X-Pin']
            logger.info(f'Updating pin for {self.id} from API header')
            self.autologin = resp.headers['X-Autologin']
            logger.info(f'Setting autologin for {self.id} from API header')
        return resp

    async def _call_web(self, path, method='GET', **kwargs):
        if not self.autologin:
            # Obtain autologin in case only password was provided
            await self._call_api({'nation': self.id, 'q': 'nextissue'})
        cookies = {
            # Will not work with unescaped equals sign
            'autologin': self.id + '%3D' + self.autologin,
            'pin': self.pin
        }
        resp = await super()._call_web(path, method=method,
                                       cookies=cookies, **kwargs)
        with suppress(KeyError):
            self.pin = resp.cookies['pin'].value
            logger.info(f'Updating pin for {self.id} from web cookie')
        return resp

    async def _call_api_command(self, data, **kwargs):
        data['nation'] = self.id
        return await self._base_call_api('POST', data=data, **kwargs)

    # End of authenticated session handling

    @api_query('issues')
    async def issues(self, root):
        """Issues the nation currently faces.

        Returns
        -------
        an :class:`ApiQuery` of a list of :class:`Issue`
        """
        return [Issue(elem, self) for elem in root.find('ISSUES')]

    def _accept_issue(self, issue_id, option_id):
        @api_command('issue', issue=str(issue_id), option=str(option_id))
        async def result(_, root):
            issue_result = IssueResult(root.find('ISSUE'))
            expand_macros = self._get_macros_expander()
            issue_result.banners = [
                await banner._expand_macros(expand_macros)
                for banner in issue_result.banners
            ]
            issue_result.headlines = [
                await expand_macros(headline)
                for headline in issue_result.headlines
            ]
            return issue_result
        return result(self)
