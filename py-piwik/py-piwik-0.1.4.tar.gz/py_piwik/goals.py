from py_piwik.helpers import _finalize_args, _process_request
import logging

log = logging.getLogger('py_piwik/goals')


class Goals(object):

    def __init__(self, url: str, token: str):
        """
        Provides Access to the API Module Goals
        """
        self.url = url
        self.token = token

    def get_goal(self, args):
        """
        :param args: api arguments
        :type args: dict

        :return:
        """

        if 'idSite' not in args:
            raise ValueError('Missing required argument args[\'idSite\']')

        if 'idGoal' not in args:
            raise ValueError('Missing required argument args[\'idGoal\']')

        fargs = _finalize_args(args, self.token, 'Goals.getGoal')

        results = _process_request(self.url, fargs)

        return results

    def get_goals(self, args: dict) -> list:
        """
        Return list of goals for siteID

        :param args: api arguments
        :type args: dict

        :return: list of goals
        """

        if 'idSite' not in args:
            raise ValueError('Missing required argument args[\'idSite\']')

        fargs = _finalize_args(args, self.token, 'Goals.getGoals')

        results = _process_request(self.url, fargs)

        return results

    def add_goal(self, args: dict):
        """
        :param args: api arguments
        :type args: dict

        :return:
        """

        if 'idSite' not in args:
            raise ValueError('Missing required argument args[\'idSite\']')

        if 'name' not in args:
            raise ValueError('Missing required argument args[\'name\']')

        if 'matchAttribute' not in args:
            raise ValueError('Missing required argument args[\'matchAttribute\']')

        if 'pattern' not in args:
            raise ValueError('Missing required argument args[\'pattern\']')

        if 'patternType' not in args:
            raise ValueError('Missing required argument args[\'patternType\']')

        fargs = _finalize_args(args, self.token, 'Goals.addGoal')

        results = _process_request(self.url, fargs)

        return results

    def update_goal(self, args: dict):
        """
        :param args: api arguments
        :type args: dict

        :return:
        """

        if 'idSite' not in args:
            raise ValueError('Missing required argument args[\'idSite\']')

        if 'idGoal' not in args:
            raise ValueError('Missing required argument args[\'idGoal\']')

        if 'name' not in args:
            raise ValueError('Missing required argument args[\'name\']')

        if 'matchAttribute' not in args:
            raise ValueError('Missing required argument args[\'matchAttribute\']')

        if 'pattern' not in args:
            raise ValueError('Missing required argument args[\'pattern\']')

        if 'patternType' not in args:
            raise ValueError('Missing required argument args[\'patternType\']')

        fargs = _finalize_args(args, self.token, 'Goals.updateGoal')

        results = _process_request(self.url, fargs)

        return results

    def delete_goal(self, args):
        """
        :param args: api arguments
        :type args: dict

        :return:
        """

        if 'idSite' not in args:
            raise ValueError('Missing required argument args[\'idSite\']')

        if 'idGoal' not in args:
            raise ValueError('Missing required argument args[\'idGoal\']')

        fargs = _finalize_args(args, self.token, 'Goals.deleteGoal')

        results = _process_request(self.url, fargs)

        return results

    def get_item_sku(self, args):
        """
        :param args: api arguments
        :type args: dict

        :return:
        """

        if 'idSite' not in args:
            raise ValueError('Missing required argument args[\'idSite\']')
        if 'period' not in args:
            raise ValueError('Missing required argument args[\'period\']')
        if 'date' not in args:
            raise ValueError('Missing required argument args[\'date\']')

        fargs = _finalize_args(args, self.token, 'Goals.getItemsSku')

        results = _process_request(self.url, fargs)

        return results

    def get_item_name(self, args):
        """
        :param args: api arguments
        :type args: dict

        :return:
        """

        if 'idSite' not in args:
            raise ValueError('Missing required argument args[\'idSite\']')
        if 'period' not in args:
            raise ValueError('Missing required argument args[\'period\']')
        if 'date' not in args:
            raise ValueError('Missing required argument args[\'date\']')

        fargs = _finalize_args(args, self.token, 'Goals.getItemsName')

        results = _process_request(self.url, fargs)

        return results

    def get_item_category(self, args):
        """
        :param args: api arguments
        :type args: dict

        :return:
        """

        if 'idSite' not in args:
            raise ValueError('Missing required argument args[\'idSite\']')
        if 'period' not in args:
            raise ValueError('Missing required argument args[\'period\']')
        if 'date' not in args:
            raise ValueError('Missing required argument args[\'date\']')

        fargs = _finalize_args(args, self.token, 'Goals.getItemsCategory')

        results = _process_request(self.url, fargs)

        return results

    def get(self, args: dict) -> dict:
        """
        Return data related to a goal

        :param args: api arguments
        :type args: dict

        :return: goal data
        """

        if 'idSite' not in args:
            raise ValueError('Missing required argument args[\'idSite\']')
        if 'period' not in args:
            raise ValueError('Missing required argument args[\'period\']')
        if 'date' not in args:
            raise ValueError('Missing required argument args[\'date\']')

        fargs = _finalize_args(args, self.token, 'Goals.get')

        results = _process_request(self.url, fargs)

        return results

    def get_days_to_conversion(self, args):
        """
        :param args: api arguments
        :type args: dict

        :return: goal data
        """

        if 'idSite' not in args:
            raise ValueError('Missing required argument args[\'idSite\']')
        if 'period' not in args:
            raise ValueError('Missing required argument args[\'period\']')
        if 'date' not in args:
            raise ValueError('Missing required argument args[\'date\']')

        fargs = _finalize_args(args, self.token, 'Goals.getDaysToConversion')

        results = _process_request(self.url, fargs)

        return results

    def get_visits_until_conversion(self, args):
        """
                :param args: api arguments
                :type args: dict

                :return: goal data
                """

        if 'idSite' not in args:
            raise ValueError('Missing required argument args[\'idSite\']')
        if 'period' not in args:
            raise ValueError('Missing required argument args[\'period\']')
        if 'date' not in args:
            raise ValueError('Missing required argument args[\'date\']')

        fargs = _finalize_args(args, self.token, 'Goals.getVisitsUntilConversion')

        results = _process_request(self.url, fargs)

        return results
