"""
generate.py

For the data index numbers see the list of fields in analyze.py 
"""
import sys
import os
from io import StringIO, BytesIO
import time
import datetime
import csv
import sqlite3
import configparser
from urllib.parse import quote

from uuid import uuid4
from collections import OrderedDict
import json
import xmltodict
import shortuuid
import iso8601
import click

from lxml import etree
    

# RDF storage imports
try:
    from franz.openrdf.rio.rdfformat import RDFFormat
except:
    pass

# Additional namespace abbreviations
NSDEF = {}
config = configparser.ConfigParser()
config.read('kunteksto.conf')

for abbrev in config['NAMESPACES']:
    NSDEF[abbrev] = config['NAMESPACES'][abbrev].strip()


def xsd_header():
    """
    Build the header string for the XSD
    """
    hstr = ''
    hstr = '<?xml version="1.0" encoding="UTF-8"?>\n'
    hstr += '<?xml-stylesheet type="text/xsl" href="dm-description.xsl"?>\n'
    hstr += '<xs:schema\n'
    hstr += '  xmlns:vc="http://www.w3.org/2007/XMLSchema-versioning"\n'
    hstr += '  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n'
    hstr += '  xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"\n'
    hstr += '  xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"\n'
    hstr += '  xmlns:owl="http://www.w3.org/2002/07/owl#"\n'
    hstr += '  xmlns:xs="http://www.w3.org/2001/XMLSchema"\n'
    hstr += '  xmlns:xsd="http://www.w3.org/2001/XMLSchema#"\n'
    hstr += '  xmlns:dc="http://purl.org/dc/elements/1.1/"\n'
    hstr += '  xmlns:dct="http://purl.org/dc/terms/"\n'
    hstr += '  xmlns:skos="http://www.w3.org/2004/02/skos/core#"\n'
    hstr += '  xmlns:foaf="http://xmlns.com/foaf/0.1/"\n'
    hstr += '  xmlns:sioc="http://rdfs.org/sioc/ns#"\n'
    hstr += '  xmlns:sh="http://www.w3.org/ns/shacl#"\n'
    hstr += '  xmlns:s3m="https://www.s3model.com/ns/s3m/"\n'
    for abbrev in NSDEF.keys():
        hstr += '  xmlns:' + abbrev + '="' + NSDEF[abbrev] + '"\n'
        
    hstr += '  targetNamespace="https://www.s3model.com/ns/s3m/"\n'
    hstr += '  xml:lang="en-US">\n\n'
    hstr += '  <xs:include schemaLocation="https://www.s3model.com/ns/s3m/s3model_3_0_0.xsd"/>\n\n'
    return(hstr)


def xsd_metadata(md):
    """
    Create the metadata for the S3Model data model.
    """
    
    mds = '<!-- Metadata -->\n  <xs:annotation><xs:appinfo><rdf:RDF><rdfs:Class\n'
    mds += '    rdf:about="dm-' + md[0] + '">\n'
    mds += '    <dc:title>' + md[1].strip() + '</dc:title>\n'
    mds += '    <dc:creator>' + md[2] + '</dc:creator>\n'
    mds += '    <dc:contributor></dc:contributor>\n'
    mds += '    <dc:subject>S3M</dc:subject>\n'
    mds += '    <dc:rights>' + md[4] + '</dc:rights>\n'
    mds += '    <dc:relation>None</dc:relation>\n'
    mds += '    <dc:coverage>Global</dc:coverage>\n'
    mds += '    <dc:type>S3M Data Model</dc:type>\n'
    mds += '    <dc:identifier>' + md[0].replace('dm-', '') + '</dc:identifier>\n'
    mds += '    <dc:description>' + md[3] + '</dc:description>\n'
    mds += '    <dc:publisher>Data Insights, Inc. via Kunteksto</dc:publisher>\n'
    mds += '    <dc:date>' + datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S") + \
        '</dc:date>\n'
    mds += '    <dc:format>text/xml</dc:format>\n'
    mds += '    <dc:language>en-US</dc:language>\n'
    mds += '    <rdfs:subClassOf rdf:resource="https://www.s3model.com/ns/s3m/s3model/DM"/>\n'
    mds += '  </rdfs:Class></rdf:RDF></xs:appinfo></xs:annotation>\n\n'
    return(mds)


def xdcount_rdf(data):
    """
    Create RDF including SHACL constraints for xdCount model.
    """
    mcID = data[15].strip()    
    rdfStr = ''
    indent = 2
    padding = ('').rjust(indent)
    rdfStr += padding.rjust(indent + 6) + '<rdfs:Class rdf:about="mc-' + mcID + '">\n'
    rdfStr += padding.rjust(indent + 8) + '<rdfs:subClassOf rdf:resource="https://www.s3model.com/ns/s3m/s3model_3_0_0.xsd#XdCountType"/>\n'
    rdfStr += padding.rjust(indent + 8) + '<rdfs:subClassOf rdf:resource="https://www.s3model.com/ns/s3m/s3model/RMC"/>\n'
    rdfStr += padding.rjust(indent + 8) + '<rdfs:isDefinedBy rdf:resource="' + quote(data[10].strip()) + '"/>\n'
    if data[11]:  # are there additional predicate-object definitions?
        for po in data[11].splitlines():
            pred = po.split()[0]
            obj = po[len(pred):].strip()
            rdfStr += padding.rjust(indent + 8) + '<' + pred.strip() + ' rdf:resource="' + quote(obj.strip()) + '"/>\n'
            
    rdfStr += padding.rjust(indent + 6) +'<sh:property>\n'
    rdfStr += padding.rjust(indent + 8) +'<rdf:Description>\n'
    rdfStr += padding.rjust(indent + 8) +'<sh:path rdf:resource="mc-' + mcID + '/xdcount-value"/>\n'
    rdfStr += padding.rjust(indent + 8) +'<sh:datatype rdf:resource="http://www.w3.org/2001/XMLSchema#int"/>\n'
    rdfStr += padding.rjust(indent + 10) +'<sh:maxCount rdf:datatype="http://www.w3.org/2001/XMLSchema#integer">1</sh:maxCount>\n'
    rdfStr += padding.rjust(indent + 10) +'<sh:minCount rdf:datatype="http://www.w3.org/2001/XMLSchema#integer">1</sh:minCount>\n'
    
    if data[7]:
        rdfStr += padding.rjust(indent + 10) +'<sh:minInclusive rdf:datatype="http://www.w3.org/2001/XMLSchema#integer">' + data[7].strip() + '</sh:minInclusive>\n'
    elif data[17]:
        rdfStr += padding.rjust(indent + 10) +'<sh:minExclusive rdf:datatype="http://www.w3.org/2001/XMLSchema#integer">' + data[17].strip() + '</sh:minExclusive>\n'
    if data[8]:
        rdfStr += padding.rjust(indent + 10) +'<sh:maxInclusive rdf:datatype="http://www.w3.org/2001/XMLSchema#integer">' + data[8].strip() + '</sh:maxInclusive>\n'    
    elif data[18]:
        rdfStr += padding.rjust(indent + 10) +'<sh:maxExclusive rdf:datatype="http://www.w3.org/2001/XMLSchema#integer">' + data[18].strip() + '</sh:maxExclusive>\n'    
    rdfStr += padding.rjust(indent + 8) +'</rdf:Description>\n'
    rdfStr += padding.rjust(indent + 6) +'</sh:property>\n'
    
    rdfStr += padding.rjust(indent + 6) + '</rdfs:Class>\n'
    return(rdfStr)


