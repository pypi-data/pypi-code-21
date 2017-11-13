import os
import shutil
from lxml import etree
from lxml import objectify
import click


@click.command()
@click.option('--xsd', default='/Tools/data/xsd/BC9.xsd', help='Root directory of the data.')
@click.option('--inputdir', default='/Tools/data/input', help='Root directory of the data.')
@click.option('--outputdir', default='/Tools/data/output', help='Root directory of the data.')
@click.option('--errordir', default='/Tools/data/error', help='Root directory of the data.')
def main(xsd, inputdir, outputdir, errordir):
    xsd_doc = xsdFromFile(xsd)
    list_files = get_files(inputdir)
    countValid = 0
    countInvalid = 0
    countKnownError = 0
    for filename in list_files:
        #print(filename, )
        xmlException = False
        try:
            xml_doc = xmlTreeFromFile(filename)
            # print("validXML: ", validXML(xml_doc, xsd_doc))
            # printXML(xml_doc)
            # print(xml_doc.getroot())
            DCS_MESSAGES = xml_doc.getroot()
            filenameFromXml = getFilenameFromXml(DCS_MESSAGES, filename)
            messageType = getMessageType(DCS_MESSAGES, filenameFromXml)
        except:
            # lxml.etree.XMLSyntaxError xe:
            xmlException = True

        if xmlException or not validXML(xml_doc, xsd_doc):
            print('Invalid xml: ', filename)
            knownError = checkKnownIssues(filename, xml_doc)
            if knownError != "":
                countKnownError += 1
                knownErrorPath = os.path.join(errorDir, str(knownError))
                knownErrorPath = os.path.join(knownErrorPath, str(filenameFromXml))
                copyFile(filename, knownErrorPath)
            else:
                countInvalid += 1
                print(xsd_doc.error_log)
                messageTypePath = os.path.join(errordir, str(messageType))
                messageTypePath = os.path.join(messageTypePath, str(filenameFromXml))
                copyFile(filename, messageTypePath)
        else:
            countValid += 1
            # print('Valid xml', filename)
            messageTypePath = os.path.join(outputdir, str(messageType))
            messageTypePath = os.path.join(messageTypePath, str(filenameFromXml))
            #moveFileToDir(filename, messageTypePath)
            copyFile(filename, messageTypePath)

    print("Number of files valid: ", countValid, " Invalid: ", countInvalid, " KnownError:", countKnownError)


def checkKnownIssues(filename, xml_doc):
    result = ""
    if filename.find("_75_") > 0:
        result = "LOACTION_NR"
        print("Known error in: ", filename, " found <LOACTION_NR>, expecting <LOCATION_NR>")
    elif filename.find("_76_") > 0:
            result = "GARAGE_NR"
            print("Known error in: ", filename, " found <GARAGE_NR>, expecting <GARAGE_NUMBER>")
    elif filename.find("_77_") > 0:
        result = "GARAGE_NR"
        print("Known error in: ", filename, " found <GARAGE_NR>, expecting <GARAGE_NUMBER>")
    elif filename.find("_28_") > 0:
        result = "SIFT_SEQUENCE"
        print("Known error in: ", filename, " found <SIFT_SEQUENCE>, expecting <SHIFT_SEQUENCE>")
    return result


def getMessageType(xmlobj, filename):
    messageType = xmlobj.find(".//MESSAGE_TYPE")
    if messageType == "":
        # print('DCS_MESSAGES.find(".//REF_XML_OUT_FILENAME")', DCS_MESSAGES.find(".//REF_XML_OUT_FILENAME"))
        fn = xmlobj.find(".//REF_XML_OUT_FILENAME")
        list = fn.split("_")
        if list.__len__() > 1:
            messageType = list[1]
    if messageType == "":
        list = filename.split("_")
        if list.__len__() > 1:
            messageType = list[1]
    #print(" Message type: ", messageType)
    return messageType

def getVehicle(xmlobj, filename):
    vehicle = xmlobj.find(".//MOBILE_ID")
    if vehicle == "":
        fn = xmlobj.find(".//REF_XML_OUT_FILENAME")
        vehicle = filename[-9:-4]
        # list = filename.split("_.")
        # if list.__len__() > 1:
        #     vehicle = list[1]
    if vehicle == "":
        vehicle = filename[-9:-4]
        # list = filename.split("_.")
        # if list.__len__() > 1:
        #     vehicle = list[1]
    print(" Vehicle: ", vehicle)
    return vehicle


def getFilenameFromXml(xmlobj, filename):
    filenameFromXml = xmlobj.find(".//REF_XML_OUT_FILENAME")
    if filenameFromXml == "":
        filenameFromXml = filename
    #print(" filenameFromXml: ", filenameFromXml)
    return filenameFromXml


def get_files(path):
     for (dirpath, _, filenames) in os.walk(path):
         for filename in filenames:
             yield os.path.join(dirpath, filename)

def xmlTreeFromFile(filename):
        xmlTree = objectify.parse(filename)
        return xmlTree

def xsdFromFile(filename):
    #xmlschema_doc = xmlTreeFromFile(filename)
    xmlschema_doc = etree.parse(filename)
    xsd = etree.XMLSchema(xmlschema_doc)
    return xsd

def validXML(xml_doc, xmlschema):
    return xmlschema.validate(xml_doc)

def copyFile(source, destination):
    try:
        destinationDir = os.path.dirname(destination)
        if not os.path.exists(destinationDir):
            os.mkdir(destinationDir)
        shutil.copy(source, destination)
    except:
        shutil.copy(source, destination+'1')

def moveFileToDir(source, destination):
    try:
        destinationDir = os.path.dirname(destination)
        if not os.path.exists(destinationDir):
            os.mkdir(destinationDir)
        shutil.move(source, destination)
    except:
        shutil.move(source, destination+'1')

def printXML(root):
    for element in root.iter():
        print("%s - %s" % (element.tag, element.text))


if __name__ == '__main__':
    main()