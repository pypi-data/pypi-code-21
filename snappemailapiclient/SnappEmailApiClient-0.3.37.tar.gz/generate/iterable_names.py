from xml.dom import minidom


def get_iterable_details():
    xml_doc = minidom.parse('SdkWebServiceDataContract.xsd')

    item_list = xml_doc.getElementsByTagName('complexType')

    all_elements = []
    names_list = []
    iter_details = {}  # iterable_name -> (iterable_attribute_name, iterable_attribute_base_type)
    for item in item_list:
        name = item.attributes['name'].value
        all_elements.append(name)

        if name.startswith('ListOf') and 'Page' not in name:
            names_list.append(name)
            sequences = item.getElementsByTagName('element')
            if len(sequences) == 1:
                sequence = sequences[0]
                iter_details[name] = (
                    sequence.attributes['name'].value,
                    sequence.attributes['type'].value.replace("bc:", "")
                )
            else:
                print(name, "More (or less) than 1 sequence", len(sequences))

    print(len(names_list), len(set(names_list)))
    print(names_list)
    print(iter_details)

    return iter_details


def save_iterable_details(path):
    iterable_details = get_iterable_details()
    fh = open(path + '../datacontract/iterable_object_mappings.py', "w")
    print("iterable_details = {", file=fh)
    iterable_keys = sorted(iterable_details)
    for iterable_object_name in iterable_keys:
        attr_name, attr_base_type = iterable_details[iterable_object_name]
        print("    '{}': ('{}', '{}'),".format(iterable_object_name, attr_name, attr_base_type), file=fh)
    print("}", file=fh)
    fh.close()


def save_resource_type_to_class_mappings(content_type_to_class, path):
    fh = open(path + '../datacontract/content_type_to_class_mapping.py', "w+")
    print("content_type_to_class_mapping = {", file=fh)
    content_type_to_class_keys = sorted(content_type_to_class)
    for k in content_type_to_class_keys:
        v = content_type_to_class[k]
        print("    '{}': '{}',".format(k, v), file=fh)
    print("}", file=fh)