def xdcount(data):
    """
    Create xdCount model used for integers.
    """
    
    adapterID = data[16].strip()
    mcID = data[15].strip()
    unitsID = str(uuid4())
    indent = 2
    padding = ('').rjust(indent)
   
    # Adapter
    xdstr = padding.rjust(indent) + '\n<xs:element name="ms-' + adapterID + '" substitutionGroup="s3m:Items" type="s3m:mc-' + adapterID + '"/>\n'
    xdstr += padding.rjust(indent) + '<xs:complexType name="mc-' + adapterID + '">\n'
    xdstr += padding.rjust(indent + 2) + '<xs:complexContent>\n'
    xdstr += padding.rjust(indent + 4) + '<xs:restriction base="s3m:XdAdapterType">\n'
    xdstr += padding.rjust(indent + 6) + '<xs:sequence>\n'
    xdstr += padding.rjust(indent + 8) + '<xs:element maxOccurs="unbounded" minOccurs="0" ref="s3m:ms-' + mcID + '"/>\n'
    xdstr += padding.rjust(indent + 6) + '</xs:sequence>\n'
    xdstr += padding.rjust(indent + 4) + '</xs:restriction>\n'
    xdstr += padding.rjust(indent + 2) + '</xs:complexContent>\n'
    xdstr += padding.rjust(indent) + '</xs:complexType>\n'
    # model component
    xdstr += padding.rjust(indent) + '<xs:element name="ms-' + mcID + '" substitutionGroup="s3m:XdAdapter-value" type="s3m:mc-' + mcID + '"/>\n'
    xdstr += padding.rjust(indent) + '<xs:complexType name="mc-' + mcID + '">\n'
    xdstr += padding.rjust(indent + 2) + '<xs:annotation>\n'
    xdstr += padding.rjust(indent + 4) + '<xs:documentation>\n'
    xdstr += padding.rjust(indent + 6) + data[9].strip() + '\n'
    xdstr += padding.rjust(indent + 4) + '</xs:documentation>\n'
    xdstr += padding.rjust(indent + 4) + '<xs:appinfo>\n'   
    # add the RDF
    xdstr += xdcount_rdf(data)
    xdstr += padding.rjust(indent + 4) + '</xs:appinfo>\n'
    xdstr += padding.rjust(indent + 2) + '</xs:annotation>\n'
    xdstr += padding.rjust(indent + 2) + '<xs:complexContent>\n'
    xdstr += padding.rjust(indent + 4) + '<xs:restriction base="s3m:XdCountType">\n'
    xdstr += padding.rjust(indent + 6) + '<xs:sequence>\n'
    xdstr += padding.rjust(indent + 8) + '<xs:element maxOccurs="1" minOccurs="1" name="label" type="xs:string" fixed="' + data[1].strip() + '"/>\n'
    xdstr += padding.rjust(indent + 8) + '<xs:element maxOccurs="1" minOccurs="0" ref="s3m:ExceptionalValue"/>\n'
    xdstr += padding.rjust(indent + 8) + '<xs:element maxOccurs="1" minOccurs="0" name="vtb" type="xs:dateTime"/>\n'
    xdstr += padding.rjust(indent + 8) + '<xs:element maxOccurs="1" minOccurs="0" name="vte" type="xs:dateTime"/>\n'
    xdstr += padding.rjust(indent + 8) + '<xs:element maxOccurs="1" minOccurs="0" name="tr" type="xs:dateTime"/>\n'
    xdstr += padding.rjust(indent + 8) + '<xs:element maxOccurs="1" minOccurs="0" name="modified" type="xs:dateTime"/>\n'
    xdstr += padding.rjust(indent + 8) + '<xs:element maxOccurs="1" minOccurs="0" name="magnitude-status" type="s3m:MagnitudeStatus"/>\n'
    xdstr += padding.rjust(indent + 8) + '<xs:element maxOccurs="1" minOccurs="1" name="error"  type="xs:int" default="0"/>\n'
    xdstr += padding.rjust(indent + 8) + '<xs:element maxOccurs="1" minOccurs="1" name="accuracy" type="xs:int" default="0"/>\n'
    if not data[7] and not data[8] and not data[17] and not data [18] and not data[13]:
        xdstr += padding.rjust(indent + 8) + '<xs:element maxOccurs="1" minOccurs="1"  name="xdcount-value" type="xs:int"/>\n'
    if data[13]:
        xdstr += padding.rjust(indent + 8) +  '<xs:element maxOccurs="1" minOccurs="1"  name="xdcount-value" type="xs:int" default="' + str(int(data[13])) + '"/>\n'       
    else:
        xdstr += padding.rjust(indent + 8) + '<xs:element maxOccurs="1" minOccurs="1"  name="xdcount-value">\n'
        xdstr += padding.rjust(indent + 10) + '<xs:simpleType>\n'
        xdstr += padding.rjust(indent + 10) + '<xs:restriction base="xs:int">\n'
        if data[7]:
            xdstr += padding.rjust(indent + 12) + '<xs:minInclusive value="' + str(int(data[7])) + '"/>\n'
        elif data[17]:
            xdstr += padding.rjust(indent + 12) + '<xs:minExclusive value="' + str(int(data[17])) + '"/>\n'
            
        if data[8]:
            xdstr += padding.rjust(indent + 12) + '<xs:maxInclusive value="' + str(int(data[8])) + '"/>\n'
        elif data[18]:
            xdstr += padding.rjust(indent + 12) + '<xs:maxExclusive value="' + str(int(data[18])) + '"/>\n'
            
        xdstr += padding.rjust(indent + 10) + '</xs:restriction>\n'
        xdstr += padding.rjust(indent + 10) + '</xs:simpleType>\n'
        xdstr += padding.rjust(indent + 8) + '</xs:element>\n'
    xdstr += padding.rjust(indent + 8) + '<xs:element maxOccurs="1" minOccurs="1" name="xdcount-units" type="s3m:mc-' + unitsID + '"/>\n'
    xdstr += padding.rjust(indent + 6) + '</xs:sequence>\n'
    xdstr += padding.rjust(indent + 4) + '</xs:restriction>\n'
    xdstr += padding.rjust(indent + 2) + '</xs:complexContent>\n'
    xdstr += padding.rjust(indent) + '</xs:complexType>\n'

    xdstr += units(unitsID, data)

    return(xdstr)


def xdquantity_rdf(data):
    """
    Create RDF including SHACL constraints for xdQuantity model.
    """
    mcID = data[15].strip()    
    rdfStr = ''
    indent = 2
    padding = ('').rjust(indent)
    rdfStr += padding.rjust(indent + 6) + '<rdfs:Class rdf:about="mc-' + mcID + '">\n'
    rdfStr += padding.rjust(indent + 8) + '<rdfs:subClassOf rdf:resource="https://www.s3model.com/ns/s3m/s3model_3_0_0.xsd#XdQuantityType"/>\n'
    rdfStr += padding.rjust(indent + 8) + '<rdfs:subClassOf rdf:resource="https://www.s3model.com/ns/s3m/s3model/RMC"/>\n'
    rdfStr += padding.rjust(indent + 8) + '<rdfs:isDefinedBy rdf:resource="' + quote(data[10].strip()) + '"/>\n'
    if data[11]:  # are there additional predicate-object definitions?
        for po in data[11].splitlines():
            pred = po.split()[0]
            obj = po[len(pred):].strip()
            rdfStr += padding.rjust(indent + 8) + '<' + pred.strip() + ' rdf:resource="' + quote(obj.strip()) + '"/>\n'
            
    rdfStr += padding.rjust(indent + 6) +'<sh:property>\n'
    rdfStr += padding.rjust(indent + 8) +'<rdf:Description>\n'
    rdfStr += padding.rjust(indent + 8) +'<sh:path rdf:resource="mc-' + mcID + '/xdquantity-value"/>\n'
    rdfStr += padding.rjust(indent + 8) +'<sh:datatype rdf:resource="http://www.w3.org/2001/XMLSchema#decimal"/>\n'
    rdfStr += padding.rjust(indent + 10) +'<sh:maxCount rdf:datatype="http://www.w3.org/2001/XMLSchema#integer">1</sh:maxCount>\n'
    rdfStr += padding.rjust(indent + 10) +'<sh:minCount rdf:datatype="http://www.w3.org/2001/XMLSchema#integer">1</sh:minCount>\n'
    
    if data[7]:
        rdfStr += padding.rjust(indent + 10) +'<sh:minInclusive rdf:datatype="http://www.w3.org/2001/XMLSchema#decimal">' + data[7].strip() + '</sh:minInclusive>\n'
    elif data[17]:
        rdfStr += padding.rjust(indent + 10) +'<sh:minExclusive rdf:datatype="http://www.w3.org/2001/XMLSchema#decimal">' + data[17].strip() + '</sh:minExclusive>\n'
        
    if data[8]:
        rdfStr += padding.rjust(indent + 10) +'<sh:maxInclusive rdf:datatype="http://www.w3.org/2001/XMLSchema#decimal">' + data[8].strip() + '</sh:maxInclusive>\n'    
    elif data[18]:
        rdfStr += padding.rjust(indent + 10) +'<sh:maxExclusive rdf:datatype="http://www.w3.org/2001/XMLSchema#decimal">' + data[18].strip() + '</sh:maxExclusive>\n'    
   
    rdfStr += padding.rjust(indent + 8) +'</rdf:Description>\n'
    rdfStr += padding.rjust(indent + 6) +'</sh:property>\n'
    
    rdfStr += padding.rjust(indent + 6) + '</rdfs:Class>\n'
    return(rdfStr)


def xdquantity(data):
    """
    Create xdQuantity model used for decimals.
    """
    
    adapterID = data[16].strip()
    mcID = data[15].strip()
    unitsID = str(uuid4())
    indent = 2
    padding = ('').rjust(indent)
    
    # Adapter
    xdstr = padding.rjust(indent) + '\n<xs:element name="ms-' + adapterID + '" substitutionGroup="s3m:Items" type="s3m:mc-' + adapterID + '"/>\n'
    xdstr += padding.rjust(indent) + '<xs:complexType name="mc-' + adapterID + '">\n'
    xdstr += padding.rjust(indent + 2) + '<xs:complexContent>\n'
    xdstr += padding.rjust(indent + 4) + '<xs:restriction base="s3m:XdAdapterType">\n'
    xdstr += padding.rjust(indent + 6) + '<xs:sequence>\n'
    xdstr += padding.rjust(indent + 8) + '<xs:element maxOccurs="unbounded" minOccurs="0" ref="s3m:ms-' + mcID + '"/>\n'
    xdstr += padding.rjust(indent + 6) + '</xs:sequence>\n'
    xdstr += padding.rjust(indent + 4) + '</xs:restriction>\n'
    xdstr += padding.rjust(indent + 2) + '</xs:complexContent>\n'
    xdstr += padding.rjust(indent) + '</xs:complexType>\n'
    # model component
    xdstr += padding.rjust(indent) + '<xs:element name="ms-' + mcID + '" substitutionGroup="s3m:XdAdapter-value" type="s3m:mc-' + mcID + '"/>\n'
    xdstr += padding.rjust(indent) + '<xs:complexType name="mc-' + mcID + '">\n'
    xdstr += padding.rjust(indent + 2) + '<xs:annotation>\n'
    xdstr += padding.rjust(indent + 4) + '<xs:documentation>\n'
    xdstr += padding.rjust(indent + 6) + data[9].strip() + '\n'
    xdstr += padding.rjust(indent + 4) + '</xs:documentation>\n'
    xdstr += padding.rjust(indent + 4) + '<xs:appinfo>\n'
    # add the RDF
    xdstr += xdquantity_rdf(data)
    xdstr += padding.rjust(indent + 4) + '</xs:appinfo>\n'
    xdstr += padding.rjust(indent + 2) + '</xs:annotation>\n'
    xdstr += padding.rjust(indent + 2) + '<xs:complexContent>\n'
    xdstr += padding.rjust(indent + 4) + '<xs:restriction base="s3m:XdQuantityType">\n'
    xdstr += padding.rjust(indent + 6) + '<xs:sequence>\n'
    xdstr += padding.rjust(indent + 8) + '<xs:element maxOccurs="1" minOccurs="1" name="label" type="xs:string" fixed="' + data[1].strip() + '"/>\n'
    xdstr += padding.rjust(indent + 8) + '<xs:element maxOccurs="1" minOccurs="0" ref="s3m:ExceptionalValue"/>\n'
    xdstr += padding.rjust(indent + 8) + '<xs:element maxOccurs="1" minOccurs="0" name="vtb" type="xs:dateTime"/>\n'
    xdstr += padding.rjust(indent + 8) + '<xs:element maxOccurs="1" minOccurs="0" name="vte" type="xs:dateTime"/>\n'
    xdstr += padding.rjust(indent + 8) + '<xs:element maxOccurs="1" minOccurs="0" name="tr" type="xs:dateTime"/>\n'
    xdstr += padding.rjust(indent + 8) + '<xs:element maxOccurs="1" minOccurs="0" name="modified" type="xs:dateTime"/>\n'
    xdstr += padding.rjust(indent + 8) + '<xs:element maxOccurs="1" minOccurs="0" name="magnitude-status" type="s3m:MagnitudeStatus"/>\n'
    xdstr += padding.rjust(indent + 8) + '<xs:element maxOccurs="1" minOccurs="1" name="error"  type="xs:int" default="0"/>\n'
    xdstr += padding.rjust(indent + 8) + '<xs:element maxOccurs="1" minOccurs="1" name="accuracy" type="xs:int" default="0"/>\n'
    if not data[7] and not data[8] and not data[17] and not data[18] and not data[13]:
        xdstr += padding.rjust(indent + 8) + '<xs:element maxOccurs="1" minOccurs="1"  name="xdquantity-value" type="xs:decimal"/>\n'
    if data[13]:
        xdstr += padding.rjust(indent + 8) + '<xs:element maxOccurs="1" minOccurs="1"  name="xdquantity-value" type="xs:decimal" default="' + data[13].strip() + '"/>\n'
    else:
        xdstr += padding.rjust(indent + 8) + '<xs:element maxOccurs="1" minOccurs="1"  name="xdquantity-value">\n'
        xdstr += padding.rjust(indent + 10) + '<xs:simpleType>\n'
        xdstr += padding.rjust(indent + 10) + '<xs:restriction base="xs:decimal">\n'
        if data[7]:
            xdstr += padding.rjust(indent + 12) + '<xs:minInclusive value="' + data[7].strip() + '"/>\n'
        elif data[17]:
            xdstr += padding.rjust(indent + 12) + '<xs:minExclusive value="' + data[17].strip() + '"/>\n'
        if data[8]:
            xdstr += padding.rjust(indent + 12) + '<xs:maxInclusive value="' + data[8].strip() + '"/>\n'
        elif data[18]:
            xdstr += padding.rjust(indent + 12) + '<xs:maxExclusive value="' + data[18].strip() + '"/>\n'
                
        xdstr += padding.rjust(indent + 10) + '</xs:restriction>\n'
        xdstr += padding.rjust(indent + 10) + '</xs:simpleType>\n'
        xdstr += padding.rjust(indent + 8) + '</xs:element>\n'
    xdstr += padding.rjust(indent + 8) +     '<xs:element maxOccurs="1" minOccurs="1" name="xdquantity-units" type="s3m:mc-' + unitsID + '"/>\n'
    xdstr += padding.rjust(indent + 6) + '</xs:sequence>\n'
    xdstr += padding.rjust(indent + 4) + '</xs:restriction>\n'
    xdstr += padding.rjust(indent + 2) + '</xs:complexContent>\n'
    xdstr += padding.rjust(indent) + '</xs:complexType>\n'

    xdstr += units(unitsID, data)

    return(xdstr)


