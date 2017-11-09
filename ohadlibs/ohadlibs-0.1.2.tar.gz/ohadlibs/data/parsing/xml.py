import bs4
import os
import json
import requests


class XMLSoup:

    def __init__(self, source, **kwargs):
        self.raw = source
        if "filepath" in kwargs:
            self.filepath = kwargs['filepath']
        if "top_tag" in kwargs:
            self.top_tag = kwargs['top_tag']
        else:
            self.top_tag = None
        self.soup = self.soupify()

    def soupify(self):
        try:
            return bs4.BeautifulSoup(self.raw, 'xml').find(self.top_tag)
        except TypeError:
            return bs4.BeautifulSoup(self.raw, 'xml')

    def save_file(self):
        if self.filepath is not None:
            f = open(self.filepath, 'w')
            f.write(str(self.soup))
            f.close()
        self.raw = str(self.soup)
        self.soup = self.soupify()
        "XML {name} was saved.".format(name=str(self.filepath))

    def find_tag(self, tag):
        return self.soup.find(tag.name, tag.attrs)

    def exists(self, tag):
        return self.soup.find(tag.name, tag.attrs) is not None

    def insert(self, tag):
        self.soup.insert(len(self.soup) - 1, tag.soup())
        self.save_file()

    def remove(self, tag):
        if self.exists(tag.soup()):
            self.find_tag(tag).decompose()
        self.save_file()


class Tag:

    def __init__(self, name, **kwargs):
        self.name = name
        if 'attrs' in kwargs:
            self.attrs = kwargs['attrs']
            for attr in self.attrs:
                setattr(self, attr, self.attrs[attr])
        else:
            self.attrs = {}
        if 'innerHTML' in kwargs:
            self.inner_html = kwargs['innerHTML']
        else:
            self.inner_html = None

    def soup(self):
        return bs4.BeautifulSoup(self.__str__(), 'xml').find(self.name)

    def __str__(self):
        attrs_str = " {}".format(' '.join(['{key}="{value}"'.format(key=attr, value=self.attrs[attr]) for attr in self.attrs])) if len(self.attrs) > 0 else ""
        inner_html_str = "/" if self.inner_html is None else ">{inner_html}</{name}".format(inner_html=self.inner_html, name=self.name)
        return "<{name}{attrs}{inner_html}>".format(name=self.name, attrs=attrs_str, inner_html=inner_html_str)


if __name__ == '__main__':
    print Tag("ohad")
    print Tag("ohad", attrs={'chaet': 'yes', 'padam': 'badam'})
    print Tag("ohad", attrs={'chaet': 'yes', 'padam': 'badam'}, innerHTML="blabla")
    raw = requests.get('https://www.w3schools.com/xml/note.xml').text
    xml_path = "test.xml"
    raw = open(xml_path, 'r').read()
    xml = XMLSoup(raw, filepath=xml_path, top_tag='note')
    tag = Tag("ohad", innerHTML="blabla")
    print xml.soup
    print xml.remove(tag)
    print
    print xml.soup
