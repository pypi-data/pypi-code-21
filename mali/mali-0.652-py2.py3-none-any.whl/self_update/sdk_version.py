# coding=utf-8
import os


def get_dist(package):
    from pkg_resources import get_distribution, DistributionNotFound

    dist = get_distribution(package)

    if os.environ.get('ML_SKIP_DIST_CHECK'):
        return dist

    # Normalize case for Windows systems
    dist_loc = os.path.normcase(dist.location)
    here = os.path.normcase(__file__)

    if not here.startswith(os.path.join(dist_loc, package)):
        # not installed, but there is another version that *is*
        raise DistributionNotFound

    return dist


def get_keywords(package):
    from pkg_resources import DistributionNotFound

    try:
        dist = get_dist(package)
    except DistributionNotFound:
        return None

    parsed_pkg_info = getattr(dist, '_parsed_pkg_info', None)

    if parsed_pkg_info is None:
        return None

    return parsed_pkg_info.get('Keywords')


def get_version(package):
    from pkg_resources import DistributionNotFound

    try:
        dist = get_dist(package)
    except DistributionNotFound:
        return None

    return str(dist.version)