def xdfloat_rdf(data):
    """
    Create RDF including SHACL constraints for xdFloat model.
    """
    mcID = data[15].strip()    
    rdfStr = ''
    indent = 2
    padding = ('').rjust(indent)
    rdfStr += padding.rjust(indent + 6) + '<rdfs:Class rdf:about="mc-' + mcID + '">\n'
    rdfStr += padding.rjust(indent + 8) + '<rdfs:subClassOf rdf:resource="https://www.s3model.com/ns/s3m/s3model_3_0_0.xsd#XdFloatType"/>\n'
    rdfStr += padding.rjust(indent + 8) + '<rdfs:subClassOf rdf:resource="https://www.s3model.com/ns/s3m/s3model/RMC"/>\n'
    rdfStr += padding.rjust(indent + 8) + '<rdfs:isDefinedBy rdf:resource="' + quote(data[10].strip()) + '"/>\n'
    if data[11]:  # are there additional predicate-object definitions?
        for po in data[11].splitlines():
            pred = po.split()[0]
            obj = po[len(pred):].strip()
            rdfStr += padding.rjust(indent + 8) + '<' + pred.strip() + ' rdf:resource="' + quote(obj.strip()) + '"/>\n'
            
    rdfStr += padding.rjust(indent + 6) +'<sh:property>\n'
    rdfStr += padding.rjust(indent + 8) +'<rdf:Description>\n'
    rdfStr += padding.rjust(indent + 8) +'<sh:path rdf:resource="mc-' + mcID + '/xdfloat-value"/>\n'
    rdfStr += padding.rjust(indent + 8) +'<sh:datatype rdf:resource="http://www.w3.org/2001/XMLSchema#float"/>\n'
    rdfStr += padding.rjust(indent + 10) +'<sh:maxCount rdf:datatype="http://www.w3.org/2001/XMLSchema#integer">1</sh:maxCount>\n'
    rdfStr += padding.rjust(indent + 10) +'<sh:minCount rdf:datatype="http://www.w3.org/2001/XMLSchema#integer">1</sh:minCount>\n'
    
    if data[7]:
        rdfStr += padding.rjust(indent + 10) +'<sh:minInclusive rdf:datatype="http://www.w3.org/2001/XMLSchema#float">' + data[7].strip() + '</sh:minInclusive>\n'
    elif data[17]:
        rdfStr += padding.rjust(indent + 10) +'<sh:minExclusive rdf:datatype="http://www.w3.org/2001/XMLSchema#float">' + data[17].strip() + '</sh:minExclusive>\n'
        
    if data[8]:
        rdfStr += padding.rjust(indent + 10) +'<sh:maxInclusive rdf:datatype="http://www.w3.org/2001/XMLSchema#float">' + data[8].strip() + '</sh:maxInclusive>\n'    
    elif data[18]:
        rdfStr += padding.rjust(indent + 10) +'<sh:maxExclusive rdf:datatype="http://www.w3.org/2001/XMLSchema#float">' + data[18].strip() + '</sh:maxExclusive>\n'    
   
    rdfStr += padding.rjust(indent + 8) +'</rdf:Description>\n'
    rdfStr += padding.rjust(indent + 6) +'</sh:property>\n'
    
    rdfStr += padding.rjust(indent + 6) + '</rdfs:Class>\n'
    return(rdfStr)


def xdfloat(data):
    """
    Create xdFloat model used for floats.
    """
    
    adapterID = data[16].strip()
    mcID = data[15].strip()
    unitsID = str(uuid4())
    indent = 2
    padding = ('').rjust(indent)
    
    # Adapter
    xdstr = padding.rjust(indent) + '\n<xs:element name="ms-' + adapterID + '" substitutionGroup="s3m:Items" type="s3m:mc-' + adapterID + '"/>\n'
    xdstr += padding.rjust(indent) + '<xs:complexType name="mc-' + adapterID + '">\n'
    xdstr += padding.rjust(indent + 2) + '<xs:complexContent>\n'
    xdstr += padding.rjust(indent + 4) + '<xs:restriction base="s3m:XdAdapterType">\n'
    xdstr += padding.rjust(indent + 6) + '<xs:sequence>\n'
    xdstr += padding.rjust(indent + 8) + '<xs:element maxOccurs="unbounded" minOccurs="0" ref="s3m:ms-' + mcID + '"/>\n'
    xdstr += padding.rjust(indent + 6) + '</xs:sequence>\n'
    xdstr += padding.rjust(indent + 4) + '</xs:restriction>\n'
    xdstr += padding.rjust(indent + 2) + '</xs:complexContent>\n'
    xdstr += padding.rjust(indent) + '</xs:complexType>\n'
    # model component
    xdstr += padding.rjust(indent) + '<xs:element name="ms-' + mcID + '" substitutionGroup="s3m:XdAdapter-value" type="s3m:mc-' + mcID + '"/>\n'
    xdstr += padding.rjust(indent) + '<xs:complexType name="mc-' + mcID + '">\n'
    xdstr += padding.rjust(indent + 2) + '<xs:annotation>\n'
    xdstr += padding.rjust(indent + 4) + '<xs:documentation>\n'
    xdstr += padding.rjust(indent + 6) + data[9].strip() + '\n'
    xdstr += padding.rjust(indent + 4) + '</xs:documentation>\n'
    xdstr += padding.rjust(indent + 4) + '<xs:appinfo>\n'
    # add the RDF
    xdstr += xdquantity_rdf(data)
    xdstr += padding.rjust(indent + 4) + '</xs:appinfo>\n'
    xdstr += padding.rjust(indent + 2) + '</xs:annotation>\n'
    xdstr += padding.rjust(indent + 2) + '<xs:complexContent>\n'
    xdstr += padding.rjust(indent + 4) + '<xs:restriction base="s3m:XdFloatType">\n'
    xdstr += padding.rjust(indent + 6) + '<xs:sequence>\n'
    xdstr += padding.rjust(indent + 8) + '<xs:element maxOccurs="1" minOccurs="1" name="label" type="xs:string" fixed="' + data[1].strip() + '"/>\n'
    xdstr += padding.rjust(indent + 8) + '<xs:element maxOccurs="1" minOccurs="0" ref="s3m:ExceptionalValue"/>\n'
    xdstr += padding.rjust(indent + 8) + '<xs:element maxOccurs="1" minOccurs="0" name="vtb" type="xs:dateTime"/>\n'
    xdstr += padding.rjust(indent + 8) + '<xs:element maxOccurs="1" minOccurs="0" name="vte" type="xs:dateTime"/>\n'
    xdstr += padding.rjust(indent + 8) + '<xs:element maxOccurs="1" minOccurs="0" name="tr" type="xs:dateTime"/>\n'
    xdstr += padding.rjust(indent + 8) + '<xs:element maxOccurs="1" minOccurs="0" name="modified" type="xs:dateTime"/>\n'
    xdstr += padding.rjust(indent + 8) + '<xs:element maxOccurs="1" minOccurs="0" name="magnitude-status" type="s3m:MagnitudeStatus"/>\n'
    xdstr += padding.rjust(indent + 8) + '<xs:element maxOccurs="1" minOccurs="1" name="error"  type="xs:int" default="0"/>\n'
    xdstr += padding.rjust(indent + 8) + '<xs:element maxOccurs="1" minOccurs="1" name="accuracy" type="xs:int" default="0"/>\n'
    if not data[7] and not data[8] and not data[17] and not data[18] and not data[13]:
        xdstr += padding.rjust(indent + 8) + '<xs:element maxOccurs="1" minOccurs="1"  name="xdfloat-value" type="xs:float"/>\n'
    if data[13]:
        xdstr += padding.rjust(indent + 8) + '<xs:element maxOccurs="1" minOccurs="1"  name="xdfloat-value" type="xs:float" default="' + data[13].strip() + '"/>\n'
    else:
        xdstr += padding.rjust(indent + 8) + '<xs:element maxOccurs="1" minOccurs="1"  name="xdfloat-value">\n'
        xdstr += padding.rjust(indent + 10) + '<xs:simpleType>\n'
        xdstr += padding.rjust(indent + 10) + '<xs:restriction base="xs:float">\n'
        if data[7]:
            xdstr += padding.rjust(indent + 12) + '<xs:minInclusive value="' + data[7].strip() + '"/>\n'
        elif data[17]:
            xdstr += padding.rjust(indent + 12) + '<xs:minExclusive value="' + data[17].strip() + '"/>\n'
        if data[8]:
            xdstr += padding.rjust(indent + 12) + '<xs:maxInclusive value="' + data[8].strip() + '"/>\n'
        elif data[18]:
            xdstr += padding.rjust(indent + 12) + '<xs:maxExclusive value="' + data[18].strip() + '"/>\n'
                
        xdstr += padding.rjust(indent + 10) + '</xs:restriction>\n'
        xdstr += padding.rjust(indent + 10) + '</xs:simpleType>\n'
        xdstr += padding.rjust(indent + 8) + '</xs:element>\n'
    xdstr += padding.rjust(indent + 8) +     '<xs:element maxOccurs="1" minOccurs="0" name="xdfloat-units" type="s3m:mc-' + unitsID + '"/>\n'
    xdstr += padding.rjust(indent + 6) + '</xs:sequence>\n'
    xdstr += padding.rjust(indent + 4) + '</xs:restriction>\n'
    xdstr += padding.rjust(indent + 2) + '</xs:complexContent>\n'
    xdstr += padding.rjust(indent) + '</xs:complexType>\n'

    xdstr += units(unitsID, data)

    return(xdstr)


