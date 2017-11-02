import datetime
import unittest


class PeriodicBackupRemoverTest(unittest.TestCase):
    def setUp(self):
        from .periodic_backup_remover import PeriodicBackupRemover

        BACKUP_RULES = [
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

        self.remover = PeriodicBackupRemover()

        for rule in BACKUP_RULES:
            self.remover.add_rule(rule['upto'], rule['interval'])

    def test_rules(self):
        file_names = [
            'backup-host1.example.com-db1-20170114-060653.zip',
            'backup-host1.example.com-db1-20170115-064242.zip',
            'backup-host1.example.com-db1-20170116-072720.zip',
            'backup-host1.example.com-db1-20170116-140950.zip',
            'backup-host1.example.com-db1-20170117-144503.zip',
            'backup-host1.example.com-db1-20170118-150440.zip',
            'backup-host1.example.com-db1-20170119-152427.zip',
            'backup-host1.example.com-db1-20170120-154418.zip',
            'backup-host1.example.com-db1-20170121-160328.zip',
            'backup-host1.example.com-db1-20170122-162216.zip',
            'backup-host1.example.com-db1-20170123-164124.zip',
            'backup-host1.example.com-db1-20170124-170108.zip',
            'backup-host2.example.com-db1-20170114-060655.zip',
            'backup-host1.example.com-db2-20170201-115109.zip',
            'backup-host1.example.com-db2-20170201-205858.zip',
            'backup-host1.example.com-db1-20170122-162216.zip',
            'backup-host1.example.com-db2-20170202-171612.zip',
            'backup-host1.example.com-db2-20170202-050529.zip',
            'backup-host1.example.com-db2-20170130-055307.zip',
            'backup-host1.example.com-db2-20170131-213921.zip',
        ]

        for file_name in file_names:
            self.assertIsNotNone(self.remover.parse_backup_file_name(file_name), "File name %s cannot be parsed" % file_name)

        self.assertEqual(
            self.remover.parse_backup_file_name(file_names[0]),
            {
                'date': datetime.datetime(2017, 1, 14, 6, 6, 53),
                'db': 'db1',
                'host': 'host1.example.com',
                'file_name': file_names[0],
            }
        )

        now = datetime.datetime.now()

        self.assertFalse(
            self.remover.rule_satisfied(
            {
                'upto': (3, 'day'),
                'interval': (2, 'hour'),
            },
            [],
            now - datetime.timedelta(days=4),
            )
        )

        self.assertTrue(
            self.remover.rule_satisfied(
                {
                    'upto': (3, 'day'),
                    'interval': (2, 'hour'),
                },
                [],
                now - datetime.timedelta(days=2),
            )
        )

        self.assertTrue(
            self.remover.rule_satisfied(
                {
                    'upto': (3, 'day'),
                    'interval': (2, 'hour'),
                },
                [
                    now - datetime.timedelta(days=2, hours=3),
                ],
                now - datetime.timedelta(days=2),
            )
        )

        self.assertFalse(
            self.remover.rule_satisfied(
                {
                    'upto': (3, 'day'),
                    'interval': (2, 'hour'),
                },
                [
                    now - datetime.timedelta(days=2, hours=1),
                ],
                now - datetime.timedelta(days=2),
            )
        )

        self.assertTrue(
            self.remover.rule_satisfied(
                {
                    'upto': (3, 'day'),
                    'interval': (2, 'hour'),
                },
                [
                    now - datetime.timedelta(days=1, hours=21),
                ],
                now - datetime.timedelta(days=2),
            )
        )

        self.assertFalse(
            self.remover.rule_satisfied(
                {
                    'upto': (3, 'day'),
                    'interval': (2, 'hour'),
                },
                [
                    now - datetime.timedelta(days=1, hours=23),
                ],
                now - datetime.timedelta(days=2),
            )
        )

        self.assertTrue(
            self.remover.check_rule_interval(
                {
                    'upto': (3, 'day'),
                    'interval': (2, 'hour'),
                },
                [
                    now - datetime.timedelta(days=1, hours=21),
                    now - datetime.timedelta(days=1, hours=19),
                ],
                now - datetime.timedelta(days=2),
            )
        )
