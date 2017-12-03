import flaskblocks.minify.exceptions
import os
import requests


less_uri = "https://minify.pelicandd.com/api/v1/less"
js_uri = "https://minify.pelicandd.com/api/v1/js"


class MinificationError(flaskblocks.minify.exceptions.MinificationError):
    def __init__(self, data):
        errors = [
            "  %s:%s:%s %s" % (e["file"], e["line"], e["column"], e["error"])
            for e
            in data["errors"]
        ]
        lines = [data["message"]] + errors
        message = "\n".join(lines)
        super(MinificationError, self).__init__(message)
        self.data = data


def minify_less_files(sources, destination, force_update=False):
    """
    Minifies LESS files to CSS and stores the result to the specified
    destination.
    """
    if force_update or _should_update(sources, destination):
        files = list(_build_files_param(sources))
        r = requests.post(less_uri, files=files)
        if not _handle_common_errors(r):
            r.raise_for_status()
        with open(destination, "w") as f:
            f.write(r.text)


def minify_less(less_code):
    """
    Minifies a LESS script to CSS and returns the resulting CSS code.
    """
    r = requests.post(less_uri, data={"source": less_code})
    if not _handle_common_errors(r):
        r.raise_for_status()
    return r.text


def minify_js_files(
        sources, destination, force_update=False, special_externs=[]):
    """
    Minifies JavaScript files and stores the result to the specified
    destination.
    """
    if force_update or _should_update(sources, destination):
        files = list(_build_files_param(sources))
        data = []
        if special_externs:
            data.append(("special-externs", special_externs))

        r = requests.post(js_uri, files=files, data=data)
        r.raise_for_status()
        with open(destination, "w") as f:
            f.write(r.text)


def _handle_common_errors(response):
    if response.status_code == 403:
        json = response.json()
        raise MinificationError(json)


def _build_files_param(sources):
    for source in sources:
        name = os.path.basename(source)
        yield ("source", (name, open(source, "rb")))


def _should_update(sources, destination):
    """
    Ensures the destination is outdated, i.e. that at least one of the sources
    was modified after the destination was effectively changed.
    """
    try:
        destination_time = os.path.getmtime(destination)
    except OSError:
        # The destination file doesn't exist.
        return True

    for source in sources:
        source_time = os.path.getmtime(source)
        if destination_time <= source_time:
            return True

    return False