def xdstring_rdf(data):
    """
    Create RDF including SHACL constraints for xdString model.
    """
    mcID = data[15].strip()    
    rdfStr = ''
    indent = 2
    padding = ('').rjust(indent)
    rdfStr += padding.rjust(indent + 6) + '<rdfs:Class rdf:about="mc-' + mcID + '">\n'
    rdfStr += padding.rjust(indent + 8) + '<rdfs:subClassOf rdf:resource="https://www.s3model.com/ns/s3m/s3model_3_0_0.xsd#XdStringType"/>\n'
    rdfStr += padding.rjust(indent + 8) + '<rdfs:subClassOf rdf:resource="https://www.s3model.com/ns/s3m/s3model/RMC"/>\n'
    rdfStr += padding.rjust(indent + 8) + '<rdfs:isDefinedBy rdf:resource="' + quote(data[10].strip()) + '"/>\n'
    if data[11]:  # are there additional predicate-object definitions?
        for po in data[11].splitlines():
            pred = po.split()[0]
            obj = po[len(pred):].strip()
            rdfStr += padding.rjust(indent + 8) + '<' + pred.strip() + ' rdf:resource="' + quote(obj.strip()) + '"/>\n'
            
    rdfStr += padding.rjust(indent + 6) +'<sh:property>\n'
    rdfStr += padding.rjust(indent + 8) +'<rdf:Description>\n'
    rdfStr += padding.rjust(indent + 10) +'<sh:path rdf:resource="mc-' + mcID + '/xdstring-value"/>\n'
    rdfStr += padding.rjust(indent + 10) +'<sh:datatype rdf:resource="http://www.w3.org/2001/XMLSchema#string"/>\n'
    rdfStr += padding.rjust(indent + 10) +'<sh:maxCount rdf:datatype="http://www.w3.org/2001/XMLSchema#integer">1</sh:maxCount>\n'
    rdfStr += padding.rjust(indent + 10) +'<sh:minCount rdf:datatype="http://www.w3.org/2001/XMLSchema#integer">1</sh:minCount>\n'
    if data[12]:
        rdfStr += padding.rjust(indent + 10) + '<sh:defaultValue rdf:datatype="http://www.w3.org/2001/XMLSchema#string">' + data[12].strip() + '</sh:defaultValue>\n'
    if data[3]:
        rdfStr += padding.rjust(indent + 10) +'<sh:minLength rdf:datatype="http://www.w3.org/2001/XMLSchema#integer">' + data[3].strip() + '</sh:minLength>\n'
        
    if data[4]:
        rdfStr += padding.rjust(indent + 10) +'<sh:maxLength rdf:datatype="http://www.w3.org/2001/XMLSchema#integer">' + data[4].strip() + '</sh:maxLength>\n'
        
    if data[6]:
        rdfStr += padding.rjust(indent + 10) +'<sh:pattern rdf:datatype="http://www.w3.org/2001/XMLSchema#string">' + data[6].strip() + '</sh:pattern>\n'
        
    rdfStr += padding.rjust(indent + 10) +'\n'
    rdfStr += padding.rjust(indent + 10) +'\n'
    rdfStr += padding.rjust(indent + 10) +'\n'
    rdfStr += padding.rjust(indent + 10) +'\n'
    
    
    rdfStr += padding.rjust(indent + 8) +'</rdf:Description>\n'
    rdfStr += padding.rjust(indent + 6) +'</sh:property>\n'
    
    rdfStr += padding.rjust(indent + 6) + '</rdfs:Class>\n'
    return(rdfStr)


def xdstring(data):
    """
    Create xdString model.
    """

    adapterID = data[16].strip()
    mcID = data[15].strip()
    indent = 2
    padding = ('').rjust(indent)
        
    # Adapter
    xdstr = padding.rjust(indent) + '\n<xs:element name="ms-' + adapterID + '" substitutionGroup="s3m:Items" type="s3m:mc-' + adapterID + '"/>\n'
    xdstr += padding.rjust(indent) + '<xs:complexType name="mc-' + adapterID + '">\n'
    xdstr += padding.rjust(indent + 2) + '<xs:complexContent>\n'
    xdstr += padding.rjust(indent + 4) + '<xs:restriction base="s3m:XdAdapterType">\n'
    xdstr += padding.rjust(indent + 6) + '<xs:sequence>\n'
    xdstr += padding.rjust(indent + 8) + '<xs:element maxOccurs="unbounded" minOccurs="0" ref="s3m:ms-' + mcID + '"/>\n'
    xdstr += padding.rjust(indent + 6) + '</xs:sequence>\n'
    xdstr += padding.rjust(indent + 4) + '</xs:restriction>\n'
    xdstr += padding.rjust(indent + 2) + '</xs:complexContent>\n'
    xdstr += padding.rjust(indent) + '</xs:complexType>\n'
    # model component
    xdstr += padding.rjust(indent) + '<xs:element name="ms-' + mcID + '" substitutionGroup="s3m:XdAdapter-value" type="s3m:mc-' + mcID + '"/>\n'
    xdstr += padding.rjust(indent) + '<xs:complexType name="mc-' + mcID + '">\n'
    xdstr += padding.rjust(indent + 2) + '<xs:annotation>\n'
    xdstr += padding.rjust(indent + 4) + '<xs:documentation>\n'
    xdstr += padding.rjust(indent + 6) + data[9].strip() + '\n'
    xdstr += padding.rjust(indent + 4) + '</xs:documentation>\n'
    xdstr += padding.rjust(indent + 4) + '<xs:appinfo>\n'

    # add the RDF
    xdstr += xdstring_rdf(data)

    xdstr += padding.rjust(indent + 4) + '</xs:appinfo>\n'
    xdstr += padding.rjust(indent + 2) + '</xs:annotation>\n'    
    xdstr += padding.rjust(indent + 2) + '<xs:complexContent>\n'
    xdstr += padding.rjust(indent + 4) + '<xs:restriction base="s3m:XdStringType">\n'
    xdstr += padding.rjust(indent + 6) + '<xs:sequence>\n'
    xdstr += padding.rjust(indent + 8) + '<xs:element maxOccurs="1" minOccurs="1" name="label" type="xs:string" fixed="' + data[1].strip() + '"/>\n'
    xdstr += padding.rjust(indent + 8) + '<xs:element maxOccurs="1" minOccurs="0" ref="s3m:ExceptionalValue"/>\n'
    xdstr += padding.rjust(indent + 8) + '<xs:element maxOccurs="1" minOccurs="0" name="vtb" type="xs:dateTime"/>\n'
    xdstr += padding.rjust(indent + 8) + '<xs:element maxOccurs="1" minOccurs="0" name="vte" type="xs:dateTime"/>\n'
    xdstr += padding.rjust(indent + 8) + '<xs:element maxOccurs="1" minOccurs="0" name="tr" type="xs:dateTime"/>\n'
    xdstr += padding.rjust(indent + 8) + '<xs:element maxOccurs="1" minOccurs="0" name="modified" type="xs:dateTime"/>\n'

    if not data[3] and not data[4] and not data[5] and not data[6] and not data[12]:
        xdstr += padding.rjust(indent + 8) + '<xs:element maxOccurs="1" minOccurs="1"  name="xdstring-value" type="xs:string"/>\n'

    elif data[12] and not data[3] and not data[4] and not data[5] and not data[6]:
        xdstr += padding.rjust(indent + 8) + '<xs:element maxOccurs="1" minOccurs="1"  name="xdstring-value" type="xs:string" default="' + data[12].strip() + '"/>\n'

    else:
        xdstr += padding.rjust(indent + 8) + '<xs:element maxOccurs="1" minOccurs="1"  name="xdstring-value">\n'
        xdstr += padding.rjust(indent + 10) + '<xs:simpleType>\n'
        xdstr += padding.rjust(indent + 10) + '<xs:restriction base="xs:string">\n'
        if data[5]:
            enums = data[5].split('|')
            for e in enums:
                xdstr += padding.rjust(indent + 12) + '<xs:enumeration value="' + e.strip() + '"/>\n'
        else:
            if data[3]:
                xdstr += padding.rjust(indent + 12) + '<xs:minLength value="' + str(int(data[3])).strip() + '"/>\n'
                                                                                    
            if data[4] is not None:
                xdstr += padding.rjust(indent + 12) + '<xs:maxLength value="' + str(int(data[4])).strip() + '"/>\n'
                
            if data[6]:
                xdstr += padding.rjust(indent + 12) + '<xs:pattern value="' + data[6].strip() + '"/>\n'
        xdstr += padding.rjust(indent + 10) + '</xs:restriction>\n'
        xdstr += padding.rjust(indent + 10) + '</xs:simpleType>\n'
        xdstr += padding.rjust(indent + 8) + '</xs:element>\n'

    xdstr += padding.rjust(indent + 8) + \
        '<xs:element maxOccurs="1" minOccurs="1" name="xdstring-language" type="xs:language" default="en-US"/>\n'
    xdstr += padding.rjust(indent + 6) + '</xs:sequence>\n'
    xdstr += padding.rjust(indent + 4) + '</xs:restriction>\n'
    xdstr += padding.rjust(indent + 2) + '</xs:complexContent>\n'
    xdstr += padding.rjust(indent) + '</xs:complexType>\n'

    return(xdstr)


