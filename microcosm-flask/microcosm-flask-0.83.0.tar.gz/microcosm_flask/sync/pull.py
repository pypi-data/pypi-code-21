"""
Pull resource definitions from an input source.

"""
from logging import getLogger
from sys import stdin

from requests import get
from yaml import load_all


logger = getLogger("sync.pull")


def iter_links(resource):
    """
    Iterate over links in a resource.

    """
    for relation, value in resource.get("_links", {}).items():
        if isinstance(value, list):
            for link in value:
                yield relation, link
        else:
            yield relation, value


def iter_resources(resource):
    """
    Iterate over resources in a resource.

    """
    if "items" in resource:
        # collection: embeds resources as items
        for embedded in resource.get("items"):
            href = embedded["_links"]["self"]["href"]
            logger.debug("Found embedded resource: {}".format(href))
            yield href, embedded
    else:
        # instance
        href = resource["_links"]["self"]["href"]
        logger.debug("Found resource: {}".format(href))
        yield href, resource


def sort_links(resource):
    """
    Sort resources links for easier diffs.

    """
    for relation, value in resource["_links"].items():
        if isinstance(value, list):
            resource["_links"][relation] = sorted(value, key=lambda value: value["href"])
    return resource


def pull_json(args, base_url):
    """
    Pull JSON resources by spidering a base url.

    """
    exclude_first = args.exclude_first
    stack = [base_url]

    seen = set()
    while stack:
        uri = stack.pop()

        logger.info("Fetching resource URI: {}".format(uri))
        response = get(uri)
        response.raise_for_status()
        data = response.json()

        for href, resource in iter_resources(data):
            if exclude_first:
                # skipping the first resource - if it's a discovery resource - avoids
                # pushing back state that cannot be persisted
                exclude_first = False
                continue
            sort_links(resource)
            for relation, links in iter_links(resource):
                if href not in seen and any(pattern.match(relation) for pattern in args.relation_patterns):
                    seen.add(href)
                    stack.append(href)
            yield href, resource

        for relation, link in iter_links(data):
            href = link["href"]
            # follow top-level search links and pagination next links
            if href not in seen and any(pattern.match(relation) for pattern in args.relation_patterns):
                seen.add(href)
                stack.append(href)


def pull_yaml(args, source):
    """
    Pull YAML resources from a file-like object.

    """
    for dct in load_all(source):
        for item in dct.items():
            yield item


def pull(args):
    logger.info("Pulling resources from: {}".format(args.input))

    if args.input == "-":
        for href, resource in pull_yaml(args, stdin):
            yield href, resource
    elif args.input.startswith("http"):
        for href, resource in pull_json(args, args.input):
            yield href, resource
    else:
        with open(args.input) as file_:
            for href, resource in pull_yaml(args, file_):
                yield href, resource
