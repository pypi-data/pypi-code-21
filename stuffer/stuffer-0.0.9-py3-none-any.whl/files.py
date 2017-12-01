"""Actions that change contents of files."""

import shutil
import urllib.request
from pathlib import Path
from typing import Optional, Union, Callable

from stuffer import content
from stuffer.content import StringArg
from stuffer.core import Action


class Chmod(Action):
    """Set permissions for a file.

    Parameters
    ----------
    permissions
        Read/write/execute permissions, expressed as a number. For readability, use Python octal numbers,
        e.g. ``0o755``.
    path
        The path to the directory or file to change permissions on.
    """

    def __init__(self, permissions: int, path: StringArg):
        self.permissions = permissions
        self.path = Path(path)
        super().__init__()

    def command(self):
        return "chmod {:o} {}".format(self.permissions, str(self.path))

    def __repr__(self):
        return "Chmod(permissions=0o{:o}, path={})".format(self.permissions, str(self.path))


class Chown(Action):
    """Set ownership for file(s).

    Parameters
    ----------
    owner
        Username that should own the file(s).
    path
        Path to directory or file to change ownership on.
    group
        Name of group to set on files.
    recursive
        If true, change files in all subdirectories.
    """

    def __init__(self, owner: StringArg, path: StringArg, group: Optional[str] = None, recursive: bool = False):
        self.owner = owner
        self.path = path
        self.group = group
        self.recursive = recursive
        super().__init__()

    def command(self):
        return "chown {} {}{} {}".format(
            "--recursive" if self.recursive else "",
            self.owner,
            "." + self.group if self.group else "",
            self.path)


class Content(Action):
    """Set the contents of a file.

    Parameters
    ----------
    path
        Path to file
    contents
        Supplier or contents, or fixed value string. In order to dynamically supply content at image build time, use
        content.OutputOf.
    make_dirs
        If True, create parent directories if necessary.
    """

    def __init__(self, path, contents, make_dirs=False):
        self.path = Path(path)
        self.contents = content.supplier(contents)
        self.make_dirs = make_dirs
        super(Content, self).__init__()

    def run(self):
        write_file_atomically(self.path, self.contents(), make_dirs=self.make_dirs)


class DownloadFile(Action):
    """Download and install a single file from a URL.

    Parameters
    ----------
    url
        URL to retrieve.
    path
        Path of destination file.
    """

    def __init__(self, url: StringArg, path: Union[Path, StringArg]):
        self.url = url
        self.path = Path(path)
        super().__init__()

    def run(self):
        local_file, _ = urllib.request.urlretrieve(self.url)
        shutil.move(local_file, str(self.path))


class Mkdir(Action):
    """Create a directory, unless it exists.

    Parameters
    ----------
    path
        Path of directory to create.
    """

    def __init__(self, path: Union[Path, StringArg]):
        self.path = Path(path)
        super().__init__()

    def command(self):
        return "mkdir -p {}".format(str(self.path))


class Transform(Action):
    """Transform the contents of a file by applying a function on the contents.

    Parameters
    ----------
    path
        Path to file whose contents should be transformed.
    transform
        Function that manipulate file contents and return the new content.
    """

    def __init__(self, path: Union[Path, StringArg], transform: Callable[[str], str]):
        self.path = Path(path)
        self.transform = transform
        super(Transform, self).__init__()

    def run(self):
        with self.path.open() as f:
            new_content = self.transform(f.read())
        write_file_atomically(self.path, new_content)


def write_file_atomically(path: Union[Path, StringArg], contents: StringArg, make_dirs: bool = False, suffix: StringArg = ".stuffer_tmp"):
    """Write contents to a file in an atomic manner.

    This routine prevents corruption in case other processes on the machine read or write the file while it is executed.
    It is overkill for Docker image building, but provides better safety when stuffer is run on live machines, e.g.
    developer machines, or when building other types of images, such as AMIs with packer.

    Parameters
    ----------
    path
        Path of destination file.
    contents
        Contents of file
    make_dirs
        If true, create parent directories if necessary.
    suffix
        Extra suffix added on temporary file.
    """
    tmp_file = path.with_suffix(path.suffix + suffix)
    if make_dirs:
        tmp_file.parent.mkdir(parents=True, exist_ok=True)
    with tmp_file.open('w') as tmp:
        tmp.write(contents)
    try:
        tmp_file.replace(path)
    except:
        if path.exists() and tmp_file.exists():
            tmp_file.unlink()
        raise