def xdtemporal_rdf(data):
    """
    Create RDF including SHACL constraints for xdTemporal model.
    """
    mcID = data[15].strip()    
    rdfStr = ''
    indent = 2
    padding = ('').rjust(indent)
    rdfStr += padding.rjust(indent + 6) + '<rdfs:Class rdf:about="mc-' + mcID + '">\n'
    rdfStr += padding.rjust(indent + 8) + '<rdfs:subClassOf rdf:resource="https://www.s3model.com/ns/s3m/s3model_3_0_0.xsd#XdTemporalType"/>\n'
    rdfStr += padding.rjust(indent + 8) + '<rdfs:subClassOf rdf:resource="https://www.s3model.com/ns/s3m/s3model/RMC"/>\n'
    rdfStr += padding.rjust(indent + 8) + '<rdfs:isDefinedBy rdf:resource="' + quote(data[10].strip()) + '"/>\n'
    if data[11]:  # are there additional predicate-object definitions?
        for po in data[11].splitlines():
            pred = po.split()[0]
            obj = po[len(pred):].strip()
            rdfStr += padding.rjust(indent + 8) + '<' + pred.strip() + ' rdf:resource="' + quote(obj.strip()) + '"/>\n'
            
    rdfStr += padding.rjust(indent + 6) +'<sh:property>\n'
    rdfStr += padding.rjust(indent + 8) +'<rdf:Description>\n'
    if data[2].lower() == 'date':    
        rdfStr += padding.rjust(indent + 8) +'<sh:path rdf:resource="mc-' + mcID + '/xdtemporal-date"/>\n'
        rdfStr += padding.rjust(indent + 8) +'<sh:datatype rdf:resource="http://www.w3.org/2001/XMLSchema#date"/>\n'
    elif data[2].lower() == 'time':    
        rdfStr += padding.rjust(indent + 8) +'<sh:path rdf:resource="mc-' + mcID + '/xdtemporal-time"/>\n'
        rdfStr += padding.rjust(indent + 8) +'<sh:datatype rdf:resource="http://www.w3.org/2001/XMLSchema#time"/>\n'
    elif data[2].lower() == 'datetime':    
        rdfStr += padding.rjust(indent + 8) +'<sh:path rdf:resource="mc-' + mcID + '/xdtemporal-datetime"/>\n'
        rdfStr += padding.rjust(indent + 8) +'<sh:datatype rdf:resource="http://www.w3.org/2001/XMLSchema#dateTime"/>\n'

    rdfStr += padding.rjust(indent + 10) +'<sh:maxCount rdf:datatype="http://www.w3.org/2001/XMLSchema#integer">1</sh:maxCount>\n'
    rdfStr += padding.rjust(indent + 10) +'<sh:minCount rdf:datatype="http://www.w3.org/2001/XMLSchema#integer">1</sh:minCount>\n'
        
    rdfStr += padding.rjust(indent + 8) +'</rdf:Description>\n'
    rdfStr += padding.rjust(indent + 6) +'</sh:property>\n'
    
    rdfStr += padding.rjust(indent + 6) + '</rdfs:Class>\n'
    return(rdfStr)


def xdtemporal(data):
    """
    Create xdTemporal model used for dates & times.
    """
    
    adapterID = data[16].strip()
    mcID = data[15].strip()
    indent = 2
    padding = ('').rjust(indent)
    
    # Adapter
    xdstr = padding.rjust(indent) + '\n<xs:element name="ms-' + adapterID + '" substitutionGroup="s3m:Items" type="s3m:mc-' + adapterID + '"/>\n'
    xdstr += padding.rjust(indent) + '<xs:complexType name="mc-' + adapterID + '">\n'
    xdstr += padding.rjust(indent + 2) + '<xs:complexContent>\n'
    xdstr += padding.rjust(indent + 4) + '<xs:restriction base="s3m:XdAdapterType">\n'
    xdstr += padding.rjust(indent + 6) + '<xs:sequence>\n'
    xdstr += padding.rjust(indent + 8) + '<xs:element maxOccurs="unbounded" minOccurs="0" ref="s3m:ms-' + mcID + '"/>\n'
    xdstr += padding.rjust(indent + 6) + '</xs:sequence>\n'
    xdstr += padding.rjust(indent + 4) + '</xs:restriction>\n'
    xdstr += padding.rjust(indent + 2) + '</xs:complexContent>\n'
    xdstr += padding.rjust(indent) + '</xs:complexType>\n'
    # model component
    xdstr += padding.rjust(indent) + '<xs:element name="ms-' + mcID + '" substitutionGroup="s3m:XdAdapter-value" type="s3m:mc-' + mcID + '"/>\n'
    xdstr += padding.rjust(indent) + '<xs:complexType name="mc-' + mcID + '">\n'
    xdstr += padding.rjust(indent + 2) + '<xs:annotation>\n'
    xdstr += padding.rjust(indent + 4) + '<xs:documentation>\n'
    xdstr += padding.rjust(indent + 6) + data[9].strip() + '\n'
    xdstr += padding.rjust(indent + 4) + '</xs:documentation>\n'
    
    xdstr += padding.rjust(indent + 4) + '<xs:appinfo>\n'
    # add the RDF
    xdstr += xdtemporal_rdf(data)
    xdstr += padding.rjust(indent + 4) + '</xs:appinfo>\n'

    
    xdstr += padding.rjust(indent + 2) + '</xs:annotation>\n'
    xdstr += padding.rjust(indent + 2) + '<xs:complexContent>\n'
    xdstr += padding.rjust(indent + 4) + '<xs:restriction base="s3m:XdTemporalType">\n'
    xdstr += padding.rjust(indent + 6) + '<xs:sequence>\n'
    xdstr += padding.rjust(indent + 8) + '<xs:element maxOccurs="1" minOccurs="1" name="label" type="xs:string" fixed="' + data[1].strip() + '"/>\n'
    xdstr += padding.rjust(indent + 8) + '<xs:element maxOccurs="1" minOccurs="0" ref="s3m:ExceptionalValue"/>\n'
    xdstr += padding.rjust(indent + 8) + '<xs:element maxOccurs="1" minOccurs="0" name="vtb" type="xs:dateTime"/>\n'
    xdstr += padding.rjust(indent + 8) + '<xs:element maxOccurs="1" minOccurs="0" name="vte" type="xs:dateTime"/>\n'
    xdstr += padding.rjust(indent + 8) + '<xs:element maxOccurs="1" minOccurs="0" name="tr" type="xs:dateTime"/>\n'
    xdstr += padding.rjust(indent + 8) + '<xs:element maxOccurs="1" minOccurs="0" name="modified" type="xs:dateTime"/>\n'
    if data[2].lower() == 'date':
        xdstr += padding.rjust(indent + 8) + '<xs:element maxOccurs="1" minOccurs="0" name="xdtemporal-date" type="xs:date"/>\n'
    else:
        xdstr += padding.rjust(indent + 8) + '<xs:element maxOccurs="0" minOccurs="0" name="xdtemporal-date" type="xs:date"/>\n'

    if data[2].lower() == 'time':
        xdstr += padding.rjust(indent + 8) + '<xs:element maxOccurs="1" minOccurs="0" name="xdtemporal-time" type="xs:time"/>\n'
    else:
        xdstr += padding.rjust(indent + 8) + '<xs:element maxOccurs="0" minOccurs="0" name="xdtemporal-time" type="xs:time"/>\n'

    if data[2].lower() == 'datetime':
        xdstr += padding.rjust(indent + 8) + '<xs:element maxOccurs="1" minOccurs="0" name="xdtemporal-datetime" type="xs:dateTime"/>\n'
    else:
        xdstr += padding.rjust(indent + 8) + '<xs:element maxOccurs="0" minOccurs="0" name="xdtemporal-datetime" type="xs:dateTime"/>\n'

    xdstr += padding.rjust(indent + 8) + '<xs:element maxOccurs="0" minOccurs="0" name="xdtemporal-day" type="xs:gDay"/>\n'
    xdstr += padding.rjust(indent + 8) + '<xs:element maxOccurs="0" minOccurs="0" name="xdtemporal-month" type="xs:gMonth"/>\n'
    xdstr += padding.rjust(indent + 8) + '<xs:element maxOccurs="0" minOccurs="0" name="xdtemporal-year" type="xs:gYear"/>\n'
    xdstr += padding.rjust(indent + 8) + '<xs:element maxOccurs="0" minOccurs="0" name="xdtemporal-year-month" type="xs:gYearMonth"/>\n'
    xdstr += padding.rjust(indent + 8) + '<xs:element maxOccurs="0" minOccurs="0" name="xdtemporal-month-day" type="xs:gMonthDay"/>\n'
    xdstr += padding.rjust(indent + 8) + '<xs:element maxOccurs="0" minOccurs="0" name="xdtemporal-duration" type="xs:duration"/>\n'
    xdstr += padding.rjust(indent + 6) + '</xs:sequence>\n'
    xdstr += padding.rjust(indent + 4) + '</xs:restriction>\n'
    xdstr += padding.rjust(indent + 2) + '</xs:complexContent>\n'
    xdstr += padding.rjust(indent) + '</xs:complexType>\n'

    return(xdstr)


