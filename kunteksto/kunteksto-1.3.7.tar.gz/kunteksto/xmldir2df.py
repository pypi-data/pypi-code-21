"""
EXPERIMENTAL: 3 functions from the Internet.
Build a pandas dataframe from a directory of XML files.
"""
import xml.etree.ElementTree as ET
import pandas as pd
from lxml import etree
from lxml import objectify


def xml2df(xml_data):
    root = ET.XML(xml_data) # element tree
    all_records = []
    for i, child in enumerate(root):
        record = {}
        for subchild in child:
            record[subchild.tag] = subchild.text
            all_records.append(record)
    return pd.DataFrame(all_records)


def etree2pd(xmldir):
    
    
    tree = etree.parse('Input.xml')

    data = []
    inner = {}
    for el in tree.xpath('/*/*'):
        for i in el:
            inner[i.tag] = i.text
        data.append(inner)
        inner = {}

    df = pd.DataFrame(data)
    
    return(df)

def obj2df(xmldir):
    path = 'file_path'
    xml = objectify.parse(open(path))
    root = xml.getroot()
    root.getchildren()[0].getchildren()
    df = pd.DataFrame(columns=('id', 'name'))
    
    for i in range(0,4):
        obj = root.getchildren()[i].getchildren()
        row = dict(zip(['id', 'name'], [obj[0].text, obj[1].text]))
        row_s = pd.Series(row)
        row_s.name = i
        df = df.append(row_s)
    
    
    """
    Example XML:
    
    <xml_root>

    <object>
        <id>1</id>
        <name>First</name>
    </object>

    <object>
        <id>2</id>
        <name>Second</name>
    </object>

    <object>
        <id>3</id>
        <name>Third</name>
    </object>

    <object>
        <id>4</id>
        <name>Fourth</name>
    </object>

</xml_root>

    """