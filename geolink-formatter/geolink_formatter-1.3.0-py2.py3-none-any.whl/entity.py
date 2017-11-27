# -*- coding: utf-8 -*-
import datetime


class Msg(object):

    invalid_argument = 'Invalid argument "{arg}": expected "{expected}", got "{got}"'
    """str: Message for invalid argument type."""


class Document(object):
    def __init__(self, files=list(), id=None, category=None, doctype=None, federal_level=None, authority=None,
                 authority_url=None, title=None, number=None, abbreviation=None, instance=None, type=None,
                 subtype=None, decree_date=None, enactment_date=None, abrogation_date=None, cycle=None):
        """Creates a new document instance.

        Args:
            files (list[geolink_formatter.entity.File]): The files contained by the document.
            id (str): The document identifier.
            category (str): The document category.
            doctype (str): The internal type of the document.
            federal_level (str): The federal level of the document.
            authority (str): The name of the authority responsible for the document.
            authority_url (str): The URL of the authority's website.
            title (str): The document title.
            number (str): The document number.
            abbreviation (str): The document abbreviation.
            instance (str): The document's instance.
            type (str): The official type of the document.
            subtype (str): The subtype of the document.
            decree_date (datetime.date): The date of decree.
            enactment_date (datetime.date): The date of enactment.
            abrogation_date (datetime.date): The date of abrogation.
            cycle (str): The document cycle.

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

        if decree_date and not isinstance(decree_date, datetime.date):
            raise TypeError(Msg.invalid_argument.format(
                arg='decree_date',
                expected=datetime.date,
                got=decree_date.__class__
            ))

        if enactment_date and not isinstance(enactment_date, datetime.date):
            raise TypeError(Msg.invalid_argument.format(
                arg='enactment_date',
                expected=datetime.date,
                got=enactment_date.__class__
            ))

        if abrogation_date and not isinstance(abrogation_date, datetime.date):
            raise TypeError(Msg.invalid_argument.format(
                arg='decree_date',
                expected=datetime.date,
                got=decree_date.__class__
            ))

        self._files = files
        self._id = id
        self._category = category
        self._doctype = doctype
        self._federal_level = federal_level
        self._authority = authority
        self._authority_url = authority_url
        self._title = title
        self._number = number
        self._abbreviation = abbreviation
        self._instance = instance
        self._type = type
        self._subtype = subtype
        self._decree_date = decree_date
        self._enactment_date = enactment_date
        self._abrogation_date = abrogation_date
        self._cycle = cycle

    @property
    def files(self):
        """list[geolink_formatter.entity.File]: The files contained by the document."""
        return self._files

    @property
    def id(self):
        """str: The document identifier."""
        return self._id

    @property
    def category(self):
        """str: The document category."""
        return self._category

    @property
    def doctype(self):
        """str: The internal type of the document."""
        return self._doctype

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
    def title(self):
        """str: The document title."""
        return self._title

    @property
    def number(self):
        """str: The document number (since v1.1.0)."""
        return self._number

    @property
    def abbreviation(self):
        """str: The document abbreviation (since v1.1.0)."""
        return self._abbreviation

    @property
    def instance(self):
        """str: The document's instance."""
        return self._instance

    @property
    def type(self):
        """str: The official type of the document."""
        return self._type

    @property
    def subtype(self):
        """str: The subtype of the document."""
        return self._subtype

    @property
    def decree_date(self):
        """datetime.date: The date of decree."""
        return self._decree_date

    @property
    def enactment_date(self):
        """datetime.date: The date of enactment."""
        return self._enactment_date

    @property
    def abrogation_date(self):
        """datetime.date: The date of abrogation (since v1.1.0)."""
        return self._abrogation_date

    @property
    def cycle(self):
        """str: The document cycle (v1.0.0 only)."""
        return self._cycle


class File(object):
    def __init__(self, category=None, href=None, title=None):
        """Creates a new file instance.

        Args:
            category (str): The file's category.
            href (str): The URL to access the file.
            title (str): The file's title.

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