def units(mcID, data):
    """
    Create xdString model as a Units component of a xdCount or xdQuantity.
    """
    
    indent = 2
    padding = ('').rjust(indent)
    xdstr = padding.rjust(indent) + '<xs:complexType name="mc-' + mcID + '">\n'
    xdstr += padding.rjust(indent + 2) + '<xs:annotation>\n'
    xdstr += padding.rjust(indent + 4) + '<xs:documentation>\n'
    xdstr += padding.rjust(indent + 6) + 'Unit constraint for: ' + data[9].strip() + '\n'
    xdstr += padding.rjust(indent + 4) + '</xs:documentation>\n'
    xdstr += padding.rjust(indent + 4) + '<xs:appinfo>\n'
    xdstr += padding.rjust(indent + 6) + '<rdfs:Class rdf:about="mc-' + mcID + '">\n'
    xdstr += padding.rjust(indent + 8) + '<rdfs:subClassOf rdf:resource="https://www.s3model.com/ns/s3m/s3model_3_0_0.xsd#XdStringType"/>\n'
    xdstr += padding.rjust(indent + 8) + '<rdfs:subClassOf rdf:resource="https://www.s3model.com/ns/s3m/s3model/RMC"/>\n'
    xdstr += padding.rjust(indent + 8) + '<rdfs:isDefinedBy rdf:resource="' + quote(data[10].strip()) + '"/>\n'
    if data[11]:  # are there additional predicate-object definitions?
        for po in data[11].splitlines():
            pred = po.split()[0]
            obj = po[len(pred):].strip()
            xdstr += padding.rjust(indent + 8) + '<' + pred.strip() + ' rdf:resource="' + quote(obj.strip()) + '"/>\n'
    xdstr += padding.rjust(indent + 6) + '</rdfs:Class>\n'
    xdstr += padding.rjust(indent + 4) + '</xs:appinfo>\n'
    xdstr += padding.rjust(indent + 2) + '</xs:annotation>\n'
    xdstr += padding.rjust(indent + 2) + '<xs:complexContent>\n'
    xdstr += padding.rjust(indent + 4) + '<xs:restriction base="s3m:XdStringType">\n'
    xdstr += padding.rjust(indent + 6) + '<xs:sequence>\n'
    xdstr += padding.rjust(indent + 8) + '<xs:element maxOccurs="1" minOccurs="1" name="label" type="xs:string" fixed="' + data[1].strip() + ' Units"/>\n'
    xdstr += padding.rjust(indent + 8) + '<xs:element maxOccurs="1" minOccurs="0" ref="s3m:ExceptionalValue"/>\n'
    xdstr += padding.rjust(indent + 8) + '<xs:element maxOccurs="1" minOccurs="0" name="vtb" type="xs:dateTime"/>\n'
    xdstr += padding.rjust(indent + 8) + '<xs:element maxOccurs="1" minOccurs="0" name="vte" type="xs:dateTime"/>\n'
    xdstr += padding.rjust(indent + 8) + '<xs:element maxOccurs="1" minOccurs="0" name="tr" type="xs:dateTime"/>\n'
    xdstr += padding.rjust(indent + 8) + '<xs:element maxOccurs="1" minOccurs="0" name="modified" type="xs:dateTime"/>\n'
    xdstr += padding.rjust(indent + 8) + '<xs:element maxOccurs="1" minOccurs="1"  name="xdstring-value" type="xs:string" fixed="' + data[12].strip() + '"/>\n'
    xdstr += padding.rjust(indent + 8) + '<xs:element maxOccurs="1" minOccurs="1" name="xdstring-language" type="xs:language" default="en-US"/>\n'
    xdstr += padding.rjust(indent + 6) + '</xs:sequence>\n'
    xdstr += padding.rjust(indent + 4) + '</xs:restriction>\n'
    xdstr += padding.rjust(indent + 2) + '</xs:complexContent>\n'
    xdstr += padding.rjust(indent) + '</xs:complexType>\n'

    return(xdstr)


def xsd_data(dataID, indent, def_url, db_file):
    """
    Create xdCluster model for the data portion of an Entry.
    """
    
    indent += 2
    padding = ('').rjust(indent)
    dstr = padding.rjust(indent) + '<xs:element name="ms-' + dataID + '" substitutionGroup="s3m:Item" type="s3m:mc-' + dataID + '"/>\n'
    dstr += padding.rjust(indent) + '<xs:complexType name="mc-' + dataID + '">\n'
    dstr += padding.rjust(indent + 2) + '<xs:annotation>\n'
    dstr += padding.rjust(indent + 4) + '<xs:documentation>\n'
    dstr += padding.rjust(indent + 6) + 'This is the Cluster that groups all of the data items (columns) definitions into one unit.\n'
    dstr += padding.rjust(indent + 4) + '</xs:documentation>\n'
    dstr += padding.rjust(indent + 4) + '<xs:appinfo>\n'
    dstr += padding.rjust(indent + 6) + '<rdfs:Class rdf:about="mc-' + dataID + '">\n'
    dstr += padding.rjust(indent + 8) + '<rdfs:subClassOf rdf:resource="https://www.s3model.com/ns/s3m/s3model_3_0_0.xsd#ClusterType"/>\n'
    dstr += padding.rjust(indent + 8) + '<rdfs:subClassOf rdf:resource="https://www.s3model.com/ns/s3m/s3model/RMC"/>\n'
    dstr += padding.rjust(indent + 8) + '<rdfs:isDefinedBy rdf:resource="' + def_url + '"/>\n'
    dstr += padding.rjust(indent + 6) + '</rdfs:Class>\n'
    dstr += padding.rjust(indent + 4) + '</xs:appinfo>\n'
    dstr += padding.rjust(indent + 2) + '</xs:annotation>\n'
    dstr += padding.rjust(indent + 2) + '<xs:complexContent>\n'
    dstr += padding.rjust(indent + 4) + '<xs:restriction base="s3m:ClusterType">\n'
    dstr += padding.rjust(indent + 6) + '<xs:sequence>\n'
    dstr += padding.rjust(indent + 8) + '<xs:element maxOccurs="1" minOccurs="1" name="label" type="xs:string" fixed="Data Items"/>\n'

    # now we need to loop through the db and create all of the model components while keeping track so we can add them here too.
    # the dictionary uses the mc uuid as the key. The items are the complete mc code.
    mcDict = OrderedDict()
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute("SELECT * FROM record")
    rows = c.fetchall()
    conn.close()

    for row in rows:
        if row[2].lower() == 'integer':
            mcDict[row[16].strip()] = xdcount(row)
        elif row[2].lower() == 'decimal':
            mcDict[row[16].strip()] = xdquantity(row)
        elif row[2].lower() in ('date', 'datetime', 'time'):
            mcDict[row[16].strip()] = xdtemporal(row)
        elif row[2].lower() == 'string':
            mcDict[row[16].strip()] = xdstring(row)
        else:
            raise ValueError("Invalid datatype")

    for mc_id in mcDict.keys():
        dstr += padding.rjust(indent + 8) + '<xs:element maxOccurs="1" minOccurs="0" ref="s3m:ms-' + mc_id + '"/>\n'

    dstr += padding.rjust(indent + 6) + '</xs:sequence>\n'
    dstr += padding.rjust(indent + 4) + '</xs:restriction>\n'
    dstr += padding.rjust(indent + 2) + '</xs:complexContent>\n'
    dstr += padding.rjust(indent) + '</xs:complexType>\n\n'

    for mc_id in mcDict.keys():
        dstr += mcDict[mc_id]

    return(dstr)


def xsd_entry(data, db_file):
    """
    Create the Entry model that si a wrapper for the data as well as various provenance components in S3Model.
    """
    
    indent = 2
    padding = ('').rjust(indent)
    dataID = str(uuid4())

    estr = padding.rjust(indent) + '<xs:element name="ms-' + data[6].strip() + '" substitutionGroup="s3m:Definition" type="s3m:mc-' + data[6].strip() + '"/>\n'
    estr += padding.rjust(indent) + '<xs:complexType name="mc-' + data[6].strip() + '">\n'
    estr += padding.rjust(indent + 2) + '<xs:annotation>\n'
    estr += padding.rjust(indent + 4) + '<xs:documentation>\n'
    estr += padding.rjust(indent + 6) + 'This is the Entry container that provides all the required contextual information to manage a dataset. It is analogous to a dataset catalog entry.\n'
    estr += padding.rjust(indent + 4) + '</xs:documentation>\n'
    estr += padding.rjust(indent + 4) + '<xs:appinfo>\n'
    estr += padding.rjust(indent + 6) + '<rdfs:Class rdf:about="mc-' + data[6].strip() + '">\n'
    estr += padding.rjust(indent + 8) + '<rdfs:subClassOf rdf:resource="https://www.s3model.com/ns/s3m/s3model_3_0_0.xsd#EntryType"/>\n'
    estr += padding.rjust(indent + 8) + '<rdfs:subClassOf rdf:resource="https://www.s3model.com/ns/s3m/s3model/RMC"/>\n'
    estr += padding.rjust(indent + 8) + '<rdfs:isDefinedBy rdf:resource="' + quote(data[4].strip()) + '"/>\n'
    estr += padding.rjust(indent + 6) + '</rdfs:Class>\n'
    estr += padding.rjust(indent + 4) + '</xs:appinfo>\n'
    estr += padding.rjust(indent + 2) + '</xs:annotation>\n'
    estr += padding.rjust(indent + 2) + '<xs:complexContent>\n'
    estr += padding.rjust(indent + 4) + '<xs:restriction base="s3m:EntryType">\n'
    estr += padding.rjust(indent + 6) + '<xs:sequence>\n'
    estr += padding.rjust(indent + 8) + '<xs:element maxOccurs="1" minOccurs="1" name="label" type="xs:string" fixed="' + data[0].strip() + '"/>\n'
    estr += padding.rjust(indent + 8) + '<xs:element maxOccurs="1" minOccurs="1" name="entry-language" type="xs:language" fixed="en-US"/>\n'
    estr += padding.rjust(indent + 8) + '<xs:element maxOccurs="1" minOccurs="1" name="entry-encoding" type="xs:string" fixed="utf-8"/>\n'
    estr += padding.rjust(indent + 8) + '<!-- current-state -->\n'
    estr += padding.rjust(indent + 8) + '<xs:element maxOccurs="1" minOccurs="1" ref="s3m:ms-' + data[7].strip() + '"/>\n'
    estr += padding.rjust(indent + 8) + '<!-- subject -->\n'
    estr += padding.rjust(indent + 8) + '<!-- provider -->\n'
    estr += padding.rjust(indent + 8) + '<!-- participations -->\n'
    estr += padding.rjust(indent + 8) + '<!-- protocol -->\n'
    estr += padding.rjust(indent + 8) + '<!-- workflow -->\n'
    estr += padding.rjust(indent + 8) + '<!-- audit -->\n'
    estr += padding.rjust(indent + 8) + '<!-- attestation -->\n'
    estr += padding.rjust(indent + 8) + '<!-- entry links -->\n'
    estr += padding.rjust(indent + 6) + '</xs:sequence>\n'
    estr += padding.rjust(indent + 4) + '</xs:restriction>\n'
    estr += padding.rjust(indent + 2) + '</xs:complexContent>\n'
    estr += padding.rjust(indent) + '</xs:complexType>\n\n'
    estr += xsd_data(data[7].strip(), indent, data[4].strip(), db_file)
    return(estr)


