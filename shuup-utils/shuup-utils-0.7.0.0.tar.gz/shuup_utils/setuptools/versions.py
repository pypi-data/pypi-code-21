import re


def get_version_from_hgtags_file(hgtags_dir_path: str) -> str:
    with open(hgtags_dir_path + '/.hgtags', 'r') as hgtags:
        tag_last = None
        for tag in hgtags:
            tag_last = tag
        version_match = re.search('(?P<version>[0-9]\.([0-9]\.?)+)', tag_last)
        version = version_match.group('version')
    return version
