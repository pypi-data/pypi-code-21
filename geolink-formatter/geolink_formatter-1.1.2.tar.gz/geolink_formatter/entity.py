# -*- coding: utf-8 -*-
import datetime


class Msg(object):

    invalid_argument = 'Invalid argument "{arg}": expected "{expected}", got "{got}"'
    """str: Message for invalid argument type."""


class Document(object):
    def __init__(self, id=None, title=None, category=None, doctype=None, files=None, enactment_date=None,
                 federal_level=None, authority=None, authority_url=None, type=None, subtype=None, cycle=None,
                 decree_date=None, instance=None):
        """Creates a new document instance.

        Args:
            id (str): The document identifier.
            title (str): The document title.
            category (str): The document category.
            doctype (str): The internal type of the document.
            files (list[geolink_formatter.entity.File]): The files contained by the document.
            enactment_date (datetime.date): The date of enactment.
            federal_level (str): The federal level of the document.
            authority (str): The name of the authority responsible for the document.
            authority_url (str): The URL of the authority's website.
            type (str): The official type of the document.
            subtype (str): The subtype of the document.
            cycle (str): The document cycle.
            decree_date (datetime.date): The date of decree.
            instance (str): The document's instance.

        Raises:
            TypeError: Raised on missing argument or invalid argument type.
            ValueError: Raised on invalid argument value.

        """

        if not isinstance(files, list):
            raise TypeError(Msg.invalid_argument.format(
                arg='files',
                expected=list,
                got=files.__class__
            ))

        if enactment_date and not isinstance(enactment_date, datetime.date):
            raise TypeError(Msg.invalid_argument.format(
                arg='enactment_date',
                expected=datetime.date,
                got=enactment_date.__class__
            ))

        if decree_date and not isinstance(decree_date, datetime.date):
            raise TypeError(Msg.invalid_argument.format(
                arg='decree_date',
                expected=datetime.date,
                got=decree_date.__class__
            ))

        self._id = id
        self._title = title
        self._category = category
        self._doctype = doctype
        self._files = files
        self._enactment_date = enactment_date
        self._federal_level = federal_level
        self._authority = authority
        self._authority_url = authority_url
        self._type = type
        self._subtype = subtype
        self._cycle = cycle
        self._decree_date = decree_date
        self._instance = instance

    @property
    def id(self):
        """str: The document identifier."""
        return self._id

    @property
    def title(self):
        """str: The document title."""
        return self._title

    @property
    def category(self):
        """str: The document category."""
        return self._category

    @property
    def doctype(self):
        """str: The internal type of the document."""
        return self._doctype

    @property
    def files(self):
        """list[geolink_formatter.entity.File]: The files contained by the document."""
        return self._files

    @property
    def enactment_date(self):
        """datetime.date: The date of enactment."""
        return self._enactment_date

    @property
    def federal_level(self):
        """str: The federal level of the document."""
        return self._federal_level

    @property
    def authority(self):
        """str: The name of the authority responsible for the document."""
        return self._authority

    @property
    def authority_url(self):
        """str: The URL of the authority's website."""
        return self._authority_url

    @property
    def type(self):
        """str: The official type of the document."""
        return self._type

    @property
    def subtype(self):
        """str: The subtype of the document."""
        return self._subtype

    @property
    def cycle(self):
        """str: The document cycle."""
        return self._cycle

    @property
    def decree_date(self):
        """datetime.date: The date of decree."""
        return self._decree_date

    @property
    def instance(self):
        """str: The document's instance."""
        return self._instance


class File(object):
    def __init__(self, title=None, href=None, category=None):
        """Creates a new file instance.

        Args:
            title (str): The file's title.
            href (str): The URL to access the file.
            category (str): The file's category.

        """

        self._title = title
        self._href = href
        self._category = category

    @property
    def title(self):
        """str: The file's title."""
        return self._title

    @property
    def href(self):
        """str: The URL to access the file."""
        return self._href

    @property
    def category(self):
        """str: The file's category."""
        return self._category