def xsd_dm(data):
    """
    Create the Data Model wrapper for the metadata and Entry.
    """
    
    indent = 2
    padding = ('').rjust(indent)

    dmstr = padding.rjust(indent) + '<xs:element name="dm-' + data[5].strip() + '" type="s3m:mc-' + data[5].strip() + '"/>\n'
    dmstr += padding.rjust(indent) + '<xs:complexType name="mc-' + data[5].strip() + '">\n'
    dmstr += padding.rjust(indent + 2) + '<xs:annotation>\n'
    dmstr += padding.rjust(indent + 4) + '<xs:documentation>\n'
    dmstr += padding.rjust(indent + 6) + data[1].strip() + '\n'
    dmstr += padding.rjust(indent + 4) + '</xs:documentation>\n'
    dmstr += padding.rjust(indent + 4) + '<xs:appinfo>\n'
    dmstr += padding.rjust(indent + 6) + '<rdfs:Class rdf:about="mc-' + data[5].strip() + '">\n'
    dmstr += padding.rjust(indent + 8) + '<rdfs:subClassOf rdf:resource="https://www.s3model.com/ns/s3m/s3model_3_0_0.xsd#DMType"/>\n'
    dmstr += padding.rjust(indent + 8) + '<rdfs:subClassOf rdf:resource="https://www.s3model.com/ns/s3m/s3model/RMC"/>\n'
    dmstr += padding.rjust(indent + 8) + '<rdfs:isDefinedBy rdf:resource="' + quote(data[4].strip()) + '"/>\n'
    dmstr += padding.rjust(indent + 6) + '</rdfs:Class>\n'
    dmstr += padding.rjust(indent + 4) + '</xs:appinfo>\n'
    dmstr += padding.rjust(indent + 2) + '</xs:annotation>\n'
    dmstr += padding.rjust(indent + 2) + '<xs:complexContent>\n'
    dmstr += padding.rjust(indent + 4) + '<xs:restriction base="s3m:DMType">\n'
    dmstr += padding.rjust(indent + 6) + '<xs:sequence>\n'
    dmstr += padding.rjust(indent + 8) + '<xs:element maxOccurs="1" minOccurs="1" ref="s3m:ms-' + data[6].strip() + '"/>\n'
    dmstr += padding.rjust(indent + 6) + '</xs:sequence>\n'
    dmstr += padding.rjust(indent + 4) + '</xs:restriction>\n'
    dmstr += padding.rjust(indent + 2) + '</xs:complexContent>\n'
    dmstr += padding.rjust(indent) + '</xs:complexType>\n'
    return(dmstr)


def xsd_rdf(xsdfile, outdir, dm_id, db_file):
    """
        Generate the RDF from the semantics embedded in the XSD.
        """

    rootdir = '.'
    ns_dict = {'xs': 'http://www.w3.org/2001/XMLSchema',
              'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
              'xsd': 'http://www.w3.org/2001/XMLSchema#',
              'dc': 'http://purl.org/dc/elements/1.1/',
              'skos': 'http://www.w3.org/2004/02/skos/core#',
              'foaf': 'http://xmlns.com/foaf/0.1/',
              'sioc': 'http://rdfs.org/sioc/ns#',
              'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
              'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
              'dct': 'http://purl.org/dc/terms/',
              'owl': 'http://www.w3.org/2002/07/owl#',
              'sh': 'http://www.w3.org/ns/shacl#',
              'vc': 'http://www.w3.org/2007/XMLSchema-versioning',
              's3m': 'https://www.s3model.com/ns/s3m/'}

    for abbrev in NSDEF.keys():
        ns_dict[abbrev] = NSDEF[abbrev]

    parser = etree.XMLParser(ns_clean=True, recover=True)
    cls_def = etree.XPath("//xs:annotation/xs:appinfo/rdfs:Class", namespaces=ns_dict)
    sh_def = etree.XPath("//xs:annotation/xs:appinfo/sh:property", namespaces=ns_dict)

    md = etree.XPath("//rdf:RDF/rdfs:Class", namespaces=ns_dict)

    rdf_file = os.open(outdir + '/dm-' + str(dm_id) + '.rdf', os.O_RDWR | os.O_CREAT)

    rdfstr = """<?xml version="1.0" encoding="UTF-8"?>\n<rdf:RDF xmlns:rdf='http://www.w3.org/1999/02/22-rdf-syntax-ns#' \nxmlns:s3m='https://www.s3model.com/ns/s3m/'>\n"""

    tree = etree.parse(xsdfile, parser)
    root = tree.getroot()

    rdf = cls_def(root)
    shacl = sh_def(root)
    
    for s in shacl:
        rdfstr += '    ' + etree.tostring(s).decode('utf-8') + '\n'
        
    for m in md(root):
        rdfstr += '    ' + etree.tostring(m).decode('utf-8') + '\n'

    for r in rdf:
        rdfstr += '    ' + etree.tostring(r).decode('utf-8') + '\n'

    # create triples for all of the elements to complexTypes
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute("SELECT * FROM record")
    rows = c.fetchall()
    conn.close()

    for row in rows:
        rdfstr += '<rdfs:Class xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"  xmlns:s3m="https://www.s3model.com/ns/s3m/" rdf:about="s3m:ms-' + row[15].strip() + '">\n'
        rdfstr += '  <s3m:isRMSOf rdf:resource="s3m:mc-' + row[15].strip() + '"/>\n'
        rdfstr += '</rdfs:Class>\n'

    rdfstr += '</rdf:RDF>\n'

    os.write(rdf_file, rdfstr.encode("utf-8"))
    os.close(rdf_file)


def make_model(db_file, outdir):
    """
    Create an S3M data model schema based on the database information.
    """

    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute("SELECT * FROM model")
    row = c.fetchone()
    dmID = row[5].strip()

    model = outdir + '/dm-' + dmID + '.xsd'
    print("\nGenerating model file: " + outdir + '/dm-' + dmID + '.xsd\n')
    xsd = open(model, 'w')
    md = []
    md.append(dmID)
    md.append(row[0])
    md.append(row[3])
    md.append(row[1])
    md.append(row[2])
    def_url = row[4]
    conn.close()

    xsd_str = xsd_header()
    xsd_str += xsd_metadata(md)
    xsd_str += xsd_dm(row)
    xsd_str += xsd_entry(row, db_file)

    xsd_str += '\n</xs:schema>\n'

    # write the xsd file
    xsd.write(xsd_str)
    xsd.close()
    try:
        xmlschema_doc = etree.parse(model)
    except:
        print('Model Error', "There was an error in generating the schema. Please re-edit the database and look for errors. Probably undefined namespaces or improperly formatted predicate-object pair.")
        return None

    xsd_rdf(model, outdir, dmID, db_file)

    return model


def xml_hdr(model, schema, schemaFile):
    xstr = '<s3m:dm-' + model[5].strip() + '\n'
    xstr += 'xmlns:s3m="https://www.s3model.com/ns/s3m/"\n'
    xstr += 'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n'
    xstr += 'xsi:schemaLocation="https://www.s3model.com/ns/s3m/ https://dmgen.s3model.com/dmlib/' + schemaFile + '">\n'
    xstr += '  <s3m:ms-' + model[6].strip() + '>\n'
    xstr += '    <label>' + model[0].strip() + '</label>\n'
    xstr += '    <entry-language>en-US</entry-language>\n'
    xstr += '    <entry-encoding>utf-8</entry-encoding>\n'
    xstr += '    <s3m:ms-' + model[7].strip() + '>\n'
    xstr += '      <label>Data Items</label>\n'
    return(xstr)


def xml_count(row, data):
    xstr = '      <s3m:ms-' + row[16].strip() + '>\n'
    xstr += '      <s3m:ms-' + row[15].strip() + '>\n'
    xstr += '        <label>' + row[1].strip() + '</label>\n'
    xstr += '        <magnitude-status>equal</magnitude-status>\n'
    xstr += '        <error>0</error>\n'
    xstr += '        <accuracy>0</accuracy>\n'
    xstr += '        <xdcount-value>' + data[row[0].strip()] + '</xdcount-value>\n'
    xstr += '        <xdcount-units>\n'
    xstr += '          <label>' + row[1].strip() + ' Units</label>\n'
    xstr += '          <xdstring-value>' + row[14].strip() + '</xdstring-value>\n'
    xstr += '          <xdstring-language>en-US</xdstring-language>\n'
    xstr += '        </xdcount-units>\n'
    xstr += '      </s3m:ms-' + row[15].strip() + '>\n'
    xstr += '      </s3m:ms-' + row[16].strip() + '>\n'
    return(xstr)


def rdf_count(row, data):
    rstr = '      <rdfs:Class rdf:about="s3m:ms-' + row[15].strip() + '">\n'
    rstr += '        <rdfs:label>' + row[1].strip() + '</rdfs:label>\n'
    rstr += '        <rdfs:value rdf:datatype="xs:int">' + data[row[0].strip()] + '</rdfs:value>\n'
    rstr += '      </rdfs:Class>\n'
    return(rstr)


def xml_quantity(row, data):
    xstr = '      <s3m:ms-' + row[16].strip() + '>\n'
    xstr += '      <s3m:ms-' + row[15].strip() + '>\n'
    xstr += '        <label>' + row[1].strip() + '</label>\n'
    xstr += '        <magnitude-status>equal</magnitude-status>\n'
    xstr += '        <error>0</error>\n'
    xstr += '        <accuracy>0</accuracy>\n'
    xstr += '        <xdquantity-value>' + data[row[0].strip()] + '</xdquantity-value>\n'
    xstr += '        <xdquantity-units>\n'
    xstr += '          <label>' + row[1].strip() + ' Units</label>\n'
    xstr += '          <xdstring-value>' + row[14].strip() + '</xdstring-value>\n'
    xstr += '          <xdstring-language>en-US</xdstring-language>\n'
    xstr += '        </xdquantity-units>\n'
    xstr += '      </s3m:ms-' + row[15].strip() + '>\n'
    xstr += '      </s3m:ms-' + row[16].strip() + '>\n'
    return(xstr)


def rdf_quantity(row, data):
    rstr = '      <rdfs:Class rdf:about="s3m:ms-' + row[15].strip() + '">\n'
    rstr += '        <rdfs:label>' + row[1].strip() + '</rdfs:label>\n'
    rstr += '        <rdfs:value rdf:datatype="xs:decimal">' + data[row[0].strip()] + '</rdfs:value>\n'
    rstr += '      </rdfs:Class>\n'
    return(rstr)


