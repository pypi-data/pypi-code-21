import os
from validatexmls import xsdFromFile, get_files, xmlTreeFromFile, getFilenameFromXml, getMessageType, \
    validXML, copyFile, checkKnownIssues
import click


@click.command()
@click.option('--datadir', default='data', help='Root directory of the data.')
def main(datadir):
    xsd_filename = os.path.join(datadir, 'xsd/BC9.xsd')
    xsd_doc = xsdFromFile(xsd_filename)
    inputDir = os.path.join(datadir, 'input')
    outputDir = os.path.join(datadir, 'output')
    errorDir = os.path.join(datadir, 'error')
    list_files = get_files(inputDir)
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
                messageTypePath = os.path.join(errorDir, str(messageType))
                messageTypePath = os.path.join(messageTypePath, str(filenameFromXml))
                copyFile(filename, messageTypePath)
        else:
            countValid += 1
            # print('Valid xml', filename)
            messageTypePath = os.path.join(outputDir, str(messageType))
            messageTypePath = os.path.join(messageTypePath, str(filenameFromXml))
            #moveFileToDir(filename, messageTypePath)
            copyFile(filename, messageTypePath)

    print("Number of files valid: ", countValid, " Invalid: ", countInvalid, " KnownError:", countKnownError)


if __name__ == '__main__':
    main()