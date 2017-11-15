# -*- coding: utf-8 -*-


class HTML(object):
    def __init__(self):
        """Creates a new HTML formatter."""
        pass

    def format(self, documents):
        """Formats a list of :obj:`geolink_formatter.entity.Document` instances as HTML list.

        Args:
            documents (list[geolink_formatter.entity.Document]): The list of documents to be formatted.

        Returns:
            str: An HTML formatted string containing the documents as HTML list.

        """
        return u'<ul class="geolink-formatter">{documents}</ul>'.format(
            documents=u''.join([self.__format_document__(document) for document in documents])
        )

    def __format_document__(self, document):
        """Formats a :obj:`geolink_formatter.entity.Document` instance as HTML list item.

        Args:
            document (geolink_formatter.entity.Document): The document to be formatted.

        Returns:
            str: The document formatted as HTML list item.

        """
        subtype = u' ({0})'.format(document.subtype) if document.subtype else u''
        return u'<li class="geolink-formatter-document">{type}{title} ({enactment_date}){files}</li>'.format(
            type=u'{0}{1}: '.format(document.type or u'', subtype)
            if document.type or document.subtype else u'',
            title=document.title,
            enactment_date=document.enactment_date.strftime('%d.%m.%Y'),
            files=self.__format_files__(document.files)
        )

    def __format_files__(self, files):
        """Formats a list of :obj:`geolink_formatter.entity.File` instances as HTML list.

        Args:
            files (list[geolink_formatter.entity.File]): The list of files to be formatted.

        Returns:
            str: The files formatted as HTML list.

        """
        if len(files) > 0:
            return u'<ul class="geolink-formatter">{files}</ul>'.format(
                files=u''.join([self.__format_file__(file) for file in files])
            )
        return u''

    def __format_file__(self, file):
        """Formats a :obj:`geolink_formatter.entity.File` instance as HTML list item.

        Args:
            file (geolink_formatter.entity.File): The file to be formatted.

        Returns:
            str: The file formatted as HTML list item.

        """
        return u'<li class="geolink-formatter-file"><a href="{href}" target="_blank">{title}</a></li>'.format(
            title=file.title,
            href=file.href
        )
