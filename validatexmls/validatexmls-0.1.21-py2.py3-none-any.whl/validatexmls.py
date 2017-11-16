import os
import shutil
from lxml import etree
from lxml import objectify
import click


@click.command()
@click.option('--xsd', default='/Tools/data/xsd/BC9.xsd', help='xsd schema.')
@click.option('--inputdir', default='/Tools/data/input', help='Root directory of the input data.')
@click.option('--outputdir', default='/Tools/data/output', help='Root directory of the output data.')
@click.option('--errordir', default='/Tools/data/error', help='Root directory of the error data.')
@click.option('--copy', default=False, help='Do not move, but copy the files from inputdir.')
def main(xsd, inputdir, outputdir, errordir, copy):
    xsd_doc = xsd_from_file(xsd)
    xml_doc = None
    list_files = get_files(inputdir)
    count_valid = 0
    count_invalid = 0
    count_known_error = 0

    for filename in list_files:
        # print(filename, )
        xml_exception = False
        filename_from_xml = None
        message_type = None

        try:
            xml_doc = xml_tree_from_file(filename)
            # print("valid_xml: ", valid_xml(xml_doc, xsd_doc))
            # print_xml(xml_doc)
            # print(xml_doc.getroot())
            DCS_MESSAGES = xml_doc.getroot()
            filename_from_xml = get_filename_from_xml(DCS_MESSAGES, filename)
            message_type = get_message_type(DCS_MESSAGES, filename_from_xml)
        except:
            # lxml.etree.XMLSyntaxError xe:
            xml_exception = True

        if filename_from_xml == None:
                filename_from_xml = os.path.basename(filename)

        if message_type == None:
            try:
                xml_doc = etree.parse(filename)
                message_type = etree.XPath('MESSAGE_TYPE')
            except:
                 xml_exception = True

        if message_type == None:
            try:
                xml_doc = open(filename).read()
                start = xml_doc.find('<MESSAGE_TYPE>')
                end = xml_doc.find('</MESSAGE_TYPE>')
                length = len('<MESSAGE_TYPE>')
                if start > -1 and end > -1 and length > 0:
                    message_type = xml_doc[start+length:end]
            except:
                 xml_exception = True

        if xml_exception or not valid_xml(xml_doc, xsd_doc):
            print('Invalid xml: ', filename)
            known_error = check_known_issues(filename)
            if known_error != "":
                count_known_error += 1
                known_error_path = os.path.join(errordir, str(known_error))
                known_error_path = os.path.join(known_error_path, str(filename_from_xml))
                if copy:
                    copy_file(filename, known_error_path)
                else:
                    move_file(filename, known_error_path)
            else:
                count_invalid += 1
                if xsd_doc.error_log != None and xsd_doc.error_log != "":
                    print(xsd_doc.error_log)
                message_type_path = os.path.join(errordir, str(message_type))
                message_type_path = os.path.join(message_type_path, str(filename_from_xml))
                if copy:
                    copy_file(filename, message_type_path)
                else:
                    move_file(filename, message_type_path)
        else:
            count_valid += 1
            # print('Valid xml', filename)
            message_type_path = os.path.join(outputdir, str(message_type))
            message_type_path = os.path.join(message_type_path, str(filename_from_xml))
            # move_file(filename, message_type_path)
            if copy:
                copy_file(filename, message_type_path)
            else:
                move_file(filename, message_type_path)

    print("Number of files valid: ", count_valid, " Invalid: ", count_invalid, " KnownError:", count_known_error)


def check_known_issues(filename):
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


def get_message_type(xml_obj, filename):
    message_type = xml_obj.find(".//MESSAGE_TYPE")
    if message_type == "":
        # print('DCS_MESSAGES.find(".//REF_XML_OUT_FILENAME")', DCS_MESSAGES.find(".//REF_XML_OUT_FILENAME"))
        fn = xml_obj.find(".//REF_XML_OUT_FILENAME")
        list = fn.split("_")
        if list.__len__() > 1:
            message_type = list[1]
    if message_type == "":
        list = filename.split("_")
        if list.__len__() > 1:
            message_type = list[1]
    # print(" Message type: ", message_type)
    return message_type

def get_vehicle(xml_obj, filename):
    vehicle = xml_obj.find(".//MOBILE_ID")
    if vehicle == "":
        fn = xml_obj.find(".//REF_XML_OUT_FILENAME")
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


def get_filename_from_xml(xmlobj, filename):
    filenameFromXml = xmlobj.find(".//REF_XML_OUT_FILENAME")
    if filenameFromXml == "":
        filenameFromXml = filename
    #print(" filenameFromXml: ", filenameFromXml)
    return filenameFromXml


def get_files(path):
     for (dirpath, _, filenames) in os.walk(path):
         for filename in filenames:
             yield os.path.join(dirpath, filename)


def xml_tree_from_file(filename):
        xmlTree = objectify.parse(filename)
        return xmlTree


def xsd_from_file(filename):
    #xmlschema_doc = xml_tree_from_file(filename)
    xmlschema_doc = etree.parse(filename)
    xsd = etree.XMLSchema(xmlschema_doc)
    return xsd


def valid_xml(xml_doc, xmlschema):
    return xmlschema.validate(xml_doc)


def copy_file(source, destination):
    try:
        destinationDir = os.path.dirname(destination)
        if not os.path.exists(destinationDir):
            os.mkdir(destinationDir)
        shutil.copy(source, destination)
        print('copied', source, 'to', destination)
    except:
        try:
            shutil.copy(source, destination+'1')
            print('copied', source, 'to', destination+'1')
        except:
            print('Cannot copy', source, 'to', destination + '1')


def move_file(source, destination):
    try:
        destinationDir = os.path.dirname(destination)
        if not os.path.exists(destinationDir):
            os.mkdir(destinationDir)
        shutil.move(source, destination)
        print('Moved', source, 'to', destination)
    except:
        try:
            shutil.move(source, destination+'1')
            print('Moved', source, 'to', destination + '1')
        except:
            print('Cannot move', source, 'to', destination+'1')


def print_xml(root):
    for element in root.iter():
        print("%s - %s" % (element.tag, element.text))


if __name__ == '__main__':
    main()