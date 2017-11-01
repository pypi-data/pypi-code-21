import setuptools
from argparse import Namespace
from subprocess import Popen, PIPE
from re import sub

meta = Namespace(
    __name__ = "snakecharmer",
    __version__ = "0.1.dev5",
    __author__ = "Kirill Grigorev",
    __git_id__ = "LankyCyril",
    __license__ = "MIT",
)

def get_remote():
    cmd = ["git", "remote", "-v", "show", "origin"]
    git = Popen(cmd, stdout=PIPE, universal_newlines=True)
    stdout = git.communicate()[0]
    try:
        fetch = stdout.split("\n")[1]
    except IndexError:
        return ""
    raw_remote = fetch.split("Fetch URL: ")[1]
    pattern = "(://){}@".format(meta.__git_id__)
    remote = sub(pattern, r"\1", raw_remote)
    return remote

if __name__ == "__main__":
    setuptools.setup(
        name = meta.__name__,
        version = meta.__version__,
        packages = [meta.__name__],
        url = get_remote(),
        author = meta.__author__,
        license = meta.__license__,
        zip_safe = True,
        description = "Helper functions for Snakemake genomics pipelines",
        classifiers = [
            "Development Status :: 3 - Alpha",
            "Programming Language :: Python :: 3",
            "Environment :: Console",
            "License :: OSI Approved :: MIT License",
            "Intended Audience :: Developers",
            "Topic :: Software Development :: Libraries :: Application Frameworks"
        ],
        install_requires = ["pyyaml"],
        entry_points = {"console_scripts": ["snakecharmer = snakecharmer.__main__:main"]}
    )
