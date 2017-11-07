from xml.dom.minidom import Document, parseString

def dict_to_xml(valueDict, xmlns, topElementName):
    doc = Document()
    rootNode = doc.createElement(topElementName)
    rootNode.attributes["xmlns"] = xmlns
    doc.appendChild(rootNode)
    if valueDict:
        for k, v in valueDict.items():
            keyNode = doc.createElement(k)
            rootNode.appendChild(keyNode)
            keyNode.appendChild(doc.createTextNode(str(v)))
    else:
        nullNode = doc.createTextNode("")
        rootNode.appendChild(nullNode)
    return doc.toxml("utf-8")

def xml_to_nodes(tag_name, xml_data):
    dom = parseString(xml_data)
    nodelist = dom.getElementsByTagName(tag_name)
    return nodelist[0].childNodes

def xml_to_dic(tag_name, xml_data):
    result = {}
    for node in xml_to_nodes(tag_name, xml_data):
        if (node.nodeName != "#text" and node.childNodes != []):
            result[node.nodeName] = str(node.childNodes[0].nodeValue.strip())
    return result