def xml_float(row, data):
    xstr = '      <s3m:ms-' + row[16].strip() + '>\n'
    xstr += '      <s3m:ms-' + row[15].strip() + '>\n'
    xstr += '        <label>' + row[1].strip() + '</label>\n'
    xstr += '        <magnitude-status>equal</magnitude-status>\n'
    xstr += '        <error>0</error>\n'
    xstr += '        <accuracy>0</accuracy>\n'
    xstr += '        <xdfloat-value>' + data[row[0].strip()] + '</xdfloat-value>\n'
    xstr += '        <xdfloat-units>\n'
    xstr += '          <label>' + row[1].strip() + ' Units</label>\n'
    xstr += '          <xdstring-value>' + row[14].strip() + '</xdstring-value>\n'
    xstr += '          <xdstring-language>en-US</xdstring-language>\n'
    xstr += '        </xdfloat-units>\n'
    xstr += '      </s3m:ms-' + row[15].strip() + '>\n'
    xstr += '      </s3m:ms-' + row[16].strip() + '>\n'
    return(xstr)


def rdf_quantity(row, data):
    rstr = '      <rdfs:Class rdf:about="s3m:ms-' + row[15].strip() + '">\n'
    rstr += '        <rdfs:label>' + row[1].strip() + '</rdfs:label>\n'
    rstr += '        <rdfs:value rdf:datatype="xs:float">' + data[row[0].strip()] + '</rdfs:value>\n'
    rstr += '      </rdfs:Class>\n'
    return(rstr)


def xml_temporal(row, data):
    xstr = '      <s3m:ms-' + row[16].strip() + '>\n'
    xstr += '      <s3m:ms-' + row[15].strip() + '>\n'
    xstr += '        <label>' + row[1].strip() + '</label>\n'
    if row[2].lower() == 'date':
        xstr += '        <xdtemporal-date>' + data[row[0].strip()] + '</xdtemporal-date>\n'
    if row[2].lower() == 'time':
        xstr += '        <xdtemporal-time>' + data[row[0].strip()] + '</xdtemporal-time>\n'
    if row[2].lower() == 'datetime':
        xstr += '        <xdtemporal-datetime>' + data[row[0].strip()] + '</xdtemporal-datetime>\n'
    xstr += '      </s3m:ms-' + row[15].strip() + '>\n'
    xstr += '      </s3m:ms-' + row[16].strip() + '>\n'
    return(xstr)


def rdf_temporal(row, data):
    rstr = '      <rdfs:Class rdf:about="s3m:ms-' + row[15].strip() + '">\n'
    rstr += '        <rdfs:label>' + row[1].strip() + '</rdfs:label>\n'
    if row[2].lower() == 'date':
        rstr += '        <rdfs:value rdf:datatype="xs:date">' + data[row[0].strip()] + '</rdfs:value>\n'
    if row[2].lower() == 'time':
        rstr += '        <rdfs:value rdf:datatype="xs:time">' + data[row[0].strip()] + '</rdfs:value>\n'
    if row[2].lower() == 'datetime':
        rstr += '        <rdfs:value rdf:datatype="xs:dateTime">' + data[row[0].strip()] + '</rdfs:value>\n'
    rstr += '      </rdfs:Class>\n'
    return(rstr)


def xml_string(row, data):
    xstr = '      <s3m:ms-' + row[16].strip() + '>\n'
    xstr += '      <s3m:ms-' + row[15].strip() + '>\n'
    xstr += '        <label>' + row[1].strip() + '</label>\n'
    xstr += '        <xdstring-value>' + data[row[0].strip()] + '</xdstring-value>\n'
    xstr += '        <xdstring-language>en-US</xdstring-language>\n'
    xstr += '      </s3m:ms-' + row[15].strip() + '>\n'
    xstr += '      </s3m:ms-' + row[16].strip() + '>\n'
    return(xstr)


def rdf_string(row, data):
    rstr = '      <rdfs:Class rdf:about="s3m:ms-' + row[15].strip() + '">\n'
    rstr += '        <rdfs:label>' + row[1].strip() + '</rdfs:label>\n'
    rstr += '        <rdfs:value rdf:datatype="xs:string">' + data[row[0].strip()] + '</rdfs:value>\n'
    rstr += '      </rdfs:Class>\n'
    return(rstr)


def make_data(schema, db_file, infile, delim, outdir, connRDF, connXML, connJSON):
    """
    Create XML and JSON data files and an RDF graph based on the model.
    """
    base = os.path.basename(infile)
    filePrefix = os.path.splitext(base)[0]
    schemaFile = os.path.basename(schema)

    schema_doc = etree.parse(schema)
    modelSchema = etree.XMLSchema(schema_doc)

    print('\n\nGeneration: ', "Generate data for: " + schemaFile + ' using ' + base + '\n')
    namespaces = {"https://www.s3model.com/ns/s3m/": "s3m", "http://www.w3.org/2001/XMLSchema-instance": "xsi"}
    xmldir = outdir + '/xml/'
    os.makedirs(xmldir, exist_ok=True)
    rdfdir = outdir + '/rdf/'
    os.makedirs(rdfdir, exist_ok=True)
    jsondir = outdir + '/json/'
    os.makedirs(jsondir, exist_ok=True)

    # get info from the sqlite DB
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute("SELECT * FROM model")
    model = c.fetchone()
    c.execute("SELECT * FROM record")
    rows = c.fetchall()
    conn.close()
    
    # count the lines in the file
    with open(infile) as f:
        s = f.read()
    csv_len =  s.count('\n') - 1
    f.close()
    
    with open(infile) as csvfile:
        val_log = 'id,valid\n'
        reader = csv.DictReader(csvfile, delimiter=delim)
        
        # this test is really for the 'generate' mode. 
        hdrs = reader.fieldnames
        for i in range(0,len(hdrs)):
            if hdrs[i] != rows[i][0]:
                print("\n\nThere was an error matching the data input file to the selected model database.")
                print('Datafile: ' + hdrs[i] + '  Model: ' + rows[i][0] + '\n\n')
                exit(code=1)
                        
        # for data in reader:
        with click.progressbar(reader, label="Writing " + str(csv_len) + " data files: ", length=csv_len) as bar:
            for data in bar:
            
                file_id = filePrefix + '-' + shortuuid.uuid()
    
                xmlProlog = '<?xml version="1.0" encoding="UTF-8"?>\n'  # lxml doesn't want this in the file during validation, it has to be reinserted afterwards. 
    
                xmlStr = ''
                rdfStr = '<?xml version="1.0" encoding="UTF-8"?>\n<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"\nxmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"\nxmlns:s3m="https://www.s3model.com/ns/s3m/"\nxmlns:xs="http://www.w3.org/2001/XMLSchema">\n'
                rdfStr += '<rdfs:Class rdf:about="' + file_id + '">\n'
                rdfStr += '  <s3m:isInstanceOf rdf:resource="dm-' + model[5].strip() + '"/>\n'
                rdfStr += '</rdfs:Class>\n'
    
                # get the DM and Entry components.
                xmlStr += xml_hdr(model, schema, schemaFile)
    
                for row in rows:
                    if row[2].lower() == 'integer':
                        xmlStr += xml_count(row, data)
                        rdfStr += rdf_count(row, data)
                    elif row[2].lower() == 'decimal':
                        xmlStr += xml_quantity(row, data)
                        rdfStr += rdf_quantity(row, data)
                    elif row[2].lower() == 'float':
                        xmlStr += xml_float(row, data)
                        rdfStr += rdf_float(row, data)
                    elif row[2].lower() in ('date', 'datetime', 'time'):
                        xmlStr += xml_temporal(row, data)
                        rdfStr += rdf_temporal(row, data)
                    elif row[2].lower() == 'string':
                        xmlStr += xml_string(row, data)
                        rdfStr += rdf_string(row, data)
                    else:
                        raise ValueError("Invalid datatype")
    
                xmlStr += '    </s3m:ms-' + model[7].strip() + '>\n'
                xmlStr += '  </s3m:ms-' + model[6].strip() + '>\n'
                xmlStr += '</s3m:dm-' + model[5].strip() + '>\n'
    
                # validate the XML data file and enter the appropriate RDF statement as well as an enry in the validation log.
                try:
                    tree = etree.parse(StringIO(xmlStr))
                    modelSchema.assertValid(tree)
                    rdfStr += '  <rdfs:Class rdf:about="' + file_id + '">\n'
                    rdfStr += '    <rdfs:subClassOf rdf:resource="https://www.s3model.com/ns/s3m/s3model/DataInstanceValid"/>\n'
                    rdfStr += '  </rdfs:Class>\n'
                    val_log += file_id + ',true\n'
                except etree.DocumentInvalid:
                    rdfStr += '  <rdfs:Class rdf:about="' + file_id + '">\n'
                    rdfStr += '    <rdfs:subClassOf rdf:resource="https://www.s3model.com/ns/s3m/s3model/DataInstanceError"/>\n'
                    rdfStr += '  </rdfs:Class>\n'
                    val_log += file_id + ',false\n'
    
                rdfStr += '</rdf:RDF>\n'
                
                # add the prolog back to the top
                xmlStr = xmlProlog + xmlStr
    
                if connXML:
                    connXML.add(file_id + '.xml', xmlStr)
                else:
                    xmlFile = open(xmldir + file_id + '.xml', 'w')
                    xmlFile.write(xmlStr)
                    xmlFile.close()
    
                if connRDF:
                    connRDF.addData(rdfStr, rdf_format=RDFFormat.RDFXML,
                                    base_uri=None, context=None)
                else:
                    rdfFile = open(rdfdir + file_id + '.rdf', 'w')
                    rdfFile.write(rdfStr)
                    rdfFile.close()
    
                d = xmltodict.parse(xmlStr, xml_attribs=True,
                                    process_namespaces=True, namespaces=namespaces)
                jsonStr = json.dumps(d, indent=4)
                if connJSON:
                    from bson.json_util import loads
                    connJSON[filePrefix].insert_one(loads(jsonStr))
                else:
                    jsonFile = open(jsondir + file_id + '.json', 'w')
                    jsonFile.write(jsonStr)
                    jsonFile.close()
    vlog = open(outdir + os.path.sep + filePrefix + '_validation_log.csv', 'w')
    vlog.write(val_log)
    vlog.close()
    return True
