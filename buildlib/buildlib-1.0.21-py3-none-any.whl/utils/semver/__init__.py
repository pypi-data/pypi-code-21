import re


def validate(semver_num: str) -> bool:
    """
    Check if version number has 'semver' format (num.num.num or num.num.num-str.num)
    """
    pattern_suffix_num = '^[0-9]+[.][0-9]+[.][0-9]+[-]\w+[.][0-9]+$'
    pattern_suffix = '^[0-9]+[.][0-9]+[.][0-9]+[-]\w+$'
    pattern_no_suffix = '^[0-9]+[.][0-9]+[.][0-9]+$'

    matches = [
        re.match(pattern, semver_num)
        for pattern
        in [pattern_no_suffix, pattern_suffix, pattern_suffix_num]
    ]

    return any(matches)


def extract_pre_release_suffix(version: str) -> str:
    """
    Get the non-numeric part of the semver num. E.g. '1.0.4-alpha.4' returns
    '-alpha'
    """
    return re.sub(r'[0-9.\s]', '', version)


def increase(
    version: str,
    type_: str
) -> str:
    """
    Increase version num based on @command:
        major: Increase num before first dot.
        minor: Increase num before second dot.
        patch: Increase num after second dot.
        pre: Increase pre num after third dot. (only when 4 dots exist in version num.)
    @version: must be of semver type. E.g.: '1.0.4' or '1.0.4-a.2' or '1.0.4-beta.1' etc.
    """
    vnum: list = re.findall(r'\d+', version)
    has_suffix: bool = True if len(vnum) > 3 else False

    if has_suffix:
        suffix_str: str = extract_pre_release_suffix(version)
        suffix_num: str = '.' + str(int(vnum[3]) + 1)
        suffix_new: str = suffix_str + '.0'

    else:
        suffix_str: str = '-alpha.'
        suffix_num: str = '.0'
        suffix_new: str = ''

    if type_ == 'major':
        return '.'.join([str(int(vnum[0]) + 1), '0', '0' + suffix_new])

    elif type_ == 'minor':
        return '.'.join([vnum[0], str(int(vnum[1]) + 1), '0' + suffix_new])

    elif type_ == 'patch':
        return '.'.join([vnum[0], vnum[1], str(int(vnum[2]) + 1) + suffix_new])

    elif type_ == 'pre':
        return '.'.join([vnum[0], vnum[1], vnum[2] + suffix_str + suffix_num])

    else:
        raise ValueError(
            'Wrong argument for parameter "command". Possible values: "major", '
            '"minor", "fix", "pre".'
        )


def convert_semver_to_wheelver(semver_num: str) -> str:
    """
    Convert a semver num to a python wheel-version num e.g.:
    1.12.1-alpha.10 -> 1.12.1a10
    """
    if not validate(semver_num):
        raise ValueError(
            'Given version number is not of semver format.'
        )

    suffix: str = extract_pre_release_suffix(semver_num)

    if suffix != '':
        wheelvernum = semver_num.replace(suffix + '.', suffix[1])

    else:
        wheelvernum = semver_num

    return wheelvernum
