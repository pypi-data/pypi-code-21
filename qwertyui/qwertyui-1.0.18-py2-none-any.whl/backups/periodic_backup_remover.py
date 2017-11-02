import datetime
import math
import re


class PeriodicBackupRemover:
    """
    Use this to remove backups based on intervals. For example you can have the following rules:

    backup_rules = [
        {
            'upto': (3, 'day'),
            'interval': (2, 'hour'),
        },
        {
            'upto': (1, 'month'),
            'interval': (1, 'day'),
        },
        {
            'upto': (1, 'year'),
            'interval': (1, 'week'),
        },
    ]

    This means that: backups up to 3 days are store with intervals at least 2 hours,
    backups older than 3 days but more recent than 1 month ago are stored in at least
    1 day intervals while backups older than 1 month and more recent than 1 year are
    stored in at least 1 week intervals. Backups older than 1 year will be discarded.

    And then you can initialize remover like this:

    remover = PeriodicBackupRemover()
    remover.add_rules(backup_rules)

    Remover also accepts a file name format.

    By default backups are in the format:

    backup-my.host.name-my-db-name-20170629-120000.zip

    We need both host name and db name to differentiate between various hosts and their dbs.
    Each (host, db) pair is treated as 1 group of backups to operate on.
    """

    def __init__(self,
                 backup_file_name_re=r'backup-(.*)-(\d{4})(\d{2})(\d{2})-(\d{2})(\d{2})(\d{2}).zip',
                 host_db_re=r'(.+\..+\.\w+)-(.+)'):
        self.rules = []
        self.backup_file_name_re = re.compile(backup_file_name_re)
        self.host_db_re = re.compile(host_db_re)

    @staticmethod
    def parse_date_format(num, unit):
        seconds_in_hour = 60*60
        seconds_in_day = seconds_in_hour*24

        if unit == 'hour':
            return num*seconds_in_hour
        elif unit == 'day':
            return num*seconds_in_day
        elif unit == 'week':
            return num*seconds_in_day*7
        elif unit == 'month':
            return num*seconds_in_day*30
        elif unit == 'year':
            return num*seconds_in_day*365

        raise Exception('Unknown upto unit %s' % unit)

    @staticmethod
    def rule_satisfied(rule, dates, date):
        if not PeriodicBackupRemover.check_rule_upto(rule, dates, date):
            return False

        if not PeriodicBackupRemover.check_rule_interval(rule, dates, date):
            return False

        return True

    @staticmethod
    def check_rule_upto(rule, dates, date):
        now = datetime.datetime.now()

        upto_num, upto_unit = rule['upto']
        upto_sec = PeriodicBackupRemover.parse_date_format(upto_num, upto_unit)

        diff = now - date
        if diff.total_seconds() > upto_sec:
            return False

        return True

    @staticmethod
    def check_rule_interval(rule, dates, date):
        # OK, diff in range, check if interval is satisfied
        interval_num, interval_unit = rule['interval']
        interval_sec = PeriodicBackupRemover.parse_date_format(interval_num, interval_unit)

        # Empty list
        if not dates:
            return True
        if len(dates) == 1:
            diff = dates[0] - date
            return abs(diff.total_seconds()) >= interval_sec

        dates = sorted(dates)

        # Find position in sorted dates list and check if 'date'
        # can be fitted between them
        pos = -1
        for i, d in enumerate(dates):
            if date <= d:
                pos = i
                break

        if pos > 0:
            d = dates[pos - 1]
            diff = date - d
            if abs(diff.total_seconds()) < interval_sec:
                return False

        if pos < len(dates) - 1:
            d = dates[pos]
            diff = date - d
            if abs(diff.total_seconds()) < interval_sec:
                return False

        return True

    def add_rules(self, rules):
        for rule in rules:
            if isinstance(rule, dict):
                self.add_rule(
                    rule['upto'],
                    rule['interval']
                )
            else:
                self.add_rule(
                    rule[0],
                    rule[1]
                )

    def add_rule(self, upto, interval):
        self.rules.append({
            'upto': upto,
            'interval': interval,
        })

    def parse_backup_file_name(self, file_name):
        try:
            match = self.backup_file_name_re.match(file_name).groups()
        except AttributeError:
            return

        host_db = match[0]
        host, db = self.host_db_re.match(host_db).groups()

        return {
            'date': datetime.datetime(*map(int, match[1:])),
            'db': db,
            'host': host,
            'file_name': file_name,
        }

    def keep_backup(self, kept_backups, backup):
        backup_dates = [b['date'] for b in kept_backups]

        for rule in self.rules:
            if self.rule_satisfied(rule, backup_dates, backup['date']):
                return True

        # No rule was satisfied -- don't keep the backup
        return False

    def filter_backups(self, file_names):
        backups = {}
        remove_backups = {}
        unknown_file_names = []

        for file_name in file_names:
            backup = self.parse_backup_file_name(file_name)
            if backup is None:
                unknown_file_names.append(file_name)
                continue
            key = (backup['host'], backup['db'])
            backups.setdefault(key, [])
            remove_backups.setdefault(key, [])

            if self.keep_backup(backups[key], backup):
                backups[key].append(backup)
            else:
                remove_backups[key].append(backup)

        return {
            'keep': backups,
            'remove': remove_backups,
            'unknown': unknown_file_names,
        }
