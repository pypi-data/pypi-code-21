from globus_cli.services.transfer import get_client as get_tc
from tests.framework.cli_testcase import default_test_config

try:
    from mock import patch
except ImportError:
    from unittest.mock import patch


def cleanup_bookmarks(tc):
    for bm in tc.bookmark_list():
        tc.delete_bookmark(bm['id'])


@patch("globus_cli.config.get_config_obj", new=default_test_config)
def main():
    tc = get_tc()
    cleanup_bookmarks(tc)


if __name__ == '__main__':
    main()
