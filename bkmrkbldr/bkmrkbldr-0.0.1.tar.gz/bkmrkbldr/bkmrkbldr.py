import logging

from time import time
from jinja2 import Environment, FileSystemLoader
from os.path import join, dirname


class BookmarkBuilder(object):
    """
    This class can be used to build bookmark files in Netscape format, which can be imported into the Google Chrome
    web browser.
    """

    def __init__(self, title):
        """
        Initializes the BookmarkBuilder object.
        :param title: The title of the file that will be produced.
        """
        self.log = logging.getLogger(self.__class__.__name__)
        self.title = title

    def render(self, item = None, output_path = None):
        """
        Renders the bookmarks list to an HTML format string.
        :param item: The item to render, i.e. a potentially nested Folder or a Link.
        :return: The HTML string.
        """
        path = join(dirname(__file__), "resources")

        env = Environment(
            loader=FileSystemLoader(path)
        )
        env.filters['type'] = lambda x: x.__class__.__name__

        rendered = env.get_template("root.jnj").render({
            "BUILDER": {
                "title" : self.title,
                "item" : item
            }
        })

        if output_path:
            with open(output_path, "w") as output:
                output.write(rendered)

        return rendered


class BookmarkItem(object):
    """
    The parent class of bookmark items.
    """
    pass


class Folder(BookmarkItem):
    """
    Representation of a bookmark folder.
    """

    def __init__(self, name, date_created = None, date_modified = None):
        """
        Initializes a new Folder object with default attributes.

        :param name: The name of the folder.
        :param date_created: The date that the folder was created. Default value is now. In Unix epoch notation.
        :param date_modified: The date that the folder was last modified. Default value is now. In Unix epoch notation.
        """
        if date_created is None:
            date_created = int(time())
        if date_modified is None:
            date_modified = int(time())

        self.log = logging.getLogger(self.__class__.__name__)
        self.name = name
        self.date_modified = date_modified
        self.date_created = date_created
        self.links = []

    def add_item(self, item):
        """
        Adds a new link to the folder.
        :param item: The item to add. Should be a Folder or a Link.
        :return: None
        """
        self.log.debug("Adding item: [%s]" % str(item))
        if item:
            self.links.append(item)

    def remove_item(self, item):
        """
        Removes the given item from the Folder.
        :param item: The item to remove.
        :return: None if the item was not in the Folder. Otherwise the item is returned.
        """
        if item in self.links:
            self.links.remove(item)

            return item
        else:
            return None

    def sort(self):
        """
        Sorts the items in the folder in alphabetical order. If any of the items are folders then these will be sorted
        recursively as well.
        :return: None
        """
        self.log.debug("Sorting [%s] items." % len(self.links))

        def key(x):
            if type(x) == Folder:
                return x.name
            elif type(x) == Link:
                return x.display_name
            else:
                raise Exception("Unable to sort object.")

        self.links.sort(key=key)

        for item in self.links:
            if type(item) == Folder:
                item.sort()


class Link(BookmarkItem):
    """
    Representation of a single bookmark link.
    """

    def __init__(self, display_name, anchor, date_created = None, date_modified = None):
        """
        Constructs a new Link object.
        :param display_name: The human readable name for the bookmark.
        :param anchor: The full link to the web page that the Link represents.
        :param date_created: The date that the Link was created. Default value is now. In Unix epoch notation.
        :param date_modified: The date that the Link was last modified. Default value is now. In Unix epoch notation.
        """
        if date_created is None:
            date_created = int(time())
        if date_modified is None:
            date_modified = int(time())

        self.log = logging.getLogger(self.__class__.__name__)
        self.display_name = display_name
        self.anchor = anchor
        self.date_created = date_created
        self.date_modified = date_modified
