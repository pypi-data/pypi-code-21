# coding=utf-8
from contextlib import closing
from mali_commands.legit.db import SqliteConnection
from mali_commands.legit.metadata_db import SqliteMetadataDB
from tests.base import BaseTest


class TestMetadata(BaseTest):
    db_test_path = ':memory:'

    def test_add(self):
        sha1 = 'sha1_' + self.some_random_shit()
        sha2 = 'sha2_' + self.some_random_shit()
        tree_id = 'sha2_' + self.some_random_shit()

        with closing(SqliteConnection({}, path=self.db_test_path)) as connection:
            meta = SqliteMetadataDB(connection)

            column_name = 'column_' + self.some_random_shit()

            commits_sha = []

            for i in range(5):
                commits_sha.append('commit_sha%s_%s' % (1, self.some_random_shit()))

            def add_row(index, *args):
                for item_sha in args:
                    val = 2 ** index
                    meta.add_data((item_sha, {'group': {column_name: val}}))

                meta.begin_commit(commits_sha[index], tree_id)
                meta.end_commit()

                return commits_sha[index]

            commits = []
            for i in range(5):
                if (i + 1) % 2 == 0:
                    commits.append(add_row(i, sha1))
                else:
                    commits.append(add_row(i, sha1, sha2))

            self.assertEqual(
                list(meta.get_head_data(sha1)),
                [{'@version': 5, 'group': {column_name: 16}, '@sha': sha1, '@commit_sha': commits_sha[4]}]
            )

            self.assertEqual(
                list(meta.get_head_data(sha2)),
                [{'@version': 5, 'group': {column_name: 16}, '@sha': sha2, '@commit_sha': commits_sha[4]}]
            )

            self.assertEqual(
                meta.get_data_for_commit(sha1, commits[1]),
                {'@version': 2, 'group': {column_name: 2}, '@sha': sha1, '@commit_sha': commits_sha[1]}
            )
            self.assertEqual(
                meta.get_data_for_commit(sha2, commits[1]),
                {'@version': 1, 'group': {column_name: 1}, '@sha': sha2, '@commit_sha': commits_sha[0]}
            )
